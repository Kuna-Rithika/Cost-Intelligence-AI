import pandas as pd
import sys
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import ask_claude, format_inr, confidence_gate, print_section

def load_cloud_costs():
    return pd.read_csv("data/cloud_costs.csv")

def detect_anomaly(df: pd.DataFrame) -> dict:
    monthly = df.groupby("month")["cost_inr"].sum().reset_index()
    monthly = monthly.sort_values("month").reset_index(drop=True)
    best_idx = 1
    best_spike = 0
    for i in range(1, len(monthly)):
        prev = monthly.iloc[i-1]["cost_inr"]
        curr = monthly.iloc[i]["cost_inr"]
        change = ((curr - prev) / prev) * 100
        if change > best_spike:
            best_spike = change
            best_idx = i
    latest = monthly.iloc[best_idx]
    previous = monthly.iloc[best_idx - 1]
    change_pct = ((latest["cost_inr"] - previous["cost_inr"]) / previous["cost_inr"]) * 100
    return {
        "latest_month": latest["month"],
        "latest_cost": latest["cost_inr"],
        "previous_month": previous["month"],
        "previous_cost": previous["cost_inr"],
        "change_pct": round(change_pct, 2),
        "is_anomaly": change_pct >= 20
    }

def diagnose_root_cause(df: pd.DataFrame, anomaly: dict) -> dict:
    latest_month = anomaly["latest_month"]
    latest = df[df["month"] == latest_month].copy()
    real_anomalies = latest[latest["anomaly_type"] != "none"]["anomaly_type"].value_counts()
    dominant_cause = real_anomalies.index[0] if len(real_anomalies) > 0 else "normal_variance"
    service_costs = latest.groupby("service")["cost_inr"].sum().sort_values(ascending=False)
    top_service = service_costs.index[0]
    top_cost = service_costs.iloc[0]
    cause_map = {
        "autoscaling_misconfiguration": {
            "cause": "Autoscaling Misconfiguration",
            "description": "EKS/EC2 autoscaling rules triggered excessive instance spin-up",
            "confidence": 0.92,
            "fix": "Reset autoscaling policies, set max instance limits"
        },
        "provisioning_error": {
            "cause": "Provisioning Error",
            "description": "Unused resources were provisioned and left running",
            "confidence": 0.88,
            "fix": "Terminate idle instances, implement resource tagging policy"
        },
        "seasonal_traffic": {
            "cause": "Seasonal Traffic Spike",
            "description": "Expected traffic increase due to business seasonality",
            "confidence": 0.78,
            "fix": "Pre-scale resources, negotiate reserved instance pricing"
        },
        "normal_variance": {
            "cause": "Normal Variance",
            "description": "Cost change within acceptable range",
            "confidence": 0.95,
            "fix": "No action needed"
        }
    }
    diagnosis = cause_map.get(dominant_cause, cause_map["normal_variance"])
    diagnosis["top_service"] = top_service
    diagnosis["top_service_cost"] = top_cost
    diagnosis["dominant_cause_raw"] = dominant_cause
    return diagnosis

def generate_remediation(anomaly: dict, diagnosis: dict) -> str:
    prompt = f"""You are a cloud FinOps expert for an Indian enterprise.

ANOMALY DETECTED:
- Cloud costs spiked {anomaly['change_pct']}% month-over-month
- Previous month: {format_inr(anomaly['previous_cost'])}
- Current month: {format_inr(anomaly['latest_cost'])}
- Top affected service: {diagnosis['top_service']} ({format_inr(diagnosis['top_service_cost'])})

ROOT CAUSE: {diagnosis['cause']}
Description: {diagnosis['description']}
Confidence: {diagnosis['confidence']*100:.0f}%

Generate a remediation plan with:
1. Immediate action (do within 24 hours)
2. Short-term fix (this week)
3. Long-term prevention (this quarter)
4. Estimated cost recovery in INR
5. Who to notify

Be specific and actionable."""
    return ask_claude(prompt, system="You are a senior cloud cost optimization engineer.")

def run_spend_agent():
    print_section("AGENT 2 — CLOUD SPEND ANOMALY DETECTION")
    df = load_cloud_costs()
    print(f"Loaded {len(df)} cloud billing records")
    anomaly = detect_anomaly(df)
    print(f"\nLatest month: {anomaly['latest_month']} → {format_inr(anomaly['latest_cost'])}")
    print(f"Previous month: {anomaly['previous_month']} → {format_inr(anomaly['previous_cost'])}")
    print(f"Change: {anomaly['change_pct']}%")
    if not anomaly["is_anomaly"]:
        print("No significant anomaly detected.")
        return {"agent": "spend_agent", "anomaly_detected": False}
    print(f"\nANOMALY DETECTED — {anomaly['change_pct']}% spike!")
    diagnosis = diagnose_root_cause(df, anomaly)
    action = confidence_gate(diagnosis["confidence"])
    print(f"\nRoot Cause: {diagnosis['cause']}")
    print(f"Description: {diagnosis['description']}")
    print(f"Confidence: {diagnosis['confidence']*100:.0f}%")
    print(f"Action: [{action}] {diagnosis['fix']}")
    print("\nGenerating AI remediation plan...")
    remediation = generate_remediation(anomaly, diagnosis)
    print("\n" + remediation)
    wasted = anomaly["latest_cost"] - anomaly["previous_cost"]
    return {
        "agent": "spend_agent",
        "anomaly_detected": True,
        "change_pct": anomaly["change_pct"],
        "wasted_inr": wasted,
        "root_cause": diagnosis["cause"],
        "confidence": diagnosis["confidence"],
        "action": action,
        "remediation": remediation
    }

if __name__ == "__main__":
    run_spend_agent()