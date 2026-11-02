"""
Sidebar Component.
Provides professional application navigation, model status indicators,
and hardware environment information.
"""
import streamlit as st
import config
from services.model_manager import ModelManager

NAV_OPTIONS = [
    ("📊 Dashboard", "Dashboard"),
    ("✍️ Summarize Text", "Summarize Text"),
    ("📄 Summarize PDF", "Summarize PDF"),
    ("⚖️ Model Comparison", "Model Comparison"),
    ("🎯 Evaluation", "Evaluation"),
    ("📜 Summary History", "Summary History"),
    ("ℹ️ About Project", "About Project"),
]

def render_sidebar() -> str:
    """Renders the navigation sidebar and returns the selected page."""
    with st.sidebar:
        st.markdown(
            f"""
            <div style="padding: 0.5rem 0 1rem 0; border-bottom: 1px solid #E2E8F0;">
                <h3 style="color: #1E3A8A; margin: 0; font-size: 1.15rem; font-weight: 700;">
                    🧠 Neural Summarizer
                </h3>
                <p style="color: #64748B; margin: 0.2rem 0 0 0; font-size: 0.78rem;">
                    Abstractive NLP
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<p style='font-size: 0.8rem; font-weight: 600; color: #475569; margin: 0.8rem 0 0.4rem 0;'>NAVIGATION</p>", unsafe_allow_html=True)

        # Get or init current page in session state
        current_page = st.session_state.get("current_page", "Dashboard")
        labels = [item[0] for item in NAV_OPTIONS]
        keys = [item[1] for item in NAV_OPTIONS]
        default_index = keys.index(current_page) if current_page in keys else 0

        selected_label = st.radio(
            label="Navigation",
            options=labels,
            index=default_index,
            label_visibility="collapsed"
        )
        selected_page = keys[labels.index(selected_label)]
        st.session_state["current_page"] = selected_page

        st.markdown("---")

        # Hardware & Model Status
        st.markdown("<p style='font-size: 0.8rem; font-weight: 600; color: #475569; margin: 0.4rem 0;'>RUNTIME ENVIRONMENT</p>", unsafe_allow_html=True)
        mm = ModelManager()
        device_name = mm.device_name

        st.markdown(
            f"""
            <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 0.6rem; font-size: 0.8rem;">
                <div style="margin-bottom: 4px;">
                    <span style="color: #64748B;">Compute Device:</span><br/>
                    <strong style="color: #0F172A;">{device_name}</strong>
                </div>
                <div>
                    <span style="color: #64748B;">Primary Model:</span><br/>
                    <strong style="color: #1E3A8A;">facebook/bart-large-cnn</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Session quick stats
        history = st.session_state.get("history_records", [])
        st.markdown(
            f"""
            <div style="margin-top: 1rem; padding: 0.5rem; background-color: #EEF2FF; border-radius: 6px; font-size: 0.78rem; color: #3730A3;">
                <strong>Session Counter:</strong> {len(history)} summaries generated
            </div>
            """,
            unsafe_allow_html=True
        )

    return selected_page
