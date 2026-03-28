<<<<<<< HEAD
from agents.vendor_agent import run_vendor_agent
from agents.spend_agent import run_spend_agent
from agents.sla_agent import run_sla_agent
from agents.reinvest_agent import run_reinvest_agent
from approval import check_approval
from utils import print_section, format_inr

def run_all_agents():
    print_section("ENTERPRISE COST INTELLIGENCE SYSTEM — STARTING")
    results = {}

    # Agent 1 — Vendor
    vendor_result = run_vendor_agent()
    results["vendor"] = vendor_result
    check_approval("vendor_agent", vendor_result)

    # Agent 2 — Spend
    spend_result = run_spend_agent()
    results["spend"] = spend_result
    check_approval("spend_agent", spend_result)

    # Agent 3 — SLA
    sla_result = run_sla_agent()
    results["sla"] = sla_result
    check_approval("sla_agent", sla_result)

    # Agent 4 — Reinvest with combined savings
    vendor_savings = vendor_result.get("total_savings_inr", 0)
    cloud_savings = spend_result.get("wasted_inr", 0)
    sla_savings = sla_result.get("penalty_exposure_inr", 0)

    reinvest_result = run_reinvest_agent(
        vendor_savings=vendor_savings,
        cloud_savings=cloud_savings,
        sla_savings=sla_savings
    )
    results["reinvest"] = reinvest_result

    # Final summary
    total = vendor_savings + cloud_savings + sla_savings
    print_section("FINAL SUMMARY")
    print(f"Vendor savings:   {format_inr(vendor_savings)}/year")
    print(f"Cloud recovery:   {format_inr(cloud_savings)}/year")
    print(f"SLA penalty saved:{format_inr(sla_savings)}/year")
    print(f"TOTAL IMPACT:     {format_inr(total)}/year")

    return results

if __name__ == "__main__":
=======
from agents.vendor_agent import run_vendor_agent
from agents.spend_agent import run_spend_agent
from agents.sla_agent import run_sla_agent
from agents.reinvest_agent import run_reinvest_agent
from approval import check_approval
from utils import print_section, format_inr

def run_all_agents():
    print_section("ENTERPRISE COST INTELLIGENCE SYSTEM — STARTING")
    results = {}

    # Agent 1 — Vendor
    vendor_result = run_vendor_agent()
    results["vendor"] = vendor_result
    check_approval("vendor_agent", vendor_result)

    # Agent 2 — Spend
    spend_result = run_spend_agent()
    results["spend"] = spend_result
    check_approval("spend_agent", spend_result)

    # Agent 3 — SLA
    sla_result = run_sla_agent()
    results["sla"] = sla_result
    check_approval("sla_agent", sla_result)

    # Agent 4 — Reinvest with combined savings
    vendor_savings = vendor_result.get("total_savings_inr", 0)
    cloud_savings = spend_result.get("wasted_inr", 0)
    sla_savings = sla_result.get("penalty_exposure_inr", 0)

    reinvest_result = run_reinvest_agent(
        vendor_savings=vendor_savings,
        cloud_savings=cloud_savings,
        sla_savings=sla_savings
    )
    results["reinvest"] = reinvest_result

    # Final summary
    total = vendor_savings + cloud_savings + sla_savings
    print_section("FINAL SUMMARY")
    print(f"Vendor savings:   {format_inr(vendor_savings)}/year")
    print(f"Cloud recovery:   {format_inr(cloud_savings)}/year")
    print(f"SLA penalty saved:{format_inr(sla_savings)}/year")
    print(f"TOTAL IMPACT:     {format_inr(total)}/year")

    return results

if __name__ == "__main__":
>>>>>>> d3f3a69b20c5cc97bedaa85d0090b1f4905adf78
    run_all_agents()