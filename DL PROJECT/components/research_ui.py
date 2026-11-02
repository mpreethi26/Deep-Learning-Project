"""
Research & Methodology Component.
Contains comprehensive academic explanations of NLP, Extractive vs Abstractive Summarization,
Transformer Architecture, Attention Mechanisms, BART vs T5, ROUGE Metrics, and IEEE Xplore Base Paper Documentation.
"""
import streamlit as st
import config

def render_research_methodology():
    """Renders the comprehensive research & methodology page."""
    st.markdown("## 🔬 Research & Methodology")
    st.caption("Academic overview of Abstractive Text Summarization, Sequence-to-Sequence Transformers, and Evaluation.")

    tab1, tab2, tab3, tab4 = st.tabs([
        "🧠 NLP & Summarization",
        "⚡ Transformer & BART",
        "🎯 Evaluation Metrics",
        "📚 IEEE Base Paper Guide"
    ])

    with tab1:
        st.markdown(
            """
            ### 1. Natural Language Processing (NLP) Overview
            Natural Language Processing (NLP) is a core subfield of Artificial Intelligence and Computational Linguistics dedicated to giving computers the ability to understand, interpret, and generate human language.

            #### Extractive vs. Abstractive Summarization
            Text summarization methods fall into two fundamentally distinct paradigms:

            | Feature | Extractive Summarization | Abstractive Summarization (Our Project) |
            | :--- | :--- | :--- |
            | **Mechanism** | Scores and selects verbatim sentences from source text. | Synthesizes ideas to generate novel phrasing and vocabulary. |
            | **Methodology** | TextRank, TF-IDF, clustering, Graph ranking. | Sequence-to-Sequence Deep Transformers (BART, T5). |
            | **Fluency** | Can suffer from abrupt sentence transitions. | Produces fluent, coherent, human-like summaries. |
            | **Paraphrasing** | Impossible (strictly concatenates original lines). | Capable of genuine synthesis, compression, and paraphrasing. |
            | **Challenge** | Lacks deep semantic abstraction. | Requires extensive pretraining; potential risk of hallucinations. |

            #### Preprocessing Pipeline
            1. **Whitespace & Control Character Normalization**: Strips invalid bytes, replaces excessive linebreaks.
            2. **Subword Tokenization (BPE)**: Breaks text into subword units, solving the out-of-vocabulary (OOV) problem.
            3. **Sliding Window Chunking**: For inputs exceeding 1,024 tokens, coherent paragraph boundaries are preserved with token overlap.
            """
        )

    with tab2:
        st.markdown(
            """
            ### 2. Transformer Architecture & BART
            Published by Vaswani et al. in *“Attention Is All You Need”* (2017), the Transformer eliminates recurrent connections in favor of self-attention.

            #### Self-Attention Formulation
            The scaled dot-product attention computes compatibility between Query ($Q$), Key ($K$), and Value ($V$) matrices:

            $$\\text{Attention}(Q, K, V) = \\text{softmax}\\left(\\frac{Q K^T}{\\sqrt{d_k}}\\right) V$$

            #### The BART Architecture (`facebook/bart-large-cnn`)
            - **Author / Origin**: Lewis et al. (Facebook AI Research, 2019).
            - **Architecture**: Standard sequence-to-sequence bidirectional encoder paired with a left-to-right autoregressive decoder.
            - **Pretraining Objective**: Pretrained as a denoising autoencoder. Arbitrary noise (token masking, token deletion, document rotation, text infilling) is applied to text, and the model is trained to reconstruct the original document.
            - **Fine-tuning**: Fine-tuned on the CNN/DailyMail dataset (over 300,000 news stories) specifically for multi-sentence abstractive summarization.
            - **Context Window**: 1,024 positional embeddings.
            """
        )

    with tab3:
        st.markdown(
            """
            ### 3. Quantitative Evaluation Framework
            Objective evaluation of abstractive summaries requires comparing candidate outputs with ground-truth reference texts.

            #### ROUGE (Recall-Oriented Understudy for Gisting Evaluation)
            - **ROUGE-1**: Evaluates unigram (single word) overlap. High ROUGE-1 indicates good topical content retention.
            - **ROUGE-2**: Evaluates bigram (word pair) overlap. Measures phrase structure and local grammatical coherence.
            - **ROUGE-L**: Measures the Longest Common Subsequence (LCS) between candidate and reference, capturing sentence-level structure without requiring consecutive strings.

            #### Compression Ratio
            $$\\text{Compression Ratio (\\%)} = \\left(1 - \\frac{\\text{Summary Words}}{\\text{Original Words}}\\right) \\times 100$$
            """
        )

    with tab4:
        st.markdown(
            f"""
            ### 4. IEEE Xplore Base Paper Documentation Guide
            - **Faculty-Specified Research Keywords**: `“{config.RESEARCH_KEYWORDS}”`
            - **Required Publication Source**: **{config.REQUIRED_PUBLISHER}**

            #### Recommended Relevant IEEE Base Papers
            To document your academic base paper, search IEEE Xplore using the designated keywords. Suitable peer-reviewed papers include:

            1. **"Abstractive Text Summarization Using Deep Learning: A Survey"**
               - *Venue*: IEEE Access
               - *Keywords*: Abstractive summarization, Transformer, sequence-to-sequence, ROUGE.
            2. **"Abstractive Text Summarization Based on Sequence-to-Sequence Transformer Model"**
               - *Venue*: IEEE International Conference on Natural Language Processing
               - *Keywords*: BART, attention mechanism, news summarization.

            #### Academic Documentation Checklist
            - [x] Peer-reviewed publisher: IEEE Xplore
            - [x] Pretrained Transformer model: Facebook BART-Large-CNN
            - [x] Evaluation metrics: ROUGE-1, ROUGE-2, ROUGE-L
            - [x] Input formats: Raw text and multi-page PDFs
            - [x] Open-source and reproducible without paid API keys
            """
        )

def render_about_project():
    """Renders the About Project page."""
    st.markdown("## ℹ️ About the Project")
    st.markdown(
        f"""
        ### Abstractive Text Summarization Using Transformer Models
        - **Team Lead / Researcher**: **{config.TEAM_LEAD}**
        - **Application Type**: NLP + Deep Learning + Transformer Web Application
        - **Primary Model**: `facebook/bart-large-cnn` (Hugging Face Transformers)
        - **Secondary / Comparison Model**: `google/flan-t5-base`
        - **Frontend Framework**: Streamlit
        - **Target Research Index**: IEEE Xplore

        #### Project Summary
        This application implements an end-to-end abstractive summarization system designed for academic documents, research articles, news stories, and PDF reports.
        Unlike traditional extractive techniques that merely clip existing sentences, this system utilizes deep Transformer sequence-to-sequence models to synthesize novel, concise, and fluent natural-language abstracts.
        """
    )
