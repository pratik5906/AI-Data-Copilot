import ollama

MODEL_NAME = "phi3"   # 🔥 Fast model


def generate_pandas_code(query, columns):

    prompt = f"""
You are a data analyst.

A pandas DataFrame named df exists.

Columns:
{columns}

Write ONLY valid pandas code.
Store final output in variable named result.
No explanation.

User Question:
{query}
"""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{"role": "system", "content": prompt}]
    )

    return response["message"]["content"].strip()


def explain_result(query, result):

    prompt = f"""
Question:
{query}

Result:
{result}

Explain clearly and briefly.
"""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{"role": "system", "content": prompt}]
    )

    return response["message"]["content"]