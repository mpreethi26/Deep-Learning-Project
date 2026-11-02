"""
Text Processing Utilities for Text Summarization.
Provides input validation, text normalization, statistics, and text chunking.
"""
import re
from typing import List, Tuple, Dict, Any

def clean_text(text: str) -> str:
    """
    Normalizes whitespace, strips unwanted control characters,
    and preserves standard punctuation and paragraphs.
    """
    if not text:
        return ""
    # Normalize unicode spaces and tabs
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Replace non-breaking spaces
    text = text.replace("\xa0", " ")
    # Replace multiple spaces with a single space per line
    text = re.sub(r"[ \t]+", " ", text)
    # Remove excessive blank lines (more than 2 consecutive)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def validate_input_text(text: str, min_words: int = 5) -> Tuple[bool, str]:
    """
    Validates input text for summarization.
    Returns (is_valid, error_message).
    """
    if not text or not text.strip():
        return False, "Input text is empty. Please enter or paste some text."
    
    cleaned = clean_text(text)
    words = cleaned.split()
    if len(words) < min_words:
        return False, f"Input text is too short ({len(words)} words). Please provide at least {min_words} words."
    
    return True, ""

def compute_text_stats(text: str) -> Dict[str, Any]:
    """
    Computes character count, word count, line count, and sentence count.
    """
    cleaned = clean_text(text)
    if not cleaned:
        return {
            "char_count": 0,
            "word_count": 0,
            "sentence_count": 0,
            "line_count": 0,
        }
    
    words = cleaned.split()
    lines = [l for l in cleaned.split("\n") if l.strip()]
    # Approximate sentence splitting
    sentences = re.split(r"[.!?]+(?:\s+|$)", cleaned)
    sentences = [s.strip() for s in sentences if s.strip()]

    return {
        "char_count": len(cleaned),
        "word_count": len(words),
        "sentence_count": len(sentences),
        "line_count": len(lines),
    }

def calculate_compression_ratio(original_words: int, summary_words: int) -> float:
    """
    Calculates compression percentage: (1 - summary_words / original_words) * 100.
    Returns a clamped float between 0.0 and 100.0.
    """
    if original_words <= 0:
        return 0.0
    if summary_words >= original_words:
        return 0.0
    ratio = (1.0 - (summary_words / original_words)) * 100.0
    return round(max(0.0, min(100.0, ratio)), 2)

def chunk_text_by_tokens(
    text: str,
    tokenizer,
    max_chunk_tokens: int = 900,
    overlap_tokens: int = 50
) -> List[str]:
    """
    Splits long text into coherent token-bounded chunks respecting model token limits.
    Uses sentence boundaries where possible with token-level fallback and sliding overlap.
    """
    cleaned = clean_text(text)
    if not cleaned:
        return []

    # Encode complete text to tokens
    full_token_ids = tokenizer.encode(cleaned, add_special_tokens=False)
    if len(full_token_ids) <= max_chunk_tokens:
        return [cleaned]

    # Split into paragraphs and sentences first to avoid cutting words
    paragraphs = [p.strip() for p in cleaned.split("\n\n") if p.strip()]
    sentences: List[str] = []
    for p in paragraphs:
        # Split sentences preserving punctuation
        s_list = re.split(r"(?<=[.!?])\s+", p)
        for s in s_list:
            if s.strip():
                sentences.append(s.strip())

    chunks: List[str] = []
    current_chunk_sentences: List[str] = []
    current_chunk_token_count = 0

    step_size = max(10, max_chunk_tokens - overlap_tokens)

    for sentence in sentences:
        s_tokens = len(tokenizer.encode(sentence, add_special_tokens=False))
        # If single sentence is bigger than max_chunk_tokens, slice it by tokens
        if s_tokens > max_chunk_tokens:
            if current_chunk_sentences:
                chunks.append(" ".join(current_chunk_sentences))
                current_chunk_sentences = []
                current_chunk_token_count = 0

            # Sub-chunk this gigantic sentence by raw token window
            sentence_token_ids = tokenizer.encode(sentence, add_special_tokens=False)
            for i in range(0, len(sentence_token_ids), step_size):
                sub_ids = sentence_token_ids[i : i + max_chunk_tokens]
                sub_text = tokenizer.decode(sub_ids, skip_special_tokens=True)
                if sub_text.strip():
                    chunks.append(sub_text.strip())
            continue

        if current_chunk_token_count + s_tokens <= max_chunk_tokens:
            current_chunk_sentences.append(sentence)
            current_chunk_token_count += s_tokens
        else:
            if current_chunk_sentences:
                chunks.append(" ".join(current_chunk_sentences))
            
            # Start next chunk with slight sentence overlap if feasible
            if overlap_tokens > 0 and len(current_chunk_sentences) > 1:
                # Include last sentence as overlap
                overlap_sentence = current_chunk_sentences[-1]
                overlap_len = len(tokenizer.encode(overlap_sentence, add_special_tokens=False))
                if overlap_len < max_chunk_tokens // 2:
                    current_chunk_sentences = [overlap_sentence, sentence]
                    current_chunk_token_count = overlap_len + s_tokens
                else:
                    current_chunk_sentences = [sentence]
                    current_chunk_token_count = s_tokens
            else:
                current_chunk_sentences = [sentence]
                current_chunk_token_count = s_tokens

    if current_chunk_sentences:
        chunks.append(" ".join(current_chunk_sentences))

    # If sentence splitting didn't produce chunks, fallback to raw token sliding window
    if not chunks:
        for i in range(0, len(full_token_ids), step_size):
            window = full_token_ids[i : i + max_chunk_tokens]
            decoded = tokenizer.decode(window, skip_special_tokens=True)
            if decoded.strip():
                chunks.append(decoded.strip())

    return chunks
