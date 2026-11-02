"""
Evaluation Metrics Utilities for Summarization.
Computes genuine ROUGE-1, ROUGE-2, and ROUGE-L scores using the rouge-score library.
"""
from typing import Dict, Any, Optional

try:
    from rouge_score import rouge_scorer
    ROUGE_AVAILABLE = True
except ImportError:
    ROUGE_AVAILABLE = False


def compute_rouge_scores(
    prediction: str,
    reference: str,
    use_stemmer: bool = True
) -> Dict[str, Any]:
    """
    Computes ROUGE-1, ROUGE-2, and ROUGE-L scores (Precision, Recall, F-measure)
    between a generated summary and a reference summary.
    """
    if not ROUGE_AVAILABLE:
        return {
            "success": False,
            "error": "The 'rouge-score' package is not installed."
        }

    if not prediction or not prediction.strip():
        return {
            "success": False,
            "error": "Generated summary is empty."
        }

    if not reference or not reference.strip():
        return {
            "success": False,
            "error": "Reference summary is empty. ROUGE requires a reference ground truth."
        }

    scorer = rouge_scorer.RougeScorer(
        ["rouge1", "rouge2", "rougeL"],
        use_stemmer=use_stemmer
    )
    scores = scorer.score(reference.strip(), prediction.strip())

    return {
        "success": True,
        "metrics": {
            "rouge1": {
                "precision": round(scores["rouge1"].precision, 4),
                "recall": round(scores["rouge1"].recall, 4),
                "fmeasure": round(scores["rouge1"].fmeasure, 4),
            },
            "rouge2": {
                "precision": round(scores["rouge2"].precision, 4),
                "recall": round(scores["rouge2"].recall, 4),
                "fmeasure": round(scores["rouge2"].fmeasure, 4),
            },
            "rougeL": {
                "precision": round(scores["rougeL"].precision, 4),
                "recall": round(scores["rougeL"].recall, 4),
                "fmeasure": round(scores["rougeL"].fmeasure, 4),
            }
        }
    }


def compute_bertscore(
    prediction: str,
    reference: str
) -> Dict[str, Any]:
    """
    Optional semantic similarity metric using BERTScore.
    Provides clear status and returns error or unavailable note if bert-score is not configured.
    """
    try:
        import bert_score
        # Compute BERTScore
        p, r, f1 = bert_score.score([prediction], [reference], lang="en", verbose=False)
        return {
            "success": True,
            "precision": round(float(p.mean().item()), 4),
            "recall": round(float(r.mean().item()), 4),
            "f1": round(float(f1.mean().item()), 4),
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"BERTScore is optional and currently unavailable: {str(e)}"
        }
