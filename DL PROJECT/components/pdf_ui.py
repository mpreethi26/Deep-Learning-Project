"""
PDF Summarization Component.
Allows users to upload PDF documents, inspect PyMuPDF extracted text,
and run abstractive summarization with hierarchical chunking.
"""
import streamlit as st
import config
from services.pdf_service import PDFService
from services.summarization_service import SummarizationService
from services.history_service import HistoryService
from utils.download_utils import format_summary_txt, format_summary_markdown

def render_summarize_pdf():
    """Renders the PDF upload and summarization interface."""
    st.markdown("## 📄 Document & PDF Summarization")
    st.caption("Upload multi-page PDF documents. PyMuPDF extracts machine-readable text and applies chunked summarization.")

    pdf_service = PDFService()
    sum_service = SummarizationService()

    col_upload, col_settings = st.columns([2, 1])

    with col_settings:
        st.markdown("#### ⚙️ Configuration")
        model_options = list(config.SUPPORTED_MODELS.keys())
        model_labels = [config.SUPPORTED_MODELS[k]["display_name"] for k in model_options]
        sel_idx = st.selectbox(
            "Model",
            range(len(model_options)),
            format_func=lambda idx: model_labels[idx]
        )
        selected_model_key = model_options[sel_idx]
        model_info = config.SUPPORTED_MODELS[selected_model_key]

        length_mode = st.radio(
            "Summary Length",
            options=["short", "medium", "long"],
            format_func=lambda x: config.LENGTH_PROFILES[x]["label"],
            index=1
        )
        show_preview = st.checkbox("Show Extracted Text Preview", value=True)

    with col_upload:
        uploaded_file = st.file_uploader(
            "Upload PDF Document (up to 25 MB):",
            type=["pdf"],
            help="Select a PDF containing text. Note: Scanned image-only PDFs require OCR."
        )

    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        filename = uploaded_file.name

        with st.spinner("Extracting machine-readable text via PyMuPDF..."):
            extraction = pdf_service.extract_text_from_bytes(file_bytes, filename=filename)

        if not extraction.get("success", False):
            st.error(f"❌ Extraction error: {extraction.get('error')}")
            return

        # Metadata cards
        p1, p2, p3, p4 = st.columns(4)
        p1.metric("File Name", filename[:18] + ("..." if len(filename) > 18 else ""))
        p2.metric("File Size", f"{extraction['file_size_mb']} MB")
        p3.metric("Pages (With Text)", f"{extraction['pages_with_text']} / {extraction['total_pages']}")
        p4.metric("Extracted Words", extraction["word_count"])

        if show_preview:
            with st.expander("👁️ Inspect Extracted Document Text", expanded=False):
                max_preview = config.PDF_SETTINGS["max_preview_chars"]
                preview_text = extraction["text"][:max_preview]
                if len(extraction["text"]) > max_preview:
                    preview_text += f"\n\n[... Truncated for display. Full text contains {extraction['word_count']} words ...]"
                st.text_area("Extracted Content Preview", preview_text, height=200, disabled=True)

        if st.button("🚀 Summarize PDF Document", type="primary"):
            with st.spinner(f"Summarizing document using {model_info['display_name']}..."):
                result = sum_service.generate_summary(
                    text=extraction["text"],
                    model_key=selected_model_key,
                    length_mode=length_mode,
                )

            if result.get("success", False):
                st.session_state["latest_pdf_summary"] = result
                # Log history
                rec = HistoryService.create_record(result, source_type="PDF Document", filename=filename)
                hist = st.session_state.get("history_records", [])
                hist.insert(0, rec)
                st.session_state["history_records"] = hist
                st.success("✅ PDF Abstractive summary generated!")
            else:
                st.error(f"❌ Failed: {result.get('error')}")

    # Display PDF Summary Result
    pdf_res = st.session_state.get("latest_pdf_summary")
    if pdf_res and pdf_res.get("success", False):
        st.markdown("---")
        st.markdown("### 📋 PDF Summary Output")

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Input Words", pdf_res["input_word_count"])
        m2.metric("Summary Words", pdf_res["summary_word_count"])
        m3.metric("Compression", f"{pdf_res['compression_ratio']}%")
        m4.metric("Processing Time", f"{pdf_res['processing_time']}s")
        m5.metric("Chunks Processed", f"{pdf_res['chunks_count']}")

        st.markdown(
            f"""
            <div style="background-color: #F8FAFC; border: 1px solid #CBD5E1; border-left: 4px solid #1E3A8A; border-radius: 8px; padding: 1.2rem; font-size: 1.05rem; line-height: 1.6; color: #0F172A;">
                {pdf_res['summary']}
            </div>
            """,
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)
        meta = {
            "model": pdf_res["model_name"],
            "original_words": pdf_res["input_word_count"],
            "summary_words": pdf_res["summary_word_count"],
            "compression_ratio": pdf_res["compression_ratio"],
            "processing_time": pdf_res["processing_time"],
            "source": f"PDF: {uploaded_file.name if uploaded_file else 'Document'}"
        }
        with col1:
            st.download_button(
                "📥 Download Summary TXT",
                format_summary_txt(pdf_res["summary"], meta),
                file_name="pdf_summary.txt",
                mime="text/plain",
                use_container_width=True
            )
        with col2:
            st.download_button(
                "📥 Download Summary Markdown",
                format_summary_markdown(pdf_res["summary"], meta),
                file_name="pdf_summary.md",
                mime="text/markdown",
                use_container_width=True
            )
