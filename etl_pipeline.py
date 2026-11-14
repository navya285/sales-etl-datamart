"""
Sales ETL pipeline: CSV -> validate/clean -> SQLite -> datamart -> dashboard CSVs.

Run:  python generate_sample_data.py   (only if you have no CSVs yet)
      python etl_pipeline.py
"""
import sqlite3, logging
from pathlib import Path
import pandas as pd

BASE = Path(__file__).parent
DB = BASE / "sales.db"
OUT = BASE / "dashboard_exports"
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("etl")


def extract():
    names = ["customers", "products", "orders", "order_items", "payments"]
    data = {n: pd.read_csv(BASE / "data" / f"{n}.csv") for n in names}
    for n, df in data.items():
        log.info("Extracted %-12s %6d rows", n, len(df))
    return data


def transform(data):
    """Data-quality checks. Bad rows are removed AND written to a rejects file."""
    rejects = []

    def reject(df, mask, reason, table):
        bad = df[mask].copy()
        if len(bad):
            bad["table"], bad["reason"] = table, reason
            rejects.append(bad)
            log.warning("%s: rejected %d rows (%s)", table, len(bad), reason)
        return df[~mask]

    c, p, o, oi, pay = (data[k] for k in ["customers", "products", "orders", "order_items", "payments"])

    o = reject(o, o.duplicated("order_id", keep="first"), "duplicate order_id", "orders")
    o = reject(o, ~o["customer_id"].isin(c["customer_id"]), "unknown customer_id", "orders")
    o["order_date"] = pd.to_datetime(o["order_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    o = reject(o, o["order_date"].isna(), "invalid order_date", "orders")

    oi = reject(oi, oi["quantity"] <= 0, "non-positive quantity", "order_items")
    oi = reject(oi, ~oi["order_id"].isin(o["order_id"]), "orphan order_id", "order_items")
    oi = reject(oi, ~oi["product_id"].isin(p["product_id"]), "unknown product_id", "order_items")

    pay = reject(pay, ~pay["order_id"].isin(o["order_id"]), "orphan order_id", "payments")
    pay = reject(pay, pay["amount"] < 0, "negative amount", "payments")

    OUT.mkdir(exist_ok=True)
    if rejects:
        pd.concat(rejects).to_csv(OUT / "rejected_rows.csv", index=False)
    clean = dict(customers=c, products=p, orders=o, order_items=oi, payments=pay)
    return clean


def load(clean):
    with sqlite3.connect(DB) as con:
        con.executescript((BASE / "sql" / "schema.sql").read_text())
        for name, df in clean.items():
            df.to_sql(name, con, if_exists="append", index=False)
            log.info("Loaded    %-12s %6d rows", name, len(df))
        con.executescript((BASE / "sql" / "datamart.sql").read_text())
        log.info("Datamart tables built")


def reconcile():
    """Simple control check: datamart revenue must equal revenue from source tables."""
    with sqlite3.connect(DB) as con:
        dm = con.execute("SELECT ROUND(SUM(revenue),2) FROM dm_daily_sales").fetchone()[0]
        src = con.execute("""SELECT ROUND(SUM(oi.quantity*p.unit_price),2)
                             FROM orders o JOIN order_items oi USING(order_id)
                             JOIN products p USING(product_id)
                             WHERE o.status='completed'""").fetchone()[0]
    ok = abs(dm - src) < 0.01
    log.info("Reconciliation datamart=%s source=%s -> %s", dm, src, "PASS" if ok else "FAIL")
    if not ok:
        raise SystemExit("Reconciliation failed")


def export_for_dashboard():
    OUT.mkdir(exist_ok=True)
    with sqlite3.connect(DB) as con:
        for t in ["dm_daily_sales", "dm_category_sales", "dm_customer_ltv", "dm_payment_mix"]:
            pd.read_sql(f"SELECT * FROM {t}", con).to_csv(OUT / f"{t}.csv", index=False)
    log.info("Dashboard CSVs written to %s", OUT)


if __name__ == "__main__":
    clean = transform(extract())
    load(clean)
    reconcile()
    export_for_dashboard()
    log.info("Pipeline finished")
