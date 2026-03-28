import pandas as pd
import numpy as np
from faker import Faker
import random
import os

fake = Faker('en_IN')
random.seed(42)
np.random.seed(42)

# ── VENDOR DATA ──────────────────────────────────────────────
def generate_vendors():
    
    # Real Indian vendor categories
    categories = [
        "Cloud Infrastructure", "IT Services", "Software Licensing",
        "Facility Management", "Security Services", "HR & Payroll",
        "Marketing & Advertising", "Legal Services", "Accounting & Finance",
        "Logistics & Supply Chain"
    ]

    # Base vendors — these will have duplicates with different names
    base_vendors = [
        ("Tata Consultancy Services", "IT Services", 2400000),
        ("Infosys Limited", "IT Services", 1800000),
        ("Wipro Technologies", "IT Services", 1500000),
        ("Amazon Web Services", "Cloud Infrastructure", 3200000),
        ("Microsoft Azure India", "Cloud Infrastructure", 2800000),
        ("Google Cloud India", "Cloud Infrastructure", 1900000),
        ("Zomato Business", "Facility Management", 450000),
        ("Swiggy Corporate", "Facility Management", 380000),
        ("HDFC Payroll Services", "HR & Payroll", 920000),
        ("Zoho Corporation", "Software Licensing", 680000),
        ("Freshworks Inc", "Software Licensing", 540000),
        ("Razorpay Payments", "Accounting & Finance", 320000),
        ("SecurityFirst India", "Security Services", 780000),
        ("QuickHeal Technologies", "Security Services", 430000),
        ("DHL India Logistics", "Logistics & Supply Chain", 560000),
    ]

    vendors = []
    vendor_id = 1

    # Add original vendors
    for name, category, spend in base_vendors:
        vendors.append({
            "vendor_id": f"V{vendor_id:03d}",
            "vendor_name": name,
            "category": category,
            "annual_spend_inr": spend,
            "contract_start": fake.date_between(start_date='-3y', end_date='-1y'),
            "payment_terms": random.choice(["Net 30", "Net 45", "Net 60"]),
            "gst_number": f"27{fake.numerify('AAAAA####A#Z#')}",
            "city": random.choice(["Mumbai", "Bangalore", "Hyderabad", "Chennai", "Pune", "Delhi"]),
            "is_duplicate": False
        })
        vendor_id += 1

    # Add DUPLICATE vendors (same service, different names — this is what Agent 1 detects)
    duplicates = [
        ("TCS India Pvt Ltd", "IT Services", 890000),           # duplicate of TCS
        ("Tata CS Limited", "IT Services", 340000),             # duplicate of TCS
        ("Infosys BPO", "IT Services", 620000),                 # duplicate of Infosys
        ("AWS India Services", "Cloud Infrastructure", 980000), # duplicate of AWS
        ("Amazon Cloud India", "Cloud Infrastructure", 450000), # duplicate of AWS
        ("MS Azure Services", "Cloud Infrastructure", 670000),  # duplicate of Microsoft
        ("Microsoft Cloud India", "Cloud Infrastructure", 320000),
        ("Wipro IT Solutions", "IT Services", 430000),          # duplicate of Wipro
        ("HDFC Salary Solutions", "HR & Payroll", 280000),      # duplicate of HDFC
        ("Zoho Software India", "Software Licensing", 190000),  # duplicate of Zoho
        ("Freshdesk Inc", "Software Licensing", 210000),        # duplicate of Freshworks
        ("Quick Heal Antivirus", "Security Services", 180000),  # duplicate of QuickHeal
        ("DHL Express India", "Logistics & Supply Chain", 230000),
        ("Razorpay India", "Accounting & Finance", 140000),
    ]

    for name, category, spend in duplicates:
        vendors.append({
            "vendor_id": f"V{vendor_id:03d}",
            "vendor_name": name,
            "category": category,
            "annual_spend_inr": spend,
            "contract_start": fake.date_between(start_date='-2y', end_date='-6m'),
            "payment_terms": random.choice(["Net 30", "Net 45", "Net 60"]),
            "gst_number": f"27{fake.numerify('AAAAA####A#Z#')}",
            "city": random.choice(["Mumbai", "Bangalore", "Hyderabad", "Chennai", "Pune", "Delhi"]),
            "is_duplicate": True
        })
        vendor_id += 1

    # Fill up to 500 with random unique vendors
    while len(vendors) < 500:
        category = random.choice(categories)
        vendors.append({
            "vendor_id": f"V{vendor_id:03d}",
            "vendor_name": fake.company() + random.choice([" Pvt Ltd", " India", " Solutions", " Technologies", " Services"]),
            "category": category,
            "annual_spend_inr": random.randint(50000, 1200000),
            "contract_start": fake.date_between(start_date='-3y', end_date='-1m'),
            "payment_terms": random.choice(["Net 30", "Net 45", "Net 60"]),
            "gst_number": f"27{fake.numerify('AAAAA####A#Z#')}",
            "city": random.choice(["Mumbai", "Bangalore", "Hyderabad", "Chennai", "Pune", "Delhi"]),
            "is_duplicate": False
        })
        vendor_id += 1

    return pd.DataFrame(vendors)


# ── CLOUD COST DATA ───────────────────────────────────────────
def generate_cloud_costs(spike_multiplier=1.4):
    months = pd.date_range(start='2024-01-01', periods=13, freq='MS')
    services = ["EC2 Compute", "S3 Storage", "RDS Database", "Lambda Functions",
                "CloudFront CDN", "EKS Kubernetes", "ElastiCache", "API Gateway"]
    records = []
    for month in months:
        for service in services:
            base_cost = random.randint(80000, 400000)
            if month.month == 10 and month.year == 2024:
                if service in ["EC2 Compute", "EKS Kubernetes"]:
                    cost = base_cost * spike_multiplier
                    anomaly_type = "autoscaling_misconfiguration"
                elif service == "S3 Storage":
                    cost = base_cost * (spike_multiplier - 0.02)
                    anomaly_type = "provisioning_error"
                else:
                    cost = base_cost * 1.05
                    anomaly_type = "normal_variance"
            else:
                cost = base_cost * random.uniform(0.9, 1.1)
                anomaly_type = "none"
            records.append({
                "month": month.strftime("%Y-%m"),
                "service": service,
                "cost_inr": round(cost, 2),
                "region": random.choice(["ap-south-1", "ap-southeast-1", "us-east-1"]),
                "anomaly_type": anomaly_type,
                "instances_count": random.randint(5, 120),
                "utilization_pct": round(random.uniform(30, 95), 1)
            })
    return pd.DataFrame(records)


# ── SLA TASK DATA ─────────────────────────────────────────────
def generate_sla_tasks():
    teams = ["Alpha", "Beta", "Gamma", "Delta"]
    task_types = ["Bug Fix", "Feature Development", "Code Review",
                  "Client Deliverable", "Testing", "Documentation"]

    tasks = []
    task_id = 1

    for _ in range(200):
        team = random.choice(teams)
        task_type = random.choice(task_types)
        estimated_hours = random.randint(2, 40)
        completed_pct = random.uniform(0.3, 1.0)

        # Inject SLA risk — Team Alpha is behind on Client Deliverables
        if team == "Alpha" and task_type == "Client Deliverable":
            completed_pct = random.uniform(0.3, 0.55)
            priority = "HIGH"
            penalty_inr = random.randint(200000, 800000)
        else:
            priority = random.choice(["LOW", "MEDIUM", "HIGH"])
            penalty_inr = random.randint(0, 300000) if priority == "HIGH" else 0

        tasks.append({
            "task_id": f"T{task_id:03d}",
            "task_name": f"{task_type} - {fake.bs().title()[:30]}",
            "team": team,
            "assignee": fake.name(),
            "task_type": task_type,
            "estimated_hours": estimated_hours,
            "hours_spent": round(estimated_hours * completed_pct * random.uniform(0.8, 1.2), 1),
            "completed_pct": round(completed_pct * 100, 1),
            "due_date": fake.date_between(start_date='today', end_date='+7d'),
            "priority": priority,
            "penalty_inr": penalty_inr,
            "status": "IN_PROGRESS" if completed_pct < 1.0 else "DONE"
        })
        task_id += 1

    return pd.DataFrame(tasks)


# ── MAIN ──────────────────────────────────────────────────────
if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)

    print("Generating vendors.csv ...")
    vendors = generate_vendors()
    vendors.to_csv("data/vendors.csv", index=False)
    print(f"  {len(vendors)} vendors saved")

    print("Generating cloud_costs.csv ...")
    cloud = generate_cloud_costs()
    cloud.to_csv("data/cloud_costs.csv", index=False)
    print(f"  {len(cloud)} records saved")

    print("Generating sla_tasks.csv ...")
    sla = generate_sla_tasks()
    sla.to_csv("data/sla_tasks.csv", index=False)
    print(f"  {len(sla)} tasks saved")

    print("\nAll datasets ready!")