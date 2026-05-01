import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

API_URL = "http://localhost:8000"

PASS_COLOR = "#4ade80"
FAIL_COLOR = "#f87171"
BG         = "rgba(0,0,0,0)"

CHART_LAYOUT = dict(
    paper_bgcolor=BG,
    plot_bgcolor=BG,
    font=dict(family="Inter, sans-serif", size=13, color="#e2e8f0"),
    title_font=dict(size=15, color="#f1f5f9", family="Inter, sans-serif"),
    margin=dict(t=50, b=40, l=50, r=20),
    legend=dict(
        bgcolor="rgba(255,255,255,0.05)",
        bordercolor="rgba(255,255,255,0.1)",
        borderwidth=1,
        font=dict(size=12),
    ),
    xaxis=dict(
        showgrid=True,
        gridcolor="rgba(255,255,255,0.07)",
        zeroline=False,
        linecolor="rgba(255,255,255,0.12)",
        tickfont=dict(size=11),
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor="rgba(255,255,255,0.07)",
        zeroline=False,
        linecolor="rgba(255,255,255,0.12)",
        tickfont=dict(size=11),
    ),
)

st.set_page_config(
    page_title="Student Performance Dashboard",
    layout="wide",
)

st.title("Student Performance Dashboard")
st.caption("Powered by Streamlit + FastAPI")

@st.cache_data(ttl=60)
def fetch_summary():
    try:
        return requests.get(f"{API_URL}/summary").json()
    except Exception:
        return None

summary = fetch_summary()

if summary:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Students",  summary["total_students"])
    c2.metric("Avg Score",       f"{summary['avg_score']}%")
    c3.metric("Pass Rate",       f"{summary['pass_rate']}%")
    c4.metric("Avg Study Hours", f"{summary['avg_study_hrs']} hrs")
else:
    st.error("Cannot reach the FastAPI backend. Make sure it's running on port 8000.")
    st.stop()

st.divider()

tab1, tab2 = st.tabs(["Data Explorer", "Score Predictor"])


with tab1:
    st.subheader("Explore the Dataset")

    try:
        raw = requests.get(f"{API_URL}/data").json()
        df = pd.DataFrame(raw)
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
        st.stop()

    ch1, ch2 = st.columns(2)

    with ch1:
        fig = px.scatter(
            df, x="study_hours", y="score",
            color="pass_fail",
            color_discrete_map={"Pass": PASS_COLOR, "Fail": FAIL_COLOR},
            labels={"study_hours": "Study Hours / Day", "score": "Exam Score", "pass_fail": "Result"},
            title="Study Hours vs Exam Score",
            trendline="ols",
            trendline_scope="overall",
            trendline_color_override="#94a3b8",
            opacity=0.7,
            size_max=8,
        )
        fig.add_hline(
            y=50, line_dash="dash", line_color="rgba(255,255,255,0.3)", line_width=1,
            annotation_text="Pass Line (50)", annotation_position="top right",
            annotation_font=dict(color="rgba(255,255,255,0.5)", size=11),
        )
        fig.update_traces(marker=dict(size=7, line=dict(width=0)))
        fig.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": True})

    with ch2:
        fig2 = px.scatter(
            df, x="attendance", y="score",
            color="pass_fail",
            color_discrete_map={"Pass": PASS_COLOR, "Fail": FAIL_COLOR},
            labels={"attendance": "Attendance (%)", "score": "Exam Score", "pass_fail": "Result"},
            title="Attendance vs Exam Score",
            trendline="ols",
            trendline_scope="overall",
            trendline_color_override="#94a3b8",
            opacity=0.7,
        )
        fig2.add_hline(
            y=50, line_dash="dash", line_color="rgba(255,255,255,0.3)", line_width=1,
            annotation_text="Pass Line (50)", annotation_position="top right",
            annotation_font=dict(color="rgba(255,255,255,0.5)", size=11),
        )
        fig2.update_traces(marker=dict(size=7, line=dict(width=0)))
        fig2.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": True})

    ch3, ch4 = st.columns(2)

    with ch3:
        fig3 = px.histogram(
            df, x="score", nbins=20,
            color="pass_fail",
            color_discrete_map={"Pass": PASS_COLOR, "Fail": FAIL_COLOR},
            title="Score Distribution",
            labels={"score": "Exam Score", "count": "Students", "pass_fail": "Result"},
            barmode="overlay",
            opacity=0.75,
        )
        fig3.add_vline(
            x=50, line_dash="dash", line_color="rgba(255,255,255,0.3)", line_width=1.5,
            annotation_text="Pass (50)", annotation_position="top right",
            annotation_font=dict(color="rgba(255,255,255,0.5)", size=11),
        )
        fig3.update_layout(**CHART_LAYOUT, bargap=0.05)
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": True})

    with ch4:
        pass_counts = df["pass_fail"].value_counts().reset_index()
        pass_counts.columns = ["Result", "Count"]
        fig4 = go.Figure(go.Pie(
            labels=pass_counts["Result"],
            values=pass_counts["Count"],
            hole=0.55,
            marker=dict(
                colors=[PASS_COLOR if r == "Pass" else FAIL_COLOR for r in pass_counts["Result"]],
                line=dict(color="rgba(0,0,0,0.3)", width=2),
            ),
            textinfo="label+percent",
            textfont=dict(size=13, color="#f1f5f9"),
            hovertemplate="%{label}: %{value} students (%{percent})<extra></extra>",
        ))
        fig4.update_layout(
            title="Pass / Fail Breakdown",
            **{k: v for k, v in CHART_LAYOUT.items() if k not in ("xaxis", "yaxis")},
            annotations=[dict(
                text=f"<b>{len(df)}</b><br>students",
                x=0.5, y=0.5, font=dict(size=14, color="#e2e8f0"),
                showarrow=False,
            )],
        )
        st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": True})

    with st.expander("View Raw Data"):
        st.dataframe(df, use_container_width=True, hide_index=True)


with tab2:
    st.subheader("Predict a Student's Exam Score")
    st.write("Adjust the sliders and click **Predict** to call the FastAPI ML endpoint.")

    col_in, col_out = st.columns([1, 1], gap="large")

    with col_in:
        study_hours = st.slider("Study Hours per Day", 1.0, 10.0, 5.0, 0.5)
        attendance  = st.slider("Attendance (%)", 50.0, 100.0, 75.0, 1.0)

        st.write("")
        predict_btn = st.button("Predict Score", use_container_width=True, type="primary")

    with col_out:
        if predict_btn:
            with st.spinner("Calling FastAPI /predict ..."):
                try:
                    resp = requests.post(
                        f"{API_URL}/predict",
                        json={"study_hours": study_hours, "attendance": attendance},
                    )
                    result = resp.json()

                    score      = result["predicted_score"]
                    outcome    = result["result"]
                    confidence = result["confidence"]

                    color = "#22c55e" if outcome == "Pass" else "#ef4444"
                    st.markdown(
                        f"""
                        <div style="
                            border: 2px solid {color};
                            border-radius: 12px;
                            padding: 24px;
                            text-align: center;
                            background: {color}11;
                        ">
                            <h1 style="color:{color}; margin:0">{score}</h1>
                            <p style="font-size:1.2rem; margin:4px 0">Predicted Score</p>
                            <hr style="border-color:{color}44">
                            <h2 style="color:{color}; margin:8px 0">{outcome}</h2>
                            <p style="color:#888; margin:0">Confidence: <b>{confidence}</b></p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    st.write("")
                    fig_g = go.Figure(go.Bar(
                        x=["Predicted Score"],
                        y=[score],
                        marker=dict(
                            color=score,
                            colorscale=[[0, "#f87171"], [0.5, "#facc15"], [1, "#4ade80"]],
                            cmin=0, cmax=100,
                            line=dict(width=0),
                        ),
                        width=[0.4],
                        text=[f"<b>{score}</b>"],
                        textposition="outside",
                        textfont=dict(size=18, color="#f1f5f9"),
                    ))
                    fig_g.add_hline(
                        y=50, line_dash="dash", line_color="rgba(255,255,255,0.4)", line_width=1.5,
                        annotation_text="Pass threshold (50)",
                        annotation_font=dict(color="rgba(255,255,255,0.5)", size=11),
                    )
                    fig_g.update_layout(
                        yaxis=dict(range=[0, 110], showgrid=True,
                                   gridcolor="rgba(255,255,255,0.07)", zeroline=False),
                        xaxis=dict(showgrid=False, zeroline=False),
                        showlegend=False, height=280,
                        paper_bgcolor=BG, plot_bgcolor=BG,
                        margin=dict(t=30, b=20, l=40, r=20),
                        font=dict(color="#e2e8f0"),
                    )
                    st.plotly_chart(fig_g, use_container_width=True, config={"displayModeBar": True})

                except Exception as e:
                    st.error(f"Prediction failed: {e}")
      