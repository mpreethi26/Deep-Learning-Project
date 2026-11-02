"""
Main Streamlit Application.
Abstractive Text Summarization Using Transformer Models.
Team Lead: CHOUDAM BHARATH REDDY
"""
import streamlit as st
import config
from components.sidebar import render_sidebar
from components.dashboard import render_dashboard
from components.summarization_ui import render_summarize_text
from components.pdf_ui import render_summarize_pdf
from components.comparison_ui import render_model_comparison
from components.evaluation_ui import render_evaluation
from components.history_ui import render_history
from components.research_ui import render_research_methodology, render_about_project

# Page Configuration
st.set_page_config(
    page_title="Neural Summarizer | DL & NLP",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for modern academic AI aesthetics
st.markdown(
    """
    <style>
    /* Global font & clean spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1280px;
    }
    /* Buttons */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    /* Metric Cards */
    [data-testid="stMetricValue"] {
        font-size: 1.4rem;
        font-weight: 700;
        color: #1E3A8A;
    }
    /* Smooth tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Session State Initialization
if "history_records" not in st.session_state:
    st.session_state["history_records"] = []
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Dashboard"

# Navigation
selected_page = render_sidebar()

# Routing
if selected_page == "Dashboard":
    render_dashboard()
elif selected_page == "Summarize Text":
    render_summarize_text()
elif selected_page == "Summarize PDF":
    render_summarize_pdf()
elif selected_page == "Model Comparison":
    render_model_comparison()
elif selected_page == "Evaluation":
    render_evaluation()
elif selected_page == "Summary History":
    render_history()
elif selected_page == "Research & Methodology":
    render_research_methodology()
elif selected_page == "About Project":
    render_about_project()
else:
    render_dashboard()
