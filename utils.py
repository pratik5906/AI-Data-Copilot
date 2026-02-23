import pandas as pd

ALLOWED_METHODS = [
    "sum", "mean", "max", "min",
    "count", "groupby", "head",
    "tail", "describe", "value_counts"
]

def safe_execute(df, code):
    if any(word in code for word in ["import", "exec", "eval", "__"]):
        return "Unsafe operation detected."

    try:
        result = eval(code, {"df": df})
        return str(result)
    except Exception as e:
        return f"Execution Error: {e}"