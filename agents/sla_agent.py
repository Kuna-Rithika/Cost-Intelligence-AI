import pandas as pd
import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import ask_claude, format_inr, confidence_gate, print_section

def load_tasks():
    df = pd.read_csv("data/sla_tasks.csv")
    df["due_date"] = pd.to_datetime(df["due_date"], format="mixed")
    return df

def assess_sla_risk(df: pd.DataFrame) -> dict:
    today = pd.Timestamp.today().normalize()
    
    at_risk = df[
        (df["status"] == "IN_PROGRESS") &
        (df["priority"] == "HIGH") &
        (df["completed_pct"] < 70) &
        (df["due_date"] <= today + pd.Timedelta(days=3))
    ].copy()
    
    at_risk["days_remaining"] = (at_risk["due_date"] - today).dt.days
    at_risk["hours_remaining"] = at_risk["estimated_hours"] * (1 - at_risk["completed_pct"] / 100)
    
    total_penalty = at_risk["penalty_inr"].sum()
    
    return {
        "at_risk_tasks": at_risk,
        "total_at_risk": len(at_risk),
        "total_penalty_inr": total_penalty,
        "teams_affected": at_risk["team"].unique().tolist()
    }

def find_reassignable_tasks(df: pd.DataFrame, risk: dict) -> pd.DataFrame:
    at_risk_teams = risk["teams_affected"]
    
    low_priority = df[
        (df["priority"].isin(["LOW", "MEDIUM"])) &
        (df["status"] == "IN_PROGRESS") &
        (df["team"].isin(at_risk_teams))
    ].copy()
    
    low_priority["freeable_hours"] = low_priority["estimated_hours"] * (1 - low_priority["completed_pct"] / 100)
    low_priority = low_priority.sort_values("freeable_hours", ascending=False)
    
    return low_priority.head(10)

def generate_recovery_plan(risk: dict, reassignable: pd.DataFrame) -> str:
    at_risk_summary = "\n".join([
        f"- Task {row['task_id']}: {row['task_name'][:40]} | "
        f"{row['completed_pct']}% done | {row['days_remaining']} days left | "
        f"Penalty: {format_inr(row['penalty_inr'])}"
        for _, row in risk["at_risk_tasks"].iterrows()
    ])
    
    reassign_summary = "\n".join([
        f"- {row['task_id']}: {row['task_name'][:40]} ({row['priority']}) → "
        f"{row['freeable_hours']:.1f} hrs freeable"
        for _, row in reassignable.iterrows()
    ])
    
    prompt = f"""You are an enterprise SLA risk manager for an Indian IT services company.

SLA BREACH RISK — 3 DAYS REMAINING:
{at_risk_summary}

Total penalty exposure: {format_inr(risk['total_penalty_inr'])}
Teams affected: {', '.join(risk['teams_affected'])}

TASKS THAT CAN BE DEPRIORITIZED (to free up resources):
{reassign_summary}

Generate a specific recovery plan with:
1. Which tasks to pause immediately and why
2. How to reassign freed hours to at-risk tasks
3. Message to send to the manager (ready to copy-paste)
4. Escalation trigger — when to escalate to senior management
5. Confidence that SLA can still be met if plan is followed

Be specific. Use Indian IT services business context."""

    return ask_claude(prompt, system="You are a senior delivery manager at an Indian IT services firm.")

def run_sla_agent():
    print_section("AGENT 3 — SLA BREACH PREVENTION")
    
    df = load_tasks()
    print(f"Loaded {len(df)} tasks across {df['team'].nunique()} teams")
    
    risk = assess_sla_risk(df)
    
    if risk["total_at_risk"] == 0:
        print("No SLA breach risk detected.")
        return {"agent": "sla_agent", "breach_risk": False}
    
    print(f"\nSLA BREACH RISK DETECTED!")
    print(f"At-risk tasks: {risk['total_at_risk']}")
    print(f"Penalty exposure: {format_inr(risk['total_penalty_inr'])}")
    print(f"Teams affected: {', '.join(risk['teams_affected'])}")
    
    print("\nAt-risk tasks:")
    for _, row in risk["at_risk_tasks"].iterrows():
        print(f"  {row['task_id']}: {row['task_name'][:40]}")
        print(f"    Progress: {row['completed_pct']}% | Days left: {row['days_remaining']} | Penalty: {format_inr(row['penalty_inr'])}")
    
    reassignable = find_reassignable_tasks(df, risk)
    confidence = 0.87 if len(reassignable) >= 5 else 0.72
    action = confidence_gate(confidence)
    
    print(f"\nAction: [{action}]")
    print(f"Found {len(reassignable)} tasks that can be deprioritized")
    
    print("\nGenerating AI recovery plan...")
    recovery_plan = generate_recovery_plan(risk, reassignable)
    print("\n" + recovery_plan)
    
    return {
        "agent": "sla_agent",
        "breach_risk": True,
        "at_risk_count": risk["total_at_risk"],
        "penalty_exposure_inr": risk["total_penalty_inr"],
        "confidence": confidence,
        "action": action,
        "recovery_plan": recovery_plan
    }

if __name__ == "__main__":
    run_sla_agent()