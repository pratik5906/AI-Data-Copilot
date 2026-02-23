import pandas as pd

def process_query(df, query):
    query = query.lower()

    # TOTAL SALES
    if "total" in query and "sale" in query:
        total = df["Sales"].sum()
        return {
            "type": "metric",
            "value": total,
            "message": f"Total sales across dataset: {total:,}"
        }

    # REGION SALES
    if "region" in query or "north" in query or "south" in query or "east" in query or "west" in query:
        region_sales = df.groupby("Region")["Sales"].sum().reset_index()
        return {
            "type": "table",
            "value": region_sales,
            "message": "Here are total sales by region."
        }

    # PROFIT
    if "profit" in query:
        total_profit = df["Profit"].sum()
        return {
            "type": "metric",
            "value": total_profit,
            "message": f"Total profit: {total_profit:,}"
        }

    return {
        "type": "error",
        "message": "Query not recognized yet."
    }