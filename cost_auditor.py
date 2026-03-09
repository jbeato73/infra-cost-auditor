# =============================================================================
# cost_auditor.py
#
# Author  : Jose M. Beato
# Created : March 9, 2026
# Built with the assistance of Claude (Anthropic) — claude.ai
#
# Description:
#   Reads a raw JSON file of server infrastructure costs, cleans and
#   normalizes the data, applies a 10% infrastructure tax, flags
#   high-cost items, and writes a summary CSV report. This script is
#   the direct predecessor to telecom_cost_auditor.py.
#
# Forked to : telecom-cost-auditor (github.com/jbeato73/telecom-cost-auditor)
#
# Project Setup (run in terminal before opening VS Code):
# ─────────────────────────────────────────────────────
#   1. cd /Users/jmb/PythonProjects
#   2. uv init infra-cost-auditor
#   3. cd infra-cost-auditor
#   4. code .
#   5. python3 -m venv .venv
#   6. source .venv/bin/activate
#   # No extra packages — 100% Python standard library
#   # Create this file as: cost_auditor.py
#
# GitHub Commit (after completing):
# ──────────────────────────────────
#   git add cost_auditor.py
#   git commit -m "refactor: standardize cost_auditor.py header and structure"
#   git push origin main
# =============================================================================

import json     # Built-in: read raw cost data from JSON
import csv      # Built-in: write audit results to CSV
import os       # Built-in: file existence check
from datetime import datetime  # Built-in: audit date stamp


# =============================================================================
# SECTION 1 — CONFIGURATION
# Best Practice: Never hardcode values that might change. Keep them at the
# top of your script in one place so they're easy to find and update.
# =============================================================================

INPUT_FILE        = "raw_costs.json"     # Raw server cost input
OUTPUT_CSV        = "finance_report.csv" # Cleaned audit output
INFRA_TAX_RATE    = 0.10                 # 10% infrastructure overhead tax
HIGH_COST_THRESHOLD = 2000.00            # Flag servers above this monthly cost


# =============================================================================
# SECTION 2 — DATA LOADING
# Best Practice: Always separate loading from processing. If the file
# format changes, you only need to update this one function.
# =============================================================================


def load_cost_records(filepath):
    """
    Reads raw server cost data from a JSON file.

    Args:
        filepath (str): Path to the input JSON file.

    Returns:
        list[dict]: Raw cost records, or empty list on error.
    """
    if not os.path.exists(filepath):
        print(f"[ERROR] File not found: '{filepath}'")
        print(f"        Make sure '{filepath}' is in the same folder as this script.")
        return []

    try:
        with open(filepath, "r") as f:
            data = json.load(f)
        print(f"[INFO] Loaded {len(data)} records from '{filepath}'")
        return data
    except Exception as e:
        print(f"[ERROR] Failed to read '{filepath}': {e}")
        return []


# =============================================================================
# SECTION 3 — AUDIT LOGIC
# Best Practice: Keep your business rules in a dedicated function, separate
# from loading and output. If a rule changes, you update one function.
# =============================================================================


def audit_record(record):
    """
    Cleans and audits a single cost record.
    Applies the infra tax and flags records exceeding the cost threshold.

    Args:
        record (dict): Raw record with 'server' and 'cost' keys.

    Returns:
        dict: Audited record with Server_Name, Total_Cost, Status, Audit_Date.
    """
    name      = record.get("server") or "Unknown-Node"
    raw_cost  = record.get("cost", 0)
    clean_cost = max(0, raw_cost)         # Guard against negative values

    tax_amount  = clean_cost * INFRA_TAX_RATE
    final_cost  = clean_cost + tax_amount

    status = "NORMAL"
    if final_cost > HIGH_COST_THRESHOLD:
        status = "HIGH COST"

    return {
        "Server_Name" : name,
        "Total_Cost"  : f"{final_cost:.2f}",
        "Status"      : status,
        "Audit_Date"  : datetime.now().strftime("%Y-%m-%d"),
    }


def audit_all_records(raw_records):
    """
    Applies audit_record() to every raw cost record.

    Args:
        raw_records (list[dict]): All raw records from the input file.

    Returns:
        list[dict]: All audited records with cost, status, and date.
    """
    return [audit_record(r) for r in raw_records]


# =============================================================================
# SECTION 4 — OUTPUT
# Best Practice: Separate output logic from processing logic.
# =============================================================================


def write_output_csv(records, filepath):
    """
    Writes audited cost records to a CSV file.

    Args:
        records  (list[dict]): Audited records to write.
        filepath (str):        Output file path.
    """
    if not records:
        print("[WARN] No records to write.")
        return

    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["Server_Name", "Total_Cost", "Status", "Audit_Date"]
        )
        writer.writeheader()
        writer.writerows(records)

    print(f"[INFO] Audit CSV written → '{filepath}'")


# =============================================================================
# SECTION 5 — SUMMARY PRINT
# Best Practice: Always print a human-readable summary to the console
# so you know what happened when you run the script.
# =============================================================================


def print_summary(records):
    """
    Prints a formatted cost audit summary to the console.

    Args:
        records (list[dict]): All audited records.
    """
    total_burn    = sum(float(r["Total_Cost"]) for r in records)
    high_cost     = [r for r in records if r["Status"] == "HIGH COST"]

    print()
    print("=" * 60)
    print("  INFRA COST AUDITOR — SUMMARY REPORT")
    print("  Jose M. Beato | March 9, 2026")
    print("=" * 60)
    print(f"  Records processed   : {len(records)}")
    print(f"  Total monthly burn  : ${total_burn:,.2f}")
    print(f"  High-cost items     : {len(high_cost)}")
    print(f"  Output CSV          : {OUTPUT_CSV}")
    print("=" * 60)

    if high_cost:
        print("\n  ⚠  HIGH COST ITEMS:\n")
        for r in high_cost:
            print(f"  Server : {r['Server_Name']}  |  Cost: ${float(r['Total_Cost']):,.2f}")
        print()

    print("=" * 60)
    print()


# =============================================================================
# SECTION 6 — MAIN ENTRY POINT
# Best Practice: Always use `if __name__ == "__main__"` to protect your
# main logic. This allows other scripts to import your functions without
# automatically running the whole pipeline.
# =============================================================================


def main():
    """
    Orchestrates the full audit pipeline:
    Load → Audit → Write CSV → Print Summary
    """
    print()
    print("=" * 60)
    print("  cost_auditor.py — Starting...")
    print("=" * 60)
    print()

    raw_records = load_cost_records(INPUT_FILE)
    if not raw_records:
        print("[ERROR] No records loaded. Exiting.")
        return

    audited_records = audit_all_records(raw_records)
    write_output_csv(audited_records, OUTPUT_CSV)
    print_summary(audited_records)


if __name__ == "__main__":
    main()

