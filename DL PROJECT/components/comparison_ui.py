"""
Model Comparison Component.
Compares BART and T5 on the exact same document side-by-side.
Measures real latency, generated output lengths, compression, and visualizes metrics with Plotly.
"""
import streamlit as st
import plotly.graph_objects as go
import config
from services.summarization_service import SummarizationService

SAMPLE_COMPARISON = (
    "Quantum computing leverages the fundamental principles of quantum mechanics—namely superposition and entanglement—"
    "to execute complex calculations exponentially faster than classical supercomputers for specialized problem domains. "
    "While conventional digital architectures represent computation in binary bits that are strictly 0 or 1, quantum systems utilize qubits "
    "that exist in probabilistic linear combinations. Major technology organizations and academic laboratories are building superconducting "
    "and trapped-ion processors; however, quantum decoherence and high gate error rates remain paramount obstacles. "
    "Developing fault-tolerant quantum error correction is essential before quantum systems can execute general algorithms at industrial scale."
)

def render_model_comparison():
    """Renders the side-by-side model comparison workspace."""
    st.markdown("## ⚖️ Model Comparison Workspace")
    st.caption("Compare BART against Flan-T5 on identical input text under controlled generation parameters.")

    sum_service = SummarizationService()

    col1, col2 = st.columns([1, 1])
    with col1:
        model_a = st.selectbox("Model A", ["bart", "t5"], index=0, format_func=lambda k: config.SUPPORTED_MODELS[k]["display_name"])
    with col2:
        model_b = st.selectbox("Model B", ["t5", "bart"], index=0, format_func=lambda k: config.SUPPORTED_MODELS[k]["display_name"])

    input_text = st.text_area(
        "Enter text to compare across both models:",
        value=SAMPLE_COMPARISON,
        height=180
    )

    if st.button("🚀 Run Side-by-Side Comparison", type="primary"):
        if not input_text or len(input_text.split()) < 10:
            st.warning("⚠️ Please provide at least 10 words of text for model comparison.")
            return

        with st.spinner(f"Running inference with Model A: {config.SUPPORTED_MODELS[model_a]['display_name']}..."):
            res_a = sum_service.generate_summary(input_text, model_key=model_a, length_mode="medium")

        with st.spinner(f"Running inference with Model B: {config.SUPPORTED_MODELS[model_b]['display_name']}..."):
            res_b = sum_service.generate_summary(input_text, model_key=model_b, length_mode="medium")

        st.session_state["comparison_results"] = (res_a, res_b)

    results = st.session_state.get("comparison_results")
    if results:
        res_a, res_b = results
        st.markdown("---")
        st.markdown("### 📊 Side-by-Side Results")

        c_a, c_b = st.columns(2)
        with c_a:
            st.markdown(f"#### 🅰️ {res_a.get('model_name', model_a)}")
            if res_a.get("success", False):
                st.markdown(
                    f"""
                    <div style="background: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 8px; padding: 1rem; min-height: 140px; font-size: 0.95rem;">
                        {res_a['summary']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.caption(f"⏱️ **Latency:** {res_a['processing_time']}s | 📝 **Words:** {res_a['summary_word_count']} | 📉 **Compression:** {res_a['compression_ratio']}%")
            else:
                st.error(f"Failed: {res_a.get('error')}")

        with c_b:
            st.markdown(f"#### 🅱️ {res_b.get('model_name', model_b)}")
            if res_b.get("success", False):
                st.markdown(
                    f"""
                    <div style="background: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 8px; padding: 1rem; min-height: 140px; font-size: 0.95rem;">
                        {res_b['summary']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.caption(f"⏱️ **Latency:** {res_b['processing_time']}s | 📝 **Words:** {res_b['summary_word_count']} | 📉 **Compression:** {res_b['compression_ratio']}%")
            else:
                st.error(f"Failed: {res_b.get('error')}")

        # Plotly comparison charts
        if res_a.get("success", False) and res_b.get("success", False):
            st.markdown("#### 📈 Quantitative Comparison")
            chart_col1, chart_col2 = st.columns(2)

            with chart_col1:
                fig_time = go.Figure(data=[
                    go.Bar(
                        x=[res_a["model_name"], res_b["model_name"]],
                        y=[res_a["processing_time"], res_b["processing_time"]],
                        marker_color=["#1E3A8A", "#4F46E5"]
                    )
                ])
                fig_time.update_layout(title="Inference Latency (Seconds)", yaxis_title="Time (s)", margin=dict(l=20, r=20, t=40, b=20), height=300)
                st.plotly_chart(fig_time, use_container_width=True)

            with chart_col2:
                fig_len = go.Figure(data=[
                    go.Bar(
                        x=[res_a["model_name"], res_b["model_name"]],
                        y=[res_a["summary_word_count"], res_b["summary_word_count"]],
                        marker_color=["#059669", "#10B981"]
                    )
                ])
                fig_len.update_layout(title="Summary Length (Word Count)", yaxis_title="Words", margin=dict(l=20, r=20, t=40, b=20), height=300)
                st.plotly_chart(fig_len, use_container_width=True)
