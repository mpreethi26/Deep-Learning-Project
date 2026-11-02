# Experimental Protocol & Evaluation Guidelines

## Objective
To rigorously evaluate abstractive summarization performance across benchmark datasets and user-supplied documents using automated metrics and latency profiling.

## Protocol Steps
1. **Sample Selection**: Use a stratified subset of documents (e.g., 10-50 examples) from news (CNN/DailyMail) or academic text.
2. **Inference Execution**:
   - Model: `facebook/bart-large-cnn` vs `google/flan-t5-base`
   - Beams: 4
   - Length Penalty: 1.5
   - Min/Max Tokens: 60 / 140
3. **Metrics Calculation**:
   - ROUGE-1, ROUGE-2, ROUGE-L against human ground truth.
   - Processing latency per document (seconds).
   - Compression ratio: $(1 - \text{Summary Words} / \text{Input Words}) \times 100$.
4. **Export**: Log all predictions, reference summaries, and scores into CSV format for statistical review.
