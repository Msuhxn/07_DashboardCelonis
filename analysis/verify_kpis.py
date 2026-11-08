"""
Recompute the Celonis results of Group 07 from the raw data files.

The script checks the numbers shown in the dashboards and slides:
  Part 1  pizza log: cases, variants, most common variant
  Part 2  orders: total cases, cancellation rate
  Part 3  orders: order-to-delivery throughput time
  Part 3  object-centric data: objects, events and the convergence example

Run from the repository root:
    pip install pandas openpyxl
    python analysis/verify_kpis.py
"""
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"


def part1_pizza():
    log = pd.read_csv(DATA / "pizza-log.csv", parse_dates=["time"])
    log = log.sort_values(["case", "time"])
    variants = log.groupby("case")["activity"].agg(" > ".join)
    counts = variants.value_counts()
    top = counts.iloc[0]
    print("Part 1: pizza log")
    print(f"  Cases:                  {variants.size:,}")
    print(f"  Variants:               {counts.size}")
    print(f"  Most common variant:    {top} cases ({top / variants.size:.0%})")
    ties = log.duplicated(["case", "time"]).sum()
    print(f"  Note: {ties} events share a timestamp with another event of the same case.")
    print("        The order of tied events decides the variant, so the variant count")
    print("        differs slightly from Celonis (111 variants, top variant 72 cases).")


def part2_and_3_orders():
    events = pd.read_excel(DATA / "table-10000-events.xlsx")
    cases = pd.read_excel(DATA / "table-10000-cases.xlsx")

    # Total Cases: COUNT("cases"."CASE")
    total = cases["case"].count()

    # Cancellation Rate:
    # 100 * SUM(CASE WHEN ACTIVITY = 'cancel order' THEN 1 ELSE 0 END) / COUNT(DISTINCT "events"."CASE")
    cancel = (events["activity"] == "cancel order").sum()
    rate = 100 * cancel / events["case"].nunique()

    # Order to Delivery:
    # AVG(CALC_THROUGHPUT(FIRST_OCCURRENCE['place order'] TO LAST_OCCURRENCE['make delivery'],
    #     REMAP_TIMESTAMPS("events"."START TIME", DAYS)))
    # REMAP_TIMESTAMPS(..., DAYS) works on whole calendar days, so dates are floored to the day.
    first_order = events[events["activity"] == "place order"].groupby("case")["start time"].min()
    last_delivery = events[events["activity"] == "make delivery"].groupby("case")["start time"].max()
    both = pd.concat([first_order, last_delivery], axis=1, keys=["start", "end"]).dropna()
    days_pql = (both["end"].dt.floor("D") - both["start"].dt.floor("D")).dt.days
    days_exact = (both["end"] - both["start"]).dt.total_seconds() / 86400

    print("\nPart 2: orders dashboard")
    print(f"  Total Cases:            {total:,}")
    print(f"  Cancellation Rate:      {rate:.2f}%")
    print("\nPart 3: throughput time, place order (first) to make delivery (last)")
    print(f"  Delivered orders:       {len(both):,}")
    print(f"  PQL KPI (whole days):   {days_pql.mean():.2f} days")
    print(f"  Exact average:          {days_exact.mean():.2f} days")
    print(f"  Median:                 {days_exact.median():.2f} days")
    print(f"  Min / max:              {days_exact.min():.2f} / {days_exact.max():.2f} days")


def part3_object_centric():
    ocpm = DATA / "ocpm"
    events = pd.read_csv(ocpm / "Events.csv")
    orders = pd.read_csv(ocpm / "OT_order.csv")
    items = pd.read_csv(ocpm / "OT_item.csv")
    packages = pd.read_csv(ocpm / "OT_package.csv")
    e2o_item = pd.read_csv(ocpm / "E2O_item.csv")
    e2o_pkg = pd.read_csv(ocpm / "E2O_package.csv")

    print("\nPart 3: object-centric data")
    print(f"  Events:                 {len(events):,} ({events['activity'].nunique()} activities)")
    print(f"  Objects:                {len(orders)} orders, {len(items)} items, {len(packages)} packages")

    # Convergence: with item as the case, every 'place order' event is copied once per item.
    place = set(events.loc[events["activity"] == "place order", "event"])
    copies = e2o_item["event"].isin(place).sum()
    print(f"  'place order' events:   {len(place)} real, {copies} if item is the case (convergence)")

    # Example order used on slide 31
    example = "ord990001"
    its = set(items.loc[items["order"] == example, "object"])
    evs = set(e2o_item.loc[e2o_item["object"].isin(its), "event"])
    pk = e2o_pkg.loc[e2o_pkg["event"].isin(evs), "object"].nunique()
    print(f"  Example {example}:      {len(its)} items in {pk} packages")


if __name__ == "__main__":
    part1_pizza()
    part2_and_3_orders()
    part3_object_centric()
