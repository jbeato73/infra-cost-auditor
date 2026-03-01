import json
import csv
import os
from datetime import datetime


def audit_costs(input_file, output_file):
    if not os.path.exists(input_file):
        print(f"❌ Error: {input_file} not found.")
        return

    try:
        with open(input_file, "r") as f:
            data = json.load(f)

        cleaned_data = []
        total_burn = 0

        for record in data:
            name = record.get("server") or "Unknown-Node"
            raw_cost = record.get("cost", 0)
            clean_cost = max(0, raw_cost)

            # Apply 10% Infra Tax
            tax_amount = clean_cost * 0.10
            final_cost = clean_cost + tax_amount
            total_burn += final_cost

            # --- NEW: High Priority Logic ---
            status = "NORMAL"
            if final_cost > 2000:
                status = "⚠️ HIGH COST"

            cleaned_data.append(
                {
                    "Server_Name": name,
                    "Total_Cost": f"{final_cost:.2f}",
                    "Status": status,
                    "Audit_Date": datetime.now().strftime("%Y-%m-%d"),
                }
            )

        with open(output_file, "w", newline="") as f:
            writer = csv.DictWriter(
                f, fieldnames=["Server_Name", "Total_Cost", "Status", "Audit_Date"]
            )
            writer.writeheader()
            writer.writerows(cleaned_data)

        print(f"✅ Audit Complete. CSV generated: {output_file}")
        print(f"📊 Total Monthly Burn: ${total_burn:,.2f}")

        # Terminal Alert for stakeholders
        high_cost_items = [
            item["Server_Name"] for item in cleaned_data if "HIGH" in item["Status"]
        ]
        if high_cost_items:
            print(
                f"🚨 ATTENTION: {len(high_cost_items)} items exceeded budget: {', '.join(high_cost_items)}"
            )

    except Exception as e:
        print(f"❌ Audit Failed: {e}")


def main():
    audit_costs("raw_costs.json", "finance_report.csv")


if __name__ == "__main__":
    main()
