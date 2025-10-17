import os
import pandas as pd
import random
from datetime import datetime, timedelta

OUT_DIR = "data/dummy_invoices"
os.makedirs(OUT_DIR, exist_ok=True)

categories = ['Rent', 'Utilities', 'Supplies', 'Internet', 'Maintenance']
vendors = ['ABC Pvt Ltd', 'XYZ Corp', 'Alpha Services', 'Delta Power', 'QuickFix Solutions']

rows = []
for i in range(100):
    inv_id = f"INV{i+1:04d}"
    vendor = random.choice(vendors)
    category = random.choice(categories)
    amount = random.randint(500, 15000)
    date = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d")
    text = (
        f"Invoice ID: {inv_id}\n"
        f"Vendor: {vendor}\n"
        f"Date: {date}\n"
        f"Description: This invoice is for {category} related charges. Total payable amount: INR {amount}.\n"
        f"Account No: ****{random.randint(1000,9999)}"
    )
    filename = os.path.join(OUT_DIR, f"{inv_id}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    rows.append({
        "invoice_id": inv_id,
        "file_name": f"{inv_id}.txt",
        "vendor": vendor,
        "date": date,
        "amount": amount,
        "category": category,
        "text": text
    })

df = pd.DataFrame(rows)
df.to_csv("data/labels.csv", index=False)
print("Generated", len(rows), "dummy invoices at", OUT_DIR)
