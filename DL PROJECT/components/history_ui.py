"""
History Component.
Displays all summarization runs in the current Streamlit session.
Supports inspecting, copying, downloading, and deleting individual or all records.
"""
import streamlit as st
from utils.download_utils import format_summary_txt, format_summary_markdown

def render_history():
    """Renders the summary history table and viewer."""
    st.markdown("## 📜 Session Summary History")
    st.caption("Review previous summarization records created during this active session. (Stored in-memory per session).")

    records = st.session_state.get("history_records", [])

    if not records:
        st.info("ℹ️ No summarization runs recorded in this session yet.")
        return

    # Clear All Button
    col_stat, col_btn = st.columns([3, 1])
    with col_stat:
        st.write(f"**Total Records:** {len(records)}")
    with col_btn:
        if st.button("🗑️ Clear Entire History", type="secondary"):
            st.session_state["history_records"] = []
            st.rerun()

    st.markdown("---")

    # Render each record as an expandable card
    for idx, rec in enumerate(records):
        header = f"#{rec['id']} | {rec['timestamp']} | {rec['model_name']} | {rec['source_type']} ({rec['summary_word_count']} words, {rec['compression_ratio']}% compressed)"
        with st.expander(header, expanded=(idx == 0)):
            m1, m2, m3, m4 = st.columns(4)
            m1.caption(f"Input Words: **{rec['input_word_count']}**")
            m2.caption(f"Summary Words: **{rec['summary_word_count']}**")
            m3.caption(f"Latency: **{rec['processing_time']}s**")
            m4.caption(f"Mode: **{'Chunked' if rec['is_chunked'] else 'Single Pass'}**")

            st.markdown(
                f"""
                <div style="background: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 6px; padding: 0.8rem; margin: 0.5rem 0; font-size: 0.95rem;">
                    {rec['summary']}
                </div>
                """,
                unsafe_allow_html=True
            )

            d1, d2, d3 = st.columns([1, 1, 2])
            meta = {
                "timestamp": rec["timestamp"],
                "model": rec["model_name"],
                "original_words": rec["input_word_count"],
                "summary_words": rec["summary_word_count"],
                "compression_ratio": rec["compression_ratio"],
                "processing_time": rec["processing_time"],
                "source": rec["source_type"]
            }
            with d1:
                st.download_button(
                    "📥 TXT",
                    format_summary_txt(rec["summary"], meta),
                    file_name=f"summary_{rec['id']}.txt",
                    key=f"dl_txt_{rec['id']}"
                )
            with d2:
                st.download_button(
                    "📥 MD",
                    format_summary_markdown(rec["summary"], meta),
                    file_name=f"summary_{rec['id']}.md",
                    key=f"dl_md_{rec['id']}"
                )
            with d3:
                if st.button("❌ Delete Record", key=f"del_{rec['id']}"):
                    st.session_state["history_records"].pop(idx)
                    st.rerun()
