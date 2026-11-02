import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
"""
Experimental Evaluation Script.
Evaluates summarization models on a local CSV dataset or synthetic benchmark sample.
Calculates ROUGE-1, ROUGE-2, ROUGE-L, measures latency, and exports CSV results.
"""
import time
import argparse
import pandas as pd
from services.summarization_service import SummarizationService
from services.evaluation_service import EvaluationService

SAMPLE_BENCHMARK = [
    {
        "id": 1,
        "text": "The James Webb Space Telescope (JWST) is a space telescope designed primarily to conduct infrared astronomy. As the largest optical telescope in space, its high resolution and sensitivity allow it to view objects too old, distant, or faint for the Hubble Space Telescope. This enables investigations across many fields of astronomy and cosmology, such as observation of the first stars and the formation of the first galaxies.",
        "reference": "The James Webb Space Telescope is the largest infrared telescope in space, capable of observing ancient and distant stars and galaxies."
    },
    {
        "id": 2,
        "text": "Machine learning algorithms build a model based on sample data, known as training data, in order to make predictions or decisions without being explicitly programmed to do so. Machine learning algorithms are used in a wide variety of applications, such as in medicine, email filtering, speech recognition, and computer vision, where it is difficult or unfeasible to develop conventional algorithms.",
        "reference": "Machine learning enables computers to learn from sample data and make predictions across fields like medicine and computer vision without explicit programming."
    }
]

def run_experiment(model_key: str = "bart", output_csv: str = "experiment_results.csv"):
    print(f"Starting experiment on benchmark using model: {model_key}...")
    sum_service = SummarizationService()
    eval_service = EvaluationService()

    results = []
    for item in SAMPLE_BENCHMARK:
        print(f"Summarizing item {item['id']}...")
        start = time.time()
        sum_res = sum_service.generate_summary(item["text"], model_key=model_key, length_mode="medium")
        latency = round(time.time() - start, 2)

        if not sum_res.get("success", False):
            print(f"Failed item {item['id']}: {sum_res.get('error')}")
            continue

        eval_res = eval_service.evaluate(sum_res["summary"], item["reference"])
        metrics = eval_res.get("metrics", {})

        results.append({
            "id": item["id"],
            "model": model_key,
            "generated_summary": sum_res["summary"],
            "reference_summary": item["reference"],
            "rouge1_f1": metrics.get("rouge1", {}).get("fmeasure", 0.0),
            "rouge2_f1": metrics.get("rouge2", {}).get("fmeasure", 0.0),
            "rougeL_f1": metrics.get("rougeL", {}).get("fmeasure", 0.0),
            "latency_sec": latency,
            "compression_ratio": sum_res["compression_ratio"],
        })

    df = pd.DataFrame(results)
    df.to_csv(output_csv, index=False)
    print(f"Experiment completed. Results saved to {output_csv}.")
    print("\nAggregate Averages:")
    print(df[["rouge1_f1", "rouge2_f1", "rougeL_f1", "latency_sec", "compression_ratio"]].mean())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Summarization Benchmark Experiment")
    parser.add_argument("--model", type=str, default="bart", help="Model key (bart or t5)")
    parser.add_argument("--output", type=str, default="experiment_results.csv", help="Output CSV path")
    args = parser.parse_args()
    run_experiment(model_key=args.model, output_csv=args.output)
