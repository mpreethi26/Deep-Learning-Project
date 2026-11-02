"""
Summarize Text Component.
Provides the primary abstractive summarization workspace for pasted/typed text,
including live token estimation, length modes, advanced beam parameters,
and multi-format download capabilities.
"""
import streamlit as st
import config
from services.summarization_service import SummarizationService
from services.history_service import HistoryService
from services.model_manager import ModelManager
from utils.text_utils import compute_text_stats
from utils.download_utils import format_summary_txt, format_summary_markdown, format_summary_json

SAMPLE_TEXTS = {
    "Artificial Intelligence in Healthcare": (
        "Artificial intelligence is transforming medical diagnostics and clinical healthcare in unprecedented ways. "
        "Deep learning models trained on large radiological image datasets now achieve diagnostic accuracy competitive with experienced radiologists in detecting thoracic pathologies and malignant tumors. "
        "Furthermore, natural language processing tools are revolutionizing clinical documentation by extracting critical diagnostic concepts from unstructured electronic health records, reducing administrative burden on clinicians. "
        "However, integrating algorithmic systems into medical decision workflows presents substantial challenges regarding clinical safety, interpretability, and algorithmic bias across underrepresented demographic cohorts. "
        "Medical practitioners emphasize that deep learning must serve as clinical decision support rather than autonomous replacement, ensuring human judgment remains central to patient care."
    ),
    "Deep Learning & Sequence Transformers": (
        "The introduction of the Transformer architecture by Vaswani et al. in 2017 fundamentally reshaped modern natural language processing. "
        "Prior sequence transduction models relied heavily on complex recurrent or convolutional neural networks operating sequentially over token steps. "
        "By replacing recurrence entirely with multi-head self-attention mechanisms, Transformers compute representations for all input positions concurrently, enabling exceptional training parallelization on modern GPU clusters. "
        "Bidirectional and auto-regressive variants, notably BERT and BART, leverage self-supervised pretraining objectives over massive corpora before downstream task adaptation. "
        "In abstractive text summarization, sequence-to-sequence models synthesize long documents into condensed semantic abstracts by attending across encoder contextual representations and generating fluent tokens autoregressively."
    ),
    "Renewable Energy & Climate Transition": (
        "Global transition towards decarbonized energy systems has accelerated dramatically as photovoltaic and wind turbine costs decline worldwide. "
        "Grid integration of variable renewable sources requires advanced computational forecasting, grid-scale lithium-ion battery storage, and dynamic load balancing. "
        "Policy frameworks across major industrialized economies incentivize industrial electrification while phasing out subcritical coal generation. "
        "Nevertheless, critical supply chain dependencies for rare earth elements and mineral refining infrastructure present systemic bottlenecks. "
        "Achieving net-zero greenhouse gas emission milestones necessitates cohesive international collaboration, modern transmission networks, and sustained public-private capital investment."
    )
}

def render_summarize_text():
    """Renders the text summarization interface."""
    st.markdown("## ✍️ Abstractive Text Summarization")
    st.caption("Generate natural-language abstracts from text using sequence-to-sequence Transformer models.")

    service = SummarizationService()

    # Layout: Main input column and configuration column
    col_input, col_config = st.columns([2, 1])

    with col_config:
        st.markdown("#### ⚙️ Model & Generation")
        
        # Model selector
        model_options = list(config.SUPPORTED_MODELS.keys())
        model_labels = [config.SUPPORTED_MODELS[k]["display_name"] for k in model_options]
        selected_model_idx = st.selectbox(
            "Transformer Model",
            range(len(model_options)),
            format_func=lambda idx: model_labels[idx],
            help="Select the Transformer architecture. BART is recommended and locally loaded."
        )
        selected_model_key = model_options[selected_model_idx]
        model_meta = config.SUPPORTED_MODELS[selected_model_key]

        # Length Mode
        length_mode = st.radio(
            "Summary Length",
            options=["short", "medium", "long"],
            format_func=lambda x: config.LENGTH_PROFILES[x]["label"],
            index=1,
            help="Determines generation length constraints and length penalty."
        )

        with st.expander("🛠️ Advanced Inference Settings"):
            preset = config.LENGTH_PROFILES[length_mode]
            custom_min = st.slider("Min Output Tokens", 10, 150, preset["min_tokens"])
            custom_max = st.slider("Max Output Tokens", 40, 300, preset["max_tokens"])
            custom_beams = st.slider("Beam Search Count", 1, 6, preset["num_beams"], help="Number of beams for deterministic sequence search.")
            do_sample = st.checkbox("Sampling (do_sample)", value=False, help="Enable stochastic sampling. Default is deterministic beam search.")

    with col_input:
        # Sample selection helper
        sample_choice = st.selectbox(
            "Load an academic sample text:",
            options=["-- Select Sample Document --"] + list(SAMPLE_TEXTS.keys())
        )
        if sample_choice != "-- Select Sample Document --":
            st.session_state["input_text_area"] = SAMPLE_TEXTS[sample_choice]

        # Text input area
        input_text = st.text_area(
            "Paste or type your document text below:",
            value=st.session_state.get("input_text_area", ""),
            height=280,
            key="input_text_area",
            placeholder="Paste raw text, news articles, academic passages, or reports here..."
        )

        # Real-time statistics bar
        stats = compute_text_stats(input_text)
        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
        stat_col1.caption(f"Words: **{stats['word_count']}**")
        stat_col2.caption(f"Characters: **{stats['char_count']}**")
        stat_col3.caption(f"Sentences: **{stats['sentence_count']}**")
        # Estimate tokens (approx 1.3 tokens per word for English)
        est_tokens = int(stats["word_count"] * 1.3)
        stat_col4.caption(f"Est. Tokens: **~{est_tokens}** / {model_meta['max_input_tokens']}")

        btn_col1, btn_col2 = st.columns([1, 4])
        with btn_col1:
            generate_clicked = st.button("🚀 Summarize", type="primary", use_container_width=True)
        with btn_col2:
            if st.button("🧹 Clear Input", use_container_width=False):
                st.session_state["input_text_area"] = ""
                st.session_state.pop("latest_summary_result", None)
                st.rerun()

    # Trigger Generation
    if generate_clicked:
        if not input_text or not input_text.strip():
            st.warning("⚠️ Input is empty. Please paste or enter text before summarizing.")
        elif stats["word_count"] < 5:
            st.warning(f"⚠️ Input text is too short ({stats['word_count']} words). Minimum 5 words required.")
        else:
            with st.spinner(f"Running abstractive summarization with {model_meta['display_name']}..."):
                result = service.generate_summary(
                    text=input_text,
                    model_key=selected_model_key,
                    length_mode=length_mode,
                    custom_min_tokens=custom_min,
                    custom_max_tokens=custom_max,
                    custom_num_beams=custom_beams,
                    do_sample=do_sample
                )

            if result.get("success", False):
                st.session_state["latest_summary_result"] = result
                # Log to history
                record = HistoryService.create_record(result, source_type="Pasted Text")
                history = st.session_state.get("history_records", [])
                history.insert(0, record)
                st.session_state["history_records"] = history
                st.success("✅ Abstractive summary generated successfully!")
            else:
                st.error(f"❌ Summarization failed: {result.get('error', 'Unknown error')}")

    # Display Output Section if summary exists
    result = st.session_state.get("latest_summary_result")
    if result and result.get("success", False):
        st.markdown("---")
        st.markdown("### 📋 Generated Summary")

        # Metric badges
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Original Words", result["input_word_count"])
        m2.metric("Summary Words", result["summary_word_count"])
        m3.metric("Compression", f"{result['compression_ratio']}%")
        m4.metric("Latency", f"{result['processing_time']}s")
        chunk_badge = f"{result['chunks_count']} chunk(s)" if result["is_chunked"] else "Single pass"
        m5.metric("Processing Mode", chunk_badge)

        # Summary text box
        st.markdown(
            f"""
            <div style="background-color: #F8FAFC; border: 1px solid #CBD5E1; border-left: 4px solid #1E3A8A; border-radius: 8px; padding: 1.2rem; font-size: 1.05rem; line-height: 1.6; color: #0F172A;">
                {result['summary']}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)

        # Working Action & Download Buttons
        col_txt, col_md, col_json, col_copy = st.columns(4)

        metadata_dict = {
            "model": result["model_name"],
            "original_words": result["input_word_count"],
            "summary_words": result["summary_word_count"],
            "compression_ratio": result["compression_ratio"],
            "processing_time": result["processing_time"],
            "source": "Pasted Text",
        }

        with col_txt:
            txt_content = format_summary_txt(result["summary"], metadata_dict)
            st.download_button(
                label="📥 Download TXT",
                data=txt_content,
                file_name="abstractive_summary.txt",
                mime="text/plain",
                use_container_width=True
            )

        with col_md:
            md_content = format_summary_markdown(result["summary"], metadata_dict)
            st.download_button(
                label="📥 Download Markdown",
                data=md_content,
                file_name="abstractive_summary.md",
                mime="text/markdown",
                use_container_width=True
            )

        with col_json:
            json_content = format_summary_json(result["summary"], metadata_dict)
            st.download_button(
                label="📥 Download JSON",
                data=json_content,
                file_name="abstractive_summary.json",
                mime="application/json",
                use_container_width=True
            )

        with col_copy:
            st.code(result["summary"], language=None)
