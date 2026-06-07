"""
============================================================
  Green Lantern Corps Recyclers
  Automated E-Waste Management System (AEWMS)
  Module  : CSE4202 - Fundamentals in Programming
  Assessment: WRIT1 | Semester 01, 2026
  Standard  : PEP 8 compliant
============================================================
"""

import datetime

# ── Constants ─────────────────────────────────────────────
STORAGE_LIMIT = 1000          # Maximum storage in kg
BULK_DISCOUNT_THRESHOLD = 50  # kg above which 5% discount applies
BULK_DISCOUNT_RATE = 0.05
HAZARD_DAYS_LIMIT = 30        # Days before hazard alert fires
VALID_CATEGORIES = ("Recyclable", "Hazardous", "Non-Recyclable")

# Default fee per kg (Rs.) per category
FEE_RATES = {
    "Recyclable":     100,
    "Hazardous":      150,
    "Non-Recyclable":  80,
}

# ── Global data store ─────────────────────────────────────
ewaste_inventory = []   # List of dicts; each dict = one e-waste record
_id_counter = [0]       # Mutable container so inner functions can update


# ══════════════════════════════════════════════════════════
# UTILITY HELPERS
# ══════════════════════════════════════════════════════════

def _next_id():
    """Return the next unique Item ID string, e.g. 'E001'."""
    _id_counter[0] += 1
    return f"E{_id_counter[0]:03d}"


def _find_item(item_id):
    """Return the item dict matching item_id, or None."""
    for item in ewaste_inventory:
        if item["item_id"] == item_id.upper():
            return item
    return None


def _total_weight():
    """Return the sum of weights of all stored items (kg)."""
    return sum(item["weight_kg"] for item in ewaste_inventory)


# ══════════════════════════════════════════════════════════
# 1. DISPLAY ALL ITEMS
# ══════════════════════════════════════════════════════════

def display_items():
    """Display all e-waste records in a formatted console table."""
    if not ewaste_inventory:
        print("\n  [INFO] No e-waste items on record.\n")
        return

    header = (f"  {'ID':<6} {'Device':<18} {'Category':<16}"
              f" {'Weight(kg)':>10} {'Fee/kg':>8}"
              f"  {'Date Stored':<13} Status")
    divider = "  " + "-" * (len(header) - 2)

    print(f"\n{divider}")
    print(header)
    print(divider)
    for item in ewaste_inventory:
        print(
            f"  {item['item_id']:<6} {item['device_name']:<18}"
            f" {item['category']:<16} {item['weight_kg']:>10.2f}"
            f" {item['fee_per_kg']:>8.2f}  {str(item['date_stored']):<13}"
            f" {item['status']}"
        )
    print(divider)
    print(f"  Records: {len(ewaste_inventory)} | "
          f"Total weight: {_total_weight():.2f} kg\n")


# ══════════════════════════════════════════════════════════
# 2. ADD NEW E-WASTE ITEM
# ══════════════════════════════════════════════════════════

def add_item():
    """Collect, validate, and store a new e-waste entry."""
    print("\n── Add New E-Waste Item ──────────────────────────")

    # Device name
    device = input("  Device Name (e.g. Laptop, Mobile): ").strip()
    if not device:
        print("  [Error] Device name cannot be empty.")
        return

    # Category
    print(f"  Valid categories: {', '.join(VALID_CATEGORIES)}")
    raw_cat = input("  Category: ").strip()
    category = next(
        (c for c in VALID_CATEGORIES if c.lower() == raw_cat.lower()), None
    )
    if not category:
        print(f"  [Error] Invalid category '{raw_cat}'.")
        return

    # Weight
    try:
        weight = float(input("  Weight (kg): "))
        if weight <= 0:
            raise ValueError("Non-positive weight")
    except ValueError:
        print("  [Error] Weight must be a positive number.")
        return

    # Storage check before adding
    if not check_storage(weight):
        return

    # Build record
    record = {
        "item_id":     _next_id(),
        "device_name": device,
        "category":    category,
        "weight_kg":   weight,
        "fee_per_kg":  FEE_RATES[category],
        "date_stored": datetime.date.today(),
        "status":      "Stored",
    }
    ewaste_inventory.append(record)
    print(f"  [OK] Item added — ID: {record['item_id']}")


# ══════════════════════════════════════════════════════════
# 3. UPDATE ITEM WEIGHT
# ══════════════════════════════════════════════════════════

def update_item():
    """Update the weight of an existing e-waste item by ID."""
    item_id = input("\n  Item ID to update: ").strip()
    item = _find_item(item_id)
    if not item:
        print(f"  [Error] Item '{item_id}' not found.")
        return
    try:
        new_wt = float(input(f"  New weight for {item['device_name']} (kg): "))
        if new_wt <= 0:
            raise ValueError
    except ValueError:
        print("  [Error] Weight must be a positive number.")
        return
    item["weight_kg"] = new_wt
    print(f"  [OK] Weight updated to {new_wt:.2f} kg.")


# ══════════════════════════════════════════════════════════
# 4. DELETE / MARK ITEM
# ══════════════════════════════════════════════════════════

def delete_item():
    """Permanently remove an item or change its status."""
    item_id = input("\n  Item ID to remove/mark: ").strip()
    item = _find_item(item_id)
    if not item:
        print(f"  [Error] Item '{item_id}' not found.")
        return
    action = input(
        f"  Action for {item['device_name']} — "
        "[D]elete / [R]ecycled / [P]rocessed: "
    ).strip().upper()
    if action == "D":
        ewaste_inventory.remove(item)
        print(f"  [OK] Item {item_id} deleted.")
    elif action in ("R", "P"):
        item["status"] = "Recycled" if action == "R" else "Processed"
        print(f"  [OK] Status → {item['status']}.")
    else:
        print("  [Error] Unknown action. Enter D, R, or P.")


# ══════════════════════════════════════════════════════════
# 5. CALCULATE RECYCLING FEE
# ══════════════════════════════════════════════════════════

def calculate_fee():
    """Compute recycling fee for an item; apply 5% bulk discount if >50kg."""
    item_id = input("\n  Item ID for fee calculation: ").strip()
    item = _find_item(item_id)
    if not item:
        print(f"  [Error] Item '{item_id}' not found.")
        return

    weight = item["weight_kg"]
    rate = item["fee_per_kg"]
    gross = weight * rate
    discount = gross * BULK_DISCOUNT_RATE if weight > BULK_DISCOUNT_THRESHOLD else 0.0
    total = gross - discount

    print("\n" + "  " + "─" * 46)
    print(f"  RECYCLING FEE INVOICE")
    print("  " + "─" * 46)
    print(f"  Item       : {item['device_name']} ({item['item_id']})")
    print(f"  Category   : {item['category']}")
    print(f"  Weight     : {weight:.2f} kg")
    print(f"  Rate       : Rs. {rate:.2f} / kg")
    print(f"  Gross Fee  : Rs. {gross:.2f}")
    if discount:
        print(f"  Discount   : Rs. {discount:.2f} (5% bulk)")
    print(f"  TOTAL FEE  : Rs. {total:.2f}")
    print("  " + "─" * 46)


# ══════════════════════════════════════════════════════════
# 6. SEARCH ITEMS
# ══════════════════════════════════════════════════════════

def search_items():
    """Search e-waste by Item ID (exact) or Device Name (substring)."""
    mode = input("\n  Search by [I]tem ID or [D]evice Name? ").strip().upper()
    query = input("  Search term: ").strip()

    if mode == "I":
        results = [i for i in ewaste_inventory
                   if i["item_id"] == query.upper()]
    elif mode == "D":
        results = [i for i in ewaste_inventory
                   if query.lower() in i["device_name"].lower()]
    else:
        print("  [Error] Enter I or D.")
        return

    if results:
        print(f"\n  {len(results)} record(s) found:")
        for r in results:
            print(f"    {r['item_id']} | {r['device_name']} | "
                  f"{r['category']} | {r['weight_kg']:.2f} kg | {r['status']}")
    else:
        print(f"  No records match '{query}'.")


# ══════════════════════════════════════════════════════════
# 7. SORT ITEMS
# ══════════════════════════════════════════════════════════

def sort_items():
    """Sort inventory by weight (descending) or category (ascending)."""
    mode = input("\n  Sort by [W]eight or [C]ategory? ").strip().upper()
    if mode == "W":
        ewaste_inventory.sort(key=lambda x: x["weight_kg"], reverse=True)
        print("  [OK] Sorted by weight — highest first.")
    elif mode == "C":
        ewaste_inventory.sort(key=lambda x: x["category"])
        print("  [OK] Sorted by category — A to Z.")
    else:
        print("  [Error] Enter W or C.")
        return
    display_items()


# ══════════════════════════════════════════════════════════
# 8. CHECK STORAGE CAPACITY
# ══════════════════════════════════════════════════════════

def check_storage(incoming_weight: float = 0.0) -> bool:
    """
    Check if storage can accept incoming_weight.

    Returns True if safe, False if adding would exceed STORAGE_LIMIT.
    Prints a warning when usage exceeds 80%.
    """
    projected = _total_weight() + incoming_weight
    pct = (projected / STORAGE_LIMIT) * 100

    if projected > STORAGE_LIMIT:
        print(f"  [BLOCKED] Storage full: {projected:.2f}/{STORAGE_LIMIT} kg. "
              f"Cannot add item.")
        return False
    elif pct >= 80:
        print(f"  [WARNING] Storage at {pct:.1f}% "
              f"({projected:.2f}/{STORAGE_LIMIT} kg). Consider disposal.")
    else:
        print(f"  [INFO] Storage: {projected:.2f}/{STORAGE_LIMIT} kg "
              f"({pct:.1f}% used).")
    return True


# ══════════════════════════════════════════════════════════
# 9. HAZARD ALERT
# ══════════════════════════════════════════════════════════

def hazard_alert():
    """Identify Hazardous items stored longer than HAZARD_DAYS_LIMIT days."""
    today = datetime.date.today()
    alerts = []
    for item in ewaste_inventory:
        if item["category"] == "Hazardous":
            days = (today - item["date_stored"]).days
            if days > HAZARD_DAYS_LIMIT:
                alerts.append((item, days))

    if not alerts:
        print("\n  [OK] No hazardous items require immediate attention.")
        return

    alerts.sort(key=lambda x: x[1], reverse=True)
    print("\n  [URGENT] Hazardous Items Requiring Immediate Disposal:")
    print(f"  {'ID':<6} {'Device':<20} {'Days Stored':>11} Status")
    print("  " + "-" * 46)
    for item, days in alerts:
        print(f"  {item['item_id']:<6} {item['device_name']:<20} "
              f"{days:>11}  {item['status']}")


# ══════════════════════════════════════════════════════════
# 10. GENERATE REPORT
# ══════════════════════════════════════════════════════════

def generate_report():
    """Aggregate statistics and write a summary report to report.txt."""
    today = datetime.date.today()
 
    total_wt = _total_weight()
    total_fee = sum(
        i["weight_kg"] * i["fee_per_kg"] for i in ewaste_inventory
    )
    n_items = len(ewaste_inventory)
    n_recycled = sum(1 for i in ewaste_inventory if i["status"] == "Recycled")
    n_hazard = sum(1 for i in ewaste_inventory if i["category"] == "Hazardous")
    storage_pct = (total_wt / STORAGE_LIMIT) * 100
    

    lines = [
        "=" * 60,
        "  GREEN LANTERN CORPS RECYCLERS — AEWMS Summary Report",
        f"  Generated : {today}",
        "=" * 60,
        f"  Total Items Recorded   : {n_items}",
        f"  Total Weight Collected : {total_wt:.2f} kg",
        f"  Total Recycling Fees   : Rs. {total_fee:,.2f}",
        f"  Items Recycled         : {n_recycled}",
        f"  Hazardous Items        : {n_hazard}",
        f"  Storage Utilisation    : {storage_pct:.1f}%",
        "=" * 60,
    ]
    report_text = "\n".join(lines)
    print("\n" + report_text)
    with open("report.txt", "w", encoding="utf-8") as fh:
        fh.write(report_text + "\n")
    print("  [OK] Report saved → report.txt")


# ══════════════════════════════════════════════════════════
# 11. MAIN MENU
# ══════════════════════════════════════════════════════════

def main_menu():
    """Entry point: display menu and route user selection to functions."""
    MENU = """
╔══════════════════════════════════════════════════════╗
║   GREEN LANTERN CORPS — E-Waste Management System   ║
╠══════════════════════════════════════════════════════╣
║  [1]  Display All E-Waste Items                     ║
║  [2]  Add New E-Waste Item                          ║
║  [3]  Update Item Weight                            ║
║  [4]  Delete / Mark Item                            ║
║  [5]  Calculate Recycling Fee                       ║
║  [6]  Search Items                                  ║
║  [7]  Sort Items                                    ║
║  [8]  Check Storage Capacity                        ║
║  [9]  Hazard Alert                                  ║
║  [10] Generate Report                               ║
║  [0]  Exit (auto-saves report)                      ║
╚══════════════════════════════════════════════════════╝"""

    HANDLERS = {
        "1": display_items,
        "2": add_item,
        "3": update_item,
        "4": delete_item,
        "5": calculate_fee,
        "6": search_items,
        "7": sort_items,
        "8": check_storage,
        "9": hazard_alert,
        "10": generate_report,
    }

    print(MENU)
    while True:
        choice = input("\n  Select option [0-10]: ").strip()
        if choice == "0":
            generate_report()
            print("  Goodbye! All records saved.")
            break
        elif choice in HANDLERS:
            HANDLERS[choice]()
        else:
            print("  [Error] Invalid option. Enter a number from 0 to 10.")


# ── Entry point ───────────────────────────────────────────
if __name__ == "__main__":
    main_menu()
