# Abstractive Text Summarization Methodology

## 1. Introduction & Domain Formulation
Text summarization is the task of condensing an elongated natural language document into an informative, coherent, and fluent synopsis while retaining critical semantic propositions.

In Natural Language Processing (NLP), summarization is classified into two distinct paradigms:
1. **Extractive Summarization:** Selects salient subsets of sentences directly from the raw document without lexical alterations. Although grammatically guaranteed, extractive summaries exhibit fragmented transitions and lack discursive synthesis.
2. **Abstractive Summarization:** Comprehends semantic representations of the input text, reformulating and generating entirely novel sentences, paraphrases, and abstractions. This mirrors human cognitive synthesis.

## 2. Transformer Architectural Foundations
The application utilizes sequence-to-sequence (Seq2Seq) Transformer architectures composed of a bidirectional encoder and an autoregressive decoder.

### Scaled Dot-Product Attention
Given input queries $Q \in \mathbb{R}^{n \times d_k}$, keys $K \in \mathbb{R}^{m \times d_k}$, and values $V \in \mathbb{R}^{m \times d_v}$:
$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

### Multi-Head Attention
Instead of performing a single attention function, multi-head attention projects queries, keys, and values $h$ times with distinct learned linear projections:
$$\text{MultiHead}(Q, K, V) = \text{Concat}(\text{head}_1, \dots, \text{head}_h)W^O$$
$$\text{where } \text{head}_i = \text{Attention}(QW_i^Q, KW_i^K, VW_i^V)$$

## 3. BART (Bidirectional and Auto-Regressive Transformers)
BART (`facebook/bart-large-cnn`) is a sequence-to-sequence model combining a bidirectional encoder (BERT-style) with a left-to-right autoregressive decoder (GPT-style).

### Denoising Pretraining Objective
BART is pretrained as a denoising autoencoder. Document text is corrupted with 5 stochastic noise transformations:
1. **Token Masking:** Random tokens sampled and replaced with `[MASK]`.
2. **Token Deletion:** Random tokens deleted from sequence.
3. **Text Infilling:** Single spans of text replaced with single `[MASK]` tokens.
4. **Sentence Permutation:** Document sentences shuffled randomly.
5. **Document Rotation:** A random token chosen to rotate the sequence.

The model is trained via cross-entropy loss to reconstruct the original clean text from the corrupted sequence:
$$\mathcal{L}_{\text{BART}} = -\sum_{t=1}^T \log P(x_t \mid x_{<t}, \tilde{x})$$
where $\tilde{x}$ denotes the corrupted input and $x$ denotes the ground truth sequence.

## 4. Diagnosis and Resolution of the "Short Summary" Bottleneck

### The Root Cause:
1. **News Corpus Inductive Brevity Bias:** `facebook/bart-large-cnn` is fine-tuned on the CNN/DailyMail dataset, where human reference highlights average only 3–4 sentences (50–80 tokens). Autoregressive decoding consequently assigns high probability to the EOS token `</s>` after just ~60 tokens.
2. **Premature Beam Termination:** Standard generation with `early_stopping=True` halts beam search as soon as completed hypotheses emit EOS, cutting off long-form synthesis.
3. **Flawed Token Budgeting:** Token count was erroneously treated as word count (1 word $\approx$ 1.35 tokens). A token limit of 140 yielded merely 90 words.
4. **Destructive Hierarchical Compression:** Naive multi-stage chunking over-compressed each chunk to $\approx 40$ tokens, and then re-compressed the concatenation back to 60 words.

### Pipeline Remediation:
1. **Length-Calibrated Generation Profiles:**
   - **Short:** Target 80–120 words (`min_new_tokens: 95`, `max_new_tokens: 175`, `length_penalty: 1.2`)
   - **Medium:** Target 150–250 words (`min_new_tokens: 180`, `max_new_tokens: 320`, `length_penalty: 1.8`)
   - **Long:** Target 300–500 words (`min_new_tokens: 320`, `max_new_tokens: 650`, `length_penalty: 2.2`)
   - **Detailed:** Target 500–800 words (`min_new_tokens: 520`, `max_new_tokens: 980`, `length_penalty: 2.5`)
2. **Section-Wise Hierarchical Synthesis:** For multi-chunk long documents, chunk summaries are allocated substantial token budgets (110–220 tokens per chunk) and synthesized into an Executive Overview + Detailed Section Syntheses, preventing destructive double-compression.
3. **Bounded Refinement & Sentence Trimming:** Guarantees summaries terminate gracefully on complete sentence boundaries without mid-word or mid-phrase truncation. Prevents hallucinations on brief source inputs by bounding generation proportionally.

## 5. Evaluation Metrics Formulation

### ROUGE-N (N-gram Overlap)
$$\text{ROUGE-N} = \frac{\sum_{S \in \text{References}} \sum_{\text{gram}_n \in S} \text{Count}_{\text{match}}(\text{gram}_n)}{\sum_{S \in \text{References}} \sum_{\text{gram}_n \in S} \text{Count}(\text{gram}_n)}$$

### ROUGE-L (Longest Common Subsequence)
$$\text{ROUGE-L}_{\text{recall}} = \frac{\text{LCS}(\text{Reference}, \text{Candidate})}{m}, \quad \text{ROUGE-L}_{\text{precision}} = \frac{\text{LCS}(\text{Reference}, \text{Candidate})}{n}$$
$$F_{\text{LCS}} = \frac{(1 + \beta^2) R_{\text{LCS}} P_{\text{LCS}}}{R_{\text{LCS}} + \beta^2 P_{\text{LCS}}}$$
where $m, n$ are the lengths of reference and candidate sequences, and $\text{LCS}$ is the length of the longest common subsequence.

