"""
Dashboard Component.
Displays project metadata, active architecture overview, genuine session statistics,
and visual end-to-end pipeline workflow.
"""
import streamlit as st
import config
from services.model_manager import ModelManager
from services.history_service import HistoryService

def render_dashboard():
    """Renders the executive academic dashboard page."""
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #1E3A8A 0%, #312E81 100%); padding: 1.8rem; border-radius: 12px; color: white; margin-bottom: 1.5rem;">
            <span style="background: rgba(255,255,255,0.18); padding: 4px 10px; border-radius: 16px; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">
                Academic NLP Research Project
            </span>
            <h1 style="color: white; margin: 0.6rem 0 0.3rem 0; font-size: 2rem; font-weight: 700;">
                {config.PROJECT_TITLE}
            </h1>
            <p style="color: #E2E8F0; margin: 0; font-size: 0.95rem; line-height: 1.5;">
                Genuine abstractive text summarization powered by pretrained sequence-to-sequence Transformer architectures.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Project Metadata Row
    col_meta1, col_meta2, col_meta3, col_meta4 = st.columns(4)
    with col_meta1:
        st.markdown(
            f"""
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 0.8rem;">
                <div style="color: #64748B; font-size: 0.75rem; text-transform: uppercase;">Team Lead</div>
                <div style="color: #0F172A; font-size: 0.95rem; font-weight: 600; margin-top: 2px;">{config.TEAM_LEAD}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_meta2:
        st.markdown(
            f"""
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 0.8rem;">
                <div style="color: #64748B; font-size: 0.75rem; text-transform: uppercase;">Domain</div>
                <div style="color: #0F172A; font-size: 0.95rem; font-weight: 600; margin-top: 2px;">{config.NLP_DOMAIN}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_meta3:
        st.markdown(
            f"""
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 0.8rem;">
                <div style="color: #64748B; font-size: 0.75rem; text-transform: uppercase;">Primary Model</div>
                <div style="color: #1E3A8A; font-size: 0.95rem; font-weight: 600; margin-top: 2px;">BART Large CNN</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_meta4:
        st.markdown(
            f"""
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 0.8rem;">
                <div style="color: #64748B; font-size: 0.75rem; text-transform: uppercase;">Research Source</div>
                <div style="color: #0F172A; font-size: 0.95rem; font-weight: 600; margin-top: 2px;">{config.REQUIRED_PUBLISHER}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

    # Session Analytics (Derived strictly from live session runs)
    history = st.session_state.get("history_records", [])
    stats = HistoryService.compute_aggregate_stats(history)

    st.markdown("### 📈 Live Session Performance")
    if stats["total_summaries"] == 0:
        st.info("ℹ️ No summarization runs recorded yet in this session. Process text or PDF documents to observe live metrics.")
    else:
        st.caption("Live metrics calculated exclusively from completed summarization passes in this session.")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Documents Processed", f"{stats['total_documents']}")
    c2.metric("Summaries Generated", f"{stats['total_summaries']}")
    c3.metric("Avg Input Words", f"{stats['avg_input_words']}")
    c4.metric("Avg Summary Words", f"{stats['avg_output_words']}")
    c5.metric("Avg Latency", f"{stats['avg_processing_time']}s")

    st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

    # End-to-End Pipeline Workflow
    st.markdown("### 🔄 End-to-End Summarization Pipeline")
    st.markdown(
        """
        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 1.2rem;">
            <div style="display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 8px; font-size: 0.85rem;">
                <div style="background: white; border: 1px solid #CBD5E1; padding: 8px 14px; border-radius: 6px; text-align: center; font-weight: 600; color: #1E293B;">
                    📄 1. Input Document<br/><span style="font-size: 0.75rem; color: #64748B; font-weight: 400;">Raw Text / PDF</span>
                </div>
                <div style="color: #94A3B8; font-weight: bold;">➔</div>
                <div style="background: white; border: 1px solid #CBD5E1; padding: 8px 14px; border-radius: 6px; text-align: center; font-weight: 600; color: #1E293B;">
                    🧹 2. Preprocessing<br/><span style="font-size: 0.75rem; color: #64748B; font-weight: 400;">Cleaning & Validation</span>
                </div>
                <div style="color: #94A3B8; font-weight: bold;">➔</div>
                <div style="background: white; border: 1px solid #CBD5E1; padding: 8px 14px; border-radius: 6px; text-align: center; font-weight: 600; color: #1E293B;">
                    🔢 3. Tokenization<br/><span style="font-size: 0.75rem; color: #64748B; font-weight: 400;">BPE / SentencePiece</span>
                </div>
                <div style="color: #94A3B8; font-weight: bold;">➔</div>
                <div style="background: #EEF2FF; border: 1px solid #C7D2FE; padding: 8px 14px; border-radius: 6px; text-align: center; font-weight: 600; color: #3730A3;">
                    ⚡ 4. Transformer Encoder<br/><span style="font-size: 0.75rem; color: #4F46E5; font-weight: 400;">Self-Attention Layers</span>
                </div>
                <div style="color: #94A3B8; font-weight: bold;">➔</div>
                <div style="background: #EEF2FF; border: 1px solid #C7D2FE; padding: 8px 14px; border-radius: 6px; text-align: center; font-weight: 600; color: #3730A3;">
                    🎯 5. Cross-Attention Decoder<br/><span style="font-size: 0.75rem; color: #4F46E5; font-weight: 400;">Autoregressive Beam Search</span>
                </div>
                <div style="color: #94A3B8; font-weight: bold;">➔</div>
                <div style="background: #ECFDF5; border: 1px solid #A7F3D0; padding: 8px 14px; border-radius: 6px; text-align: center; font-weight: 600; color: #065F46;">
                    📝 6. Abstractive Summary<br/><span style="font-size: 0.75rem; color: #059669; font-weight: 400;">Natural Synthesis</span>
                </div>
                <div style="color: #94A3B8; font-weight: bold;">➔</div>
                <div style="background: white; border: 1px solid #CBD5E1; padding: 8px 14px; border-radius: 6px; text-align: center; font-weight: 600; color: #1E293B;">
                    📊 7. Evaluation<br/><span style="font-size: 0.75rem; color: #64748B; font-weight: 400;">ROUGE-1, 2, L</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # Call to action button navigating to Summarize Text
    col_btn, _ = st.columns([1, 2])
    with col_btn:
        if st.button("🚀 Open Summarization Workspace", type="primary", use_container_width=True):
            st.session_state["current_page"] = "Summarize Text"
            st.rerun()
