"""
Summarization Service.
Coordinates tokenization, length-aware generation, long-document chunking,
hierarchical consolidation, bounded refinement, and execution timing.
"""
import time
import re
import logging
from typing import Dict, Any, Optional, List
import torch

import config
from services.model_manager import ModelManager
from utils.text_utils import (
    clean_text,
    validate_input_text,
    compute_text_stats,
    calculate_compression_ratio,
    chunk_text_by_tokens
)

logger = logging.getLogger(__name__)

class SummarizationService:
    def __init__(self):
        self.model_manager = ModelManager()

    def generate_summary(
        self,
        text: str,
        model_key: str = "t5_small",
        length_mode: str = "medium",
        custom_min_tokens: Optional[int] = None,
        custom_max_tokens: Optional[int] = None,
        custom_num_beams: Optional[int] = None,
        custom_length_penalty: Optional[float] = None,
        target_word_count: Optional[int] = None,
        do_sample: bool = False,
        progress_callback: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Generates an abstractive summary from input text with length-aware configuration.
        Tracks model loading time separately from neural inference time.
        Handles single-pass or multi-stage chunked summarization for long documents.
        """
        # 1. Validation
        is_valid, err_msg = validate_input_text(text)
        if not is_valid:
            return {
                "success": False,
                "error": err_msg,
                "summary": "",
            }

        cleaned_text = clean_text(text)
        input_stats = compute_text_stats(cleaned_text)
        input_words = input_stats["word_count"]

        # 2. Model Configuration
        model_key = self.model_manager.resolve_model_key(model_key)
        if model_key not in config.SUPPORTED_MODELS:
            model_key = config.DEFAULT_MODEL_KEY
        model_info = config.SUPPORTED_MODELS[model_key]

        # 3. Resolve Length Profile & Presets
        length_preset = config.LENGTH_PROFILES.get(length_mode, config.LENGTH_PROFILES["medium"])
        target_w_min = length_preset.get("target_word_min", 120)
        target_w_max = length_preset.get("target_word_max", 180)

        # Allow user-provided target word count
        if target_word_count and target_word_count > 20:
            target_w_min = max(20, int(target_word_count * 0.8))
            target_w_max = max(target_w_min + 30, int(target_word_count * 1.2))

        # Check if source text is shorter than target summary
        warnings: List[str] = []
        source_is_brief = False
        if input_words < target_w_min:
            source_is_brief = True
            warnings.append(
                f"Source document has {input_words} words, which is smaller than the requested "
                f"preset target ({target_w_min}–{target_w_max} words). Output length is bounded "
                "by source content to prevent hallucination or artificial filler."
            )
        elif input_words < target_w_max:
            warnings.append(
                f"Source document has {input_words} words. Summary length is dynamically optimized "
                f"to maintain high compression ratio without hallucination."
            )

        # Token budget calculation
        min_tokens = custom_min_tokens if custom_min_tokens is not None else length_preset["min_tokens"]
        max_tokens = custom_max_tokens if custom_max_tokens is not None else length_preset["max_tokens"]
        num_beams = custom_num_beams if custom_num_beams is not None else length_preset.get("num_beams", 2)
        length_pen = custom_length_penalty if custom_length_penalty is not None else length_preset["length_penalty"]

        # Ensure max_tokens does not force model beyond source content
        max_allowed_words_from_source = max(25, int(input_words * 0.65))
        max_allowed_tokens_from_source = int(max_allowed_words_from_source * 1.35)

        if max_tokens > max_allowed_tokens_from_source and not custom_max_tokens:
            max_tokens = max(50, max_allowed_tokens_from_source)
            min_tokens = max(20, min(min_tokens, int(max_tokens * 0.6)))

        if min_tokens >= max_tokens:
            min_tokens = max(15, int(max_tokens * 0.6))
        num_beams = max(1, min(8, num_beams))

        start_time = time.time()
        model_load_time = 0.0

        try:
            if progress_callback:
                progress_callback(10, f"Initializing {model_info['display_name']}...")

            # 4. Load Model and Tokenizer (measures separate load time)
            tokenizer, model, model_load_time = self.model_manager.load_model_with_timing(model_key)
            device = self.model_manager.device

            infer_start_time = time.time()

            max_input_tokens = model_info["max_input_tokens"]
            safe_chunk_limit = max_input_tokens - config.CHUNK_SETTINGS["chunk_safety_margin"]

            full_tokens = tokenizer.encode(cleaned_text, add_special_tokens=False)
            token_count = len(full_tokens)

            is_chunked = False
            chunks_processed = 1

            # 5. Single Pass vs Hierarchical Execution
            if token_count <= safe_chunk_limit:
                if progress_callback:
                    progress_callback(35, "Running neural sequence generation...")

                # Single pass summarization - execute once without duplicate retry passes
                raw_summary = self._summarize_chunk(
                    chunk_text=cleaned_text,
                    tokenizer=tokenizer,
                    model=model,
                    device=device,
                    prefix=model_info.get("default_prefix", ""),
                    min_tokens=min_tokens,
                    max_tokens=max_tokens,
                    num_beams=num_beams,
                    length_penalty=length_pen,
                    do_sample=do_sample,
                )
                summary = self._ensure_sentence_completion(raw_summary)

            else:
                # Hierarchical chunked summarization for long documents
                is_chunked = True
                chunks = chunk_text_by_tokens(
                    text=cleaned_text,
                    tokenizer=tokenizer,
                    max_chunk_tokens=safe_chunk_limit,
                    overlap_tokens=config.CHUNK_SETTINGS.get("overlap_tokens", 30)
                )
                chunks_processed = len(chunks)
                logger.info(f"Document has {token_count} tokens. Splitting into {chunks_processed} hierarchical chunks.")

                # Safe chunk ceiling to prevent CPU timeout on massive documents
                max_chunks = config.CHUNK_SETTINGS.get("max_chunks_limit", 5)
                if len(chunks) > max_chunks:
                    step = len(chunks) / max_chunks
                    chunks = [chunks[int(i * step)] for i in range(max_chunks)]
                    warnings.append(
                        f"Document has {chunks_processed} segments. Subsampled to {max_chunks} salient sections "
                        "to ensure complete synthesis within real-time latency budgets."
                    )
                    chunks_processed = len(chunks)

                if progress_callback:
                    progress_callback(25, f"Split document into {len(chunks)} token-bounded sections...")

                # Allocate chunk budget proportionally based on preset
                chunk_budget = length_preset.get("chunk_intermediate_tokens", 100)
                chunk_min = max(20, int(chunk_budget * 0.5))
                chunk_max = max(chunk_min + 20, int(chunk_budget * 1.2))

                intermediate_summaries: List[str] = []
                for idx, chunk in enumerate(chunks):
                    if progress_callback:
                        pct = int(30 + 45 * (idx + 1) / len(chunks))
                        progress_callback(pct, f"Summarizing section {idx + 1} of {len(chunks)}...")

                    chunk_sum = self._summarize_chunk(
                        chunk_text=chunk,
                        tokenizer=tokenizer,
                        model=model,
                        device=device,
                        prefix=model_info.get("default_prefix", ""),
                        min_tokens=chunk_min,
                        max_tokens=chunk_max,
                        num_beams=2,  # 2 beams on intermediate chunks for fast turnaround
                        length_penalty=1.2,
                        do_sample=False,
                        max_input_tokens=safe_chunk_limit
                    )
                    clean_chunk_sum = self._ensure_sentence_completion(chunk_sum)
                    if clean_chunk_sum:
                        intermediate_summaries.append(clean_chunk_sum)

                if progress_callback:
                    progress_callback(80, "Consolidating section summaries...")

                combined_intermediate = " ".join(intermediate_summaries)
                combined_tokens = len(tokenizer.encode(combined_intermediate, add_special_tokens=False))

                if length_mode in ["long", "detailed"] and chunks_processed > 1:
                    # Synthesize an overarching executive overview
                    exec_overview = self._summarize_chunk(
                        chunk_text=combined_intermediate[:safe_chunk_limit],
                        tokenizer=tokenizer,
                        model=model,
                        device=device,
                        prefix=model_info.get("default_prefix", ""),
                        min_tokens=40,
                        max_tokens=100,
                        num_beams=num_beams,
                        length_penalty=1.2,
                        do_sample=False,
                    )
                    exec_clean = self._ensure_sentence_completion(exec_overview)
                    section_paragraphs = "\n\n".join(intermediate_summaries)
                    summary = f"**Executive Overview:**\n{exec_clean}\n\n**Detailed Section Synthesis:**\n{section_paragraphs}"
                else:
                    # Final synthesis pass
                    final_raw = self._summarize_chunk(
                        chunk_text=combined_intermediate[:safe_chunk_limit],
                        tokenizer=tokenizer,
                        model=model,
                        device=device,
                        prefix=model_info.get("default_prefix", ""),
                        min_tokens=min_tokens,
                        max_tokens=max_tokens,
                        num_beams=num_beams,
                        length_penalty=length_pen,
                        do_sample=do_sample,
                    )
                    summary = self._ensure_sentence_completion(final_raw)

            inference_time = round(time.time() - infer_start_time, 2)
            duration = round(time.time() - start_time, 2)
            summary_stats = compute_text_stats(summary)
            compression_ratio = calculate_compression_ratio(
                original_words=input_stats["word_count"],
                summary_words=summary_stats["word_count"]
            )

            # Check output range vs targets
            if not source_is_brief:
                actual_words = summary_stats["word_count"]
                if actual_words < target_w_min:
                    warnings.append(
                        f"Generated summary ({actual_words} words) is slightly below target range "
                        f"({target_w_min}–{target_w_max} words) due to model inductive brevity bias."
                    )

            if progress_callback:
                progress_callback(100, "Summary generation completed.")

            return {
                "success": True,
                "summary": summary,
                "model_key": model_key,
                "model_name": model_info["display_name"],
                "length_mode": length_mode,
                "target_word_range": f"{target_w_min}–{target_w_max} words",
                "processing_time": duration,
                "model_load_time": model_load_time,
                "inference_time": inference_time,
                "input_word_count": input_stats["word_count"],
                "input_char_count": input_stats["char_count"],
                "input_token_count": token_count,
                "summary_word_count": summary_stats["word_count"],
                "summary_char_count": summary_stats["char_count"],
                "compression_ratio": compression_ratio,
                "is_chunked": is_chunked,
                "chunks_count": chunks_processed,
                "device": self.model_manager.device_name,
                "warnings": warnings,
            }

        except Exception as e:
            logger.error(f"Summarization error: {e}", exc_info=True)
            duration = round(time.time() - start_time, 2)
            return {
                "success": False,
                "error": f"Inference failed: {str(e)}",
                "summary": "",
                "processing_time": duration,
                "model_load_time": model_load_time,
                "inference_time": 0.0,
                "warnings": [str(e)],
            }

    def _summarize_chunk(
        self,
        chunk_text: str,
        tokenizer,
        model,
        device,
        prefix: str,
        min_tokens: int,
        max_tokens: int,
        num_beams: int,
        length_penalty: float,
        do_sample: bool,
        max_input_tokens: Optional[int] = None,
    ) -> str:
        """Runs model generation on a single token-bounded chunk of text with strict length parameters."""
        prepared_input = f"{prefix}{chunk_text}".strip()
        max_pos = max_input_tokens or getattr(model.config, "max_position_embeddings", getattr(model.config, "n_positions", 512))
        inputs = tokenizer(
            prepared_input,
            max_length=max_pos,
            truncation=True,
            return_tensors="pt"
        ).to(device)

        gen_kwargs = {
            "max_new_tokens": max_tokens,
            "min_new_tokens": min_tokens,
            "num_beams": num_beams,
            "no_repeat_ngram_size": 3,
            "early_stopping": True,
            "do_sample": do_sample,
            "length_penalty": length_penalty,
        }

        with torch.inference_mode():
            output_ids = model.generate(
                inputs["input_ids"],
                attention_mask=inputs.get("attention_mask", None),
                **gen_kwargs
            )

        summary = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        return clean_text(summary)

    def _ensure_sentence_completion(self, text: str) -> str:
        """Trims dangling trailing fragments so summaries end gracefully on sentence boundaries."""
        if not text:
            return ""
        text = text.strip()
        # If text ends with punctuation, return
        if text[-1] in [".", "!", "?", '"', "”"]:
            return text
        
        # Look for last sentence boundary
        match = re.search(r"^(.*[.!?])\s+[A-Za-z0-9]", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Fallback: find last period or punctuation
        last_punct = max(text.rfind("."), text.rfind("!"), text.rfind("?"))
        if last_punct > int(len(text) * 0.5):
            return text[: last_punct + 1].strip()
        return text
