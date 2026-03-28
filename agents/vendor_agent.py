import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rapidfuzz import fuzz
from utils import ask_claude, format_inr, confidence_gate, print_section

def load_vendors():
    return pd.read_csv("data/vendors.csv")

def find_duplicate_vendors(df: pd.DataFrame, threshold: int = 75) -> list:
    """Find vendors with similar names in the same category."""
    duplicates = []
    vendors_list = df.to_dict("records")

    for i in range(len(vendors_list)):
        for j in range(i + 1, len(vendors_list)):
            v1 = vendors_list[i]
            v2 = vendors_list[j]

            # Only compare vendors in the same category
            if v1["category"] != v2["category"]:
                continue

            # Fuzzy name match score
            score = fuzz.token_sort_ratio(v1["vendor_name"], v2["vendor_name"])

            if score >= threshold:
                combined_spend = v1["annual_spend_inr"] + v2["annual_spend_inr"]
                estimated_savings = combined_spend * 0.15  # 15% savings from consolidation

                duplicates.append({
                    "vendor_1": v1["vendor_name"],
                    "vendor_2": v2["vendor_name"],
                    "category": v1["category"],
                    "vendor_1_spend": v1["annual_spend_inr"],
                    "vendor_2_spend": v2["annual_spend_inr"],
                    "combined_spend": combined_spend,
                    "estimated_savings_inr": estimated_savings,
                    "similarity_score": score,
                    "confidence": round(score / 100, 2)
                })

    # Sort by savings potential
    duplicates.sort(key=lambda x: x["estimated_savings_inr"], reverse=True)
    return duplicates

def calculate_total_savings(duplicates: list) -> float:
    seen = set()
    total = 0
    for d in duplicates:
        key = tuple(sorted([d["vendor_1"], d["vendor_2"]]))
        if key not in seen:
            seen.add(key)
            total += d["estimated_savings_inr"]
    return total

def generate_action_plan(duplicates: list) -> str:
    """Ask Claude to generate a prioritized action plan."""
    top = duplicates[:10]
    summary = "\n".join([
        f"- {d['vendor_1']} + {d['vendor_2']} ({d['category']}) → "
        f"save {format_inr(d['estimated_savings_inr'])} | confidence {d['confidence']}"
        for d in top
    ])

    prompt = f"""You are an enterprise cost intelligence AI for an Indian company.

These duplicate vendors were detected (same service, different entity names):

{summary}

Generate a concise action plan with:
1. Top 5 consolidation actions ranked by savings (use ₹ amounts)
2. Which vendor to retain and which to exit for each pair
3. Estimated timeline to consolidate (weeks)
4. Total annual savings if all actions are taken
5. One risk to watch out for

Keep it sharp and CFO-ready. Use Indian business context."""

    return ask_claude(prompt, system="You are a CFO-level enterprise cost advisor for Indian enterprises.")

def run_vendor_agent():
    print_section("AGENT 1 — VENDOR DUPLICATE DETECTION")

    df = load_vendors()
    print(f"Loaded {len(df)} vendors across {df['category'].nunique()} categories")

    print("\nScanning for duplicates...")
    duplicates = find_duplicate_vendors(df)
    total_savings = calculate_total_savings(duplicates)

    print(f"\nFound {len(duplicates)} duplicate pairs")
    print(f"Total estimated savings: {format_inr(total_savings)}/year")

    print("\nTop 5 duplicate pairs by savings:")
    seen = set()
    shown = 0
    for d in duplicates:
        key = tuple(sorted([d["vendor_1"], d["vendor_2"]]))
        if key in seen or shown >= 5:
            continue
        seen.add(key)
        shown += 1
        action = confidence_gate(d["confidence"])
        print(f"  [{action}] {d['vendor_1']} ↔ {d['vendor_2']}")
        print(f"    Category: {d['category']} | Savings: {format_inr(d['estimated_savings_inr'])} | Score: {d['similarity_score']}")

    print("\nGenerating AI action plan...")
    action_plan = generate_action_plan(duplicates)
    print("\n" + action_plan)

    return {
        "agent": "vendor_agent",
        "duplicates_found": len(duplicates),
        "total_savings_inr": total_savings,
        "top_duplicates": duplicates[:10],
        "action_plan": action_plan
    }

if __name__ == "__main__":
    result = run_vendor_agent()
    print(f"\nSavings Summary: {format_inr(result['total_savings_inr'])}/year")