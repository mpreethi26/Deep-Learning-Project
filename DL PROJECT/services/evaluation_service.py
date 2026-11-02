"""
Evaluation Service.
Computes ROUGE-1, ROUGE-2, and ROUGE-L metrics against reference ground truths.
Supports optional BERTScore semantic similarity.
"""
from typing import Dict, Any, Optional
from utils.metrics_utils import compute_rouge_scores, compute_bertscore
from utils.text_utils import compute_text_stats, calculate_compression_ratio

class EvaluationService:
    """Service to evaluate generated summaries with standard NLP metrics."""

    @staticmethod
    def evaluate(
        generated_summary: str,
        reference_summary: str,
        original_text: Optional[str] = None,
        include_bertscore: bool = False
    ) -> Dict[str, Any]:
        """
        Evaluates a generated summary against a reference summary.
        Calculates ROUGE-1, ROUGE-2, ROUGE-L, and optional BERTScore.
        """
        if not reference_summary or not reference_summary.strip():
            return {
                "success": False,
                "error": "A reference (ground-truth) summary is required to compute reference-based NLP metrics."
            }

        if not generated_summary or not generated_summary.strip():
            return {
                "success": False,
                "error": "Generated summary is empty."
            }

        rouge_res = compute_rouge_scores(generated_summary, reference_summary)
        if not rouge_res.get("success", False):
            return rouge_res

        gen_stats = compute_text_stats(generated_summary)
        ref_stats = compute_text_stats(reference_summary)

        result: Dict[str, Any] = {
            "success": True,
            "metrics": rouge_res["metrics"],
            "summary_words": gen_stats["word_count"],
            "reference_words": ref_stats["word_count"],
        }

        if original_text and original_text.strip():
            orig_stats = compute_text_stats(original_text)
            result["original_words"] = orig_stats["word_count"]
            result["compression_ratio"] = calculate_compression_ratio(
                orig_stats["word_count"], gen_stats["word_count"]
            )

        if include_bertscore:
            bert_res = compute_bertscore(generated_summary, reference_summary)
            result["bertscore"] = bert_res

        return result
