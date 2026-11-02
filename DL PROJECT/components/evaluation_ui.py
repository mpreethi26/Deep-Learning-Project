"""
Evaluation Component.
Computes genuine ROUGE-1, ROUGE-2, and ROUGE-L metrics against a reference ground truth.
Includes educational metric tooltips and interactive Plotly visualization.
"""
import streamlit as st
import plotly.graph_objects as go
from services.evaluation_service import EvaluationService

SAMPLE_CANDIDATE = (
    "The Apollo program was an American human spaceflight project conducted by NASA that achieved the first human moon landing in 1969. "
    "Initiated under Eisenhower and championed by President Kennedy, it successfully fulfilled the goal of landing astronauts on the lunar surface."
)

SAMPLE_REFERENCE = (
    "NASA's Apollo program landed the first humans on the Moon in 1969. "
    "Dedicated to President John F. Kennedy's national goal, it marked a historic milestone in human space exploration."
)

def render_evaluation():
    """Renders the NLP evaluation interface."""
    st.markdown("## 🎯 Summary Evaluation & NLP Metrics")
    st.caption("Calculate genuine ROUGE (Recall-Oriented Understudy for Gisting Evaluation) metrics against a reference summary.")

    eval_service = EvaluationService()

    col_cand, col_ref = st.columns(2)
    with col_cand:
        candidate_text = st.text_area(
            "Generated Summary (Candidate):",
            value=st.session_state.get("latest_summary_result", {}).get("summary", SAMPLE_CANDIDATE),
            height=160,
            help="The machine-generated summary to evaluate."
        )

    with col_ref:
        reference_text = st.text_area(
            "Reference Ground Truth (Gold Standard):",
            value=SAMPLE_REFERENCE,
            height=160,
            help="Human-authored reference summary required for objective overlap metrics."
        )

    include_bert = st.checkbox("Include BERTScore (Contextual Embedding Similarity)", value=False)

    if st.button("📊 Calculate ROUGE Metrics", type="primary"):
        with st.spinner("Computing precision, recall, and F1 ROUGE scores..."):
            result = eval_service.evaluate(
                generated_summary=candidate_text,
                reference_summary=reference_text,
                include_bertscore=include_bert
            )

        if result.get("success", False):
            st.session_state["eval_result"] = result
            st.success("✅ Evaluation metrics computed successfully!")
        else:
            st.error(f"❌ Evaluation error: {result.get('error')}")

    eval_res = st.session_state.get("eval_result")
    if eval_res and eval_res.get("success", False):
        metrics = eval_res["metrics"]
        st.markdown("---")
        st.markdown("### 📈 ROUGE Scores Breakdown")

        r1 = metrics["rouge1"]
        r2 = metrics["rouge2"]
        rl = metrics["rougeL"]

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(
                f"""
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-top: 3px solid #1E3A8A; border-radius: 8px; padding: 1rem;">
                    <h4 style="margin: 0; color: #1E3A8A;">ROUGE-1 (Unigrams)</h4>
                    <p style="font-size: 0.8rem; color: #64748B; margin: 4px 0 10px 0;">Measures single-word lexical overlap.</p>
                    <div style="font-size: 1.3rem; font-weight: 700; color: #0F172A;">F1: {r1['fmeasure'] * 100:.1f}%</div>
                    <div style="font-size: 0.82rem; color: #475569; margin-top: 4px;">Precision: {r1['precision'] * 100:.1f}% | Recall: {r1['recall'] * 100:.1f}%</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c2:
            st.markdown(
                f"""
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-top: 3px solid #4F46E5; border-radius: 8px; padding: 1rem;">
                    <h4 style="margin: 0; color: #4F46E5;">ROUGE-2 (Bigrams)</h4>
                    <p style="font-size: 0.8rem; color: #64748B; margin: 4px 0 10px 0;">Measures consecutive two-word overlap.</p>
                    <div style="font-size: 1.3rem; font-weight: 700; color: #0F172A;">F1: {r2['fmeasure'] * 100:.1f}%</div>
                    <div style="font-size: 0.82rem; color: #475569; margin-top: 4px;">Precision: {r2['precision'] * 100:.1f}% | Recall: {r2['recall'] * 100:.1f}%</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c3:
            st.markdown(
                f"""
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-top: 3px solid #059669; border-radius: 8px; padding: 1rem;">
                    <h4 style="margin: 0; color: #059669;">ROUGE-L (LCS)</h4>
                    <p style="font-size: 0.8rem; color: #64748B; margin: 4px 0 10px 0;">Measures longest common subsequence.</p>
                    <div style="font-size: 1.3rem; font-weight: 700; color: #0F172A;">F1: {rl['fmeasure'] * 100:.1f}%</div>
                    <div style="font-size: 0.82rem; color: #475569; margin-top: 4px;">Precision: {rl['precision'] * 100:.1f}% | Recall: {rl['recall'] * 100:.1f}%</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Plotly chart for Precision, Recall, F1
        fig = go.Figure(data=[
            go.Bar(name="Precision", x=["ROUGE-1", "ROUGE-2", "ROUGE-L"], y=[r1["precision"], r2["precision"], rl["precision"]], marker_color="#3B82F6"),
            go.Bar(name="Recall", x=["ROUGE-1", "ROUGE-2", "ROUGE-L"], y=[r1["recall"], r2["recall"], rl["recall"]], marker_color="#10B981"),
            go.Bar(name="F1-Score", x=["ROUGE-1", "ROUGE-2", "ROUGE-L"], y=[r1["fmeasure"], r2["fmeasure"], rl["fmeasure"]], marker_color="#6366F1"),
        ])
        fig.update_layout(
            barmode="group",
            title="ROUGE Metrics Comparison (Score Range 0.0 - 1.0)",
            yaxis=dict(range=[0, 1.05], title="Score"),
            height=320,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

        if "bertscore" in eval_res:
            bs = eval_res["bertscore"]
            if bs.get("success", False):
                st.info(f"✨ **BERTScore:** F1 = {bs['f1']:.4f} | Precision = {bs['precision']:.4f} | Recall = {bs['recall']:.4f}")
            else:
                st.caption(f"ℹ️ {bs.get('error')}")
