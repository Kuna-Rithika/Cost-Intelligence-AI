from utils import format_inr

APPROVAL_THRESHOLD = 500000  # Auto-approve actions under ₹5L impact

def check_approval(agent_name: str, result: dict):
    print(f"\n[APPROVAL GATE] — {agent_name}")

    action = result.get("action", "NEEDS_APPROVAL")
    
    if agent_name == "vendor_agent":
        amount = result.get("total_savings_inr", 0)
    elif agent_name == "spend_agent":
        amount = result.get("wasted_inr", 0)
    elif agent_name == "sla_agent":
        amount = result.get("penalty_exposure_inr", 0)
    else:
        amount = 0

    if action == "AUTO_EXECUTE" and amount < APPROVAL_THRESHOLD:
        print(f"  ✅ AUTO-APPROVED — Impact: {format_inr(amount)} (below threshold)")
    else:
        print(f"  ⚠️  NEEDS HUMAN APPROVAL — Impact: {format_inr(amount)}")
        print(f"  → Staged for manager review")