import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import ask_claude, format_inr, print_section

def generate_reinvestment_plan(total_saved_inr: float, sources: dict) -> str:
    prompt = f"""You are an enterprise CFO advisor for a mid-size Indian technology company.

Your AI Cost Intelligence system has recovered the following savings:

SAVINGS BREAKDOWN:
- Vendor consolidation: {format_inr(sources.get('vendor_savings', 0))}/year
- Cloud cost recovery: {format_inr(sources.get('cloud_savings', 0))}/year
- SLA penalty avoided: {format_inr(sources.get('sla_savings', 0))}/year
- TOTAL RECOVERED: {format_inr(total_saved_inr)}/year

Now generate a smart reinvestment plan for maximum ROI.

Include:
1. Recommended allocation split (show % and INR amount for each area)
2. Top 3 investment areas with expected 12-month return
3. 6-month compounding ROI projection
4. Risk assessment of each investment
5. One bold strategic recommendation

Investment areas to consider:
- Engineering talent and upskilling
- Cloud infrastructure upgrades
- AI/ML tooling and automation
- Sales and marketing expansion
- R&D and product innovation
- Emergency/contingency reserve

Use Indian business context and realistic ROI numbers."""
    return ask_claude(prompt, system="You are a strategic CFO advisor for Indian technology companies.")

def run_reinvest_agent(vendor_savings=0, cloud_savings=0, sla_savings=0):
    print_section("AGENT 4 — REINVESTMENT ENGINE")
    sources = {
        "vendor_savings": vendor_savings,
        "cloud_savings": cloud_savings,
        "sla_savings": sla_savings
    }
    total = vendor_savings + cloud_savings + sla_savings
    print(f"Total savings recovered: {format_inr(total)}/year")
    print(f"  From vendor consolidation: {format_inr(vendor_savings)}")
    print(f"  From cloud optimization:   {format_inr(cloud_savings)}")
    print(f"  From SLA penalty avoided:  {format_inr(sla_savings)}")
    print("\nGenerating smart reinvestment plan...")
    plan = generate_reinvestment_plan(total, sources)
    print("\n" + plan)
    return {
        "agent": "reinvest_agent",
        "total_saved_inr": total,
        "sources": sources,
        "reinvestment_plan": plan
    }

if __name__ == "__main__":
    run_reinvest_agent(
        vendor_savings=1840000,
        cloud_savings=980000,
        sla_savings=500000
    )