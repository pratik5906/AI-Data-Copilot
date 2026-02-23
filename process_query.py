import pandas as pd

def process_query(df, query):
    query = query.lower()

    # -------- TOTAL SALES --------
    if "total" in query and "sale" in query:
        total = df["Sales"].sum()
        return {
            "type": "metric",
            "message": f"Total sales: {total:,}"
        }

    # -------- REGION SPECIFIC SALES --------
    if "sale" in query:
        for region in df["Region"].unique():
            if region.lower() in query:
                total = df[df["Region"] == region]["Sales"].sum()
                return {
                    "type": "metric",
                    "message": f"Total sales in {region}: {total:,}"
                }

    # -------- PROFIT --------
    if "profit" in query:
        total_profit = df["Profit"].sum()
        return {
            "type": "metric",
            "message": f"Total profit: {total_profit:,}"
        }

    return {
        "type": "error",
        "message": "Query not recognized."
    }