"""Creates realistic sample CSVs in ./data so the pipeline runs end to end.
Replace these CSVs with your own export later; keep the same column names."""
import csv, random, datetime as dt
random.seed(42)

cities = ["Hyderabad", "Bengaluru", "Chennai", "Mumbai", "Delhi", "Pune", "Vijayawada"]
cats = {"Electronics": (1500, 40000), "Fashion": (300, 4000), "Home": (400, 8000), "Books": (100, 900), "Beauty": (150, 2500)}

def write(name, header, rows):
    with open(f"data/{name}.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)

customers = [(i, f"Customer {i}", random.choice(cities),
              (dt.date(2024, 1, 1) + dt.timedelta(days=random.randint(0, 300))).isoformat())
             for i in range(1, 201)]
products = []
for i in range(1, 61):
    cat = random.choice(list(cats)); lo, hi = cats[cat]
    price = round(random.uniform(lo, hi), 2)
    products.append((i, f"{cat} Item {i}", cat, price, round(price * random.uniform(0.55, 0.85), 2)))

orders, items, payments = [], [], []
oi = pid = 1
start = dt.date(2025, 1, 1)
for oid in range(1, 3001):
    d = start + dt.timedelta(days=random.randint(0, 364))
    status = random.choices(["completed", "cancelled", "returned"], [88, 7, 5])[0]
    orders.append((oid, random.randint(1, 200), d.isoformat(), status))
    total = 0
    for _ in range(random.randint(1, 3)):
        p = random.choice(products); q = random.randint(1, 3)
        items.append((oi, oid, p[0], q)); oi += 1; total += q * p[3]
    payments.append((pid, oid, random.choice(["UPI", "Card", "NetBanking", "COD", "Wallet"]),
                     round(total, 2), d.isoformat())); pid += 1

# Deliberate dirty rows so the validation step has something real to catch
orders.append((3001, 9999, "2025-06-01", "completed"))        # unknown customer
items.append((oi, 3001, 1, 1))
orders.append((3002, 5, "2025-07-15", "completed"))
items.append((oi + 1, 3002, 2, -2))                            # negative quantity
orders.append((1, 7, "2025-03-03", "completed"))               # duplicate order_id

write("customers", ["customer_id", "customer_name", "city", "signup_date"], customers)
write("products", ["product_id", "product_name", "category", "unit_price", "unit_cost"], products)
write("orders", ["order_id", "customer_id", "order_date", "status"], orders)
write("order_items", ["order_item_id", "order_id", "product_id", "quantity"], items)
write("payments", ["payment_id", "order_id", "method", "amount", "paid_date"], payments)
print("Sample data written to ./data")
