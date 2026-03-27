import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils import format_inr
from agents.vendor_agent import run_vendor_agent, load_vendors, find_duplicate_vendors
from agents.spend_agent import run_spend_agent, load_cloud_costs, detect_anomaly
from agents.sla_agent import run_sla_agent, load_tasks, assess_sla_risk
from agents.reinvest_agent import run_reinvest_agent
from data.generate_data import generate_cloud_costs as gen_cloud

st.set_page_config(
    page_title="Enterprise Cost Intelligence",
    page_icon="💰",
    layout="wide"
)

st.title("🤖 Enterprise Cost Intelligence & Autonomous Action")
st.caption("AI-powered cost detection, diagnosis, and reinvestment planning for Indian enterprises")

# ── SIDEBAR ──────────────────────────────────────────────────
st.sidebar.header("Control Panel")
st.sidebar.markdown("### Scenario Simulator")

scenario = st.sidebar.selectbox(
    "Select Business Scenario",
    [
        "Normal Operations",
        "Vendor Overlap Crisis",
        "Cloud Cost Spike (Autoscaling)",
        "Cloud Cost Spike (Provisioning Error)",
        "SLA Breach Imminent",
        "All Problems at Once"
    ]
)

spike_pct = st.sidebar.slider("Cloud Spike Severity %", 10, 100, 40)
vendor_threshold = st.sidebar.slider("Vendor Similarity Threshold", 50, 95, 75)
sla_days_left = st.sidebar.slider("SLA Days Remaining", 1, 7, 3)

run_button = st.sidebar.button("🚀 Run All Agents", type="primary", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.markdown("**Agent Status:**")
st.sidebar.markdown("✅ Vendor Duplicate Detection")
st.sidebar.markdown("✅ Cloud Spend Anomaly")
st.sidebar.markdown("✅ SLA Breach Prevention")
st.sidebar.markdown("✅ Reinvestment Engine")

# ── LOAD DATA DYNAMICALLY ─────────────────────────────────────
vendors_df = load_vendors()
duplicates = find_duplicate_vendors(vendors_df, threshold=vendor_threshold)

seen_keys = set()
unique_savings = []
for d in duplicates:
    key = tuple(sorted([d["vendor_1"], d["vendor_2"]]))
    if key not in seen_keys:
        seen_keys.add(key)
        unique_savings.append(d["estimated_savings_inr"])
vendor_savings = sum(unique_savings)

# Regenerate cloud data with spike severity from slider
cloud_df = gen_cloud(spike_multiplier=1 + spike_pct / 100)
cloud_df.to_csv("data/cloud_costs.csv", index=False)
cloud_df = load_cloud_costs()
anomaly = detect_anomaly(cloud_df)
cloud_savings = max(0, anomaly["latest_cost"] - anomaly["previous_cost"])

# SLA data with dynamic days remaining
tasks_df = pd.read_csv("data/sla_tasks.csv")
today = pd.Timestamp.today().normalize()

def adjust_due_date(x):
    try:
        d = pd.to_datetime(x, format="mixed")
    except Exception:
        d = pd.to_datetime(x)
    if d <= today + pd.Timedelta(days=4):
        return str((today + pd.Timedelta(days=sla_days_left)).date())
    return str(d.date())

tasks_df["due_date"] = tasks_df["due_date"].apply(adjust_due_date)
tasks_df.to_csv("data/sla_tasks.csv", index=False)
tasks_df = load_tasks()
risk = assess_sla_risk(tasks_df)
sla_savings = risk["total_penalty_inr"]

total_impact = vendor_savings + cloud_savings + sla_savings

# ── METRICS ROW ───────────────────────────────────────────────
st.subheader("📊 Live Financial Impact")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Vendor Savings", format_inr(vendor_savings), "per year")
with col2:
    st.metric("Cloud Recovery", format_inr(cloud_savings), f"{anomaly['change_pct']}% spike")
with col3:
    st.metric("SLA Penalty Avoided", format_inr(sla_savings), f"{risk['total_at_risk']} tasks at risk")
with col4:
    st.metric("Total Impact", format_inr(total_impact), "🎯 Annual savings")

st.markdown("---")

# ── TABS ──────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🏢 Vendor Duplicates",
    "☁️ Cloud Spend",
    "⏰ SLA Risk",
    "💡 Reinvestment Plan"
])

# ── TAB 1 — VENDOR ────────────────────────────────────────────
with tab1:
    st.subheader("Duplicate Vendor Detection")
    st.info(f"Similarity threshold: {vendor_threshold}% | Found {len(duplicates)} duplicate pairs")

    top_dups = duplicates[:15]
    if top_dups:
        df_display = pd.DataFrame([{
            "Vendor 1": d["vendor_1"],
            "Vendor 2": d["vendor_2"],
            "Category": d["category"],
            "Combined Spend": format_inr(d["combined_spend"]),
            "Est. Savings": format_inr(d["estimated_savings_inr"]),
            "Similarity": f"{d['similarity_score']}%",
            "Action": "✅ AUTO" if d["confidence"] >= 0.85 else "⚠️ REVIEW"
        } for d in top_dups])
        st.dataframe(df_display, use_container_width=True)

    cat_savings = {}
    for d in duplicates:
        cat_savings[d["category"]] = cat_savings.get(d["category"], 0) + d["estimated_savings_inr"]

    if cat_savings:
        fig = px.bar(
            x=list(cat_savings.keys()),
            y=[v / 100000 for v in cat_savings.values()],
            labels={"x": "Category", "y": "Savings (₹ Lakhs)"},
            title="Savings Potential by Category",
            color=list(cat_savings.values()),
            color_continuous_scale="Teal"
        )
        st.plotly_chart(fig, use_container_width=True)

    if run_button:
        with st.spinner("Running Vendor Agent with AI..."):
            result = run_vendor_agent()
            st.success("Agent completed!")
            st.markdown("**AI Action Plan:**")
            st.markdown(result["action_plan"])

# ── TAB 2 — CLOUD ─────────────────────────────────────────────
with tab2:
    st.subheader("Cloud Spend Anomaly Detection")
    st.info(f"Simulated spike: {spike_pct}% | Detected spike month: {anomaly['latest_month']}")

    monthly = cloud_df.groupby("month")["cost_inr"].sum().reset_index()
    monthly = monthly.sort_values("month").reset_index(drop=True)

    fig = px.line(
        monthly, x="month", y="cost_inr",
        title="Monthly Cloud Spend (₹)",
        markers=True
    )

    spike_month = anomaly["latest_month"]
    if spike_month in monthly["month"].values:
        spike_pos = monthly[monthly["month"] == spike_month].index[0]
        fig.add_shape(
            type="line",
            x0=spike_pos, x1=spike_pos,
            y0=0, y1=1,
            xref="x", yref="paper",
            line=dict(color="red", dash="dash", width=2)
        )
        fig.add_annotation(
            x=spike_pos, y=1,
            xref="x", yref="paper",
            text=f"{anomaly['change_pct']}% Spike",
            showarrow=False,
            font=dict(color="red")
        )

    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.error(f"**Anomaly:** {anomaly['change_pct']}% spike detected")
        st.write(f"Previous month ({anomaly['previous_month']}): {format_inr(anomaly['previous_cost'])}")
        st.write(f"Spike month ({anomaly['latest_month']}): {format_inr(anomaly['latest_cost'])}")
        st.write(f"Wasted: {format_inr(cloud_savings)}")
    with col2:
        service_cost = cloud_df[cloud_df["month"] == anomaly["latest_month"]].groupby("service")["cost_inr"].sum()
        fig2 = px.pie(
            values=service_cost.values,
            names=service_cost.index,
            title="Cost Breakdown by Service"
        )
        st.plotly_chart(fig2, use_container_width=True)

    if run_button:
        with st.spinner("Running Spend Agent with AI..."):
            result = run_spend_agent()
            st.success("Agent completed!")
            st.markdown("**AI Remediation Plan:**")
            st.markdown(result.get("remediation", ""))

# ── TAB 3 — SLA ───────────────────────────────────────────────
with tab3:
    st.subheader("SLA Breach Prevention")
    st.info(f"Days remaining: {sla_days_left} | At-risk tasks: {risk['total_at_risk']}")

    if risk["total_at_risk"] > 0:
        st.error(f"⚠️ {risk['total_at_risk']} tasks at risk | Penalty exposure: {format_inr(sla_savings)}")

        at_risk_df = risk["at_risk_tasks"][[
            "task_id", "task_name", "team", "completed_pct",
            "days_remaining", "penalty_inr"
        ]].copy()
        at_risk_df["penalty_inr"] = at_risk_df["penalty_inr"].apply(format_inr)
        at_risk_df.columns = ["ID", "Task", "Team", "Progress %", "Days Left", "Penalty"]
        st.dataframe(at_risk_df, use_container_width=True)

        team_data = tasks_df.groupby("team")["completed_pct"].mean().reset_index()
        fig = px.bar(
            team_data, x="team", y="completed_pct",
            title="Average Task Completion by Team",
            color="completed_pct",
            color_continuous_scale="RdYlGn"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("✅ No SLA breach risk detected for current settings!")

    if run_button:
        with st.spinner("Running SLA Agent with AI..."):
            result = run_sla_agent()
            st.success("Agent completed!")
            st.markdown("**AI Recovery Plan:**")
            st.markdown(result.get("recovery_plan", ""))

# ── TAB 4 — REINVESTMENT ──────────────────────────────────────
with tab4:
    st.subheader("💡 Smart Reinvestment Engine")
    st.caption("Unique feature — AI tells you WHERE to invest the money you saved")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("From Vendor Savings", format_inr(vendor_savings))
    with col2:
        st.metric("From Cloud Recovery", format_inr(cloud_savings))
    with col3:
        st.metric("From SLA Avoidance", format_inr(sla_savings))

    st.markdown(f"### Total Available for Reinvestment: {format_inr(total_impact)}")

    allocation = {
        "Engineering & Talent": 0.30,
        "Cloud Infrastructure": 0.25,
        "AI/ML Tooling": 0.20,
        "Sales & Marketing": 0.15,
        "Contingency Reserve": 0.10
    }

    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(
            values=[v * total_impact for v in allocation.values()],
            names=list(allocation.keys()),
            title=f"Suggested Reinvestment of {format_inr(total_impact)}",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        alloc_df = pd.DataFrame([{
            "Area": k,
            "Allocation %": f"{int(v*100)}%",
            "Amount": format_inr(v * total_impact),
            "Expected ROI": "18-24%" if k == "Engineering & Talent"
                else "12-18%" if k == "Cloud Infrastructure"
                else "25-35%" if k == "AI/ML Tooling"
                else "15-20%" if k == "Sales & Marketing"
                else "Safety buffer"
        } for k, v in allocation.items()])
        st.dataframe(alloc_df, use_container_width=True)

    if run_button:
        with st.spinner("Generating AI Reinvestment Plan..."):
            result = run_reinvest_agent(
                vendor_savings=vendor_savings,
                cloud_savings=cloud_savings,
                sla_savings=sla_savings
            )
            st.success("Reinvestment plan ready!")
            st.markdown("**AI Reinvestment Strategy:**")
            st.markdown(result["reinvestment_plan"])