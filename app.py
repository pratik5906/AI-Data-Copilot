import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import ollama
import re
import os
from datetime import datetime
from report_generator import generate_pdf

st.set_page_config(page_title="AI Data Copilot", layout="wide")

# ================= BACKGROUND ================= #

def set_bg(image_file):
    if not os.path.exists(image_file):
        return
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.88), rgba(0,0,0,0.92)),
                    url("data:image/jpg;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    </style>
    """, unsafe_allow_html=True)

set_bg("background.jpg")

# ================= SIDEBAR ================= #

st.sidebar.title("📂 Upload CSV Files")

uploaded_files = st.sidebar.file_uploader(
    "Upload one or more CSV files",
    type=["csv"],
    accept_multiple_files=True
)

st.sidebar.markdown("---")
st.sidebar.markdown("🚀 Powered by Phi3 (Fast Local AI)")

st.markdown("<h1 style='color:#00F5A0;'>AI Data Copilot</h1>", unsafe_allow_html=True)
st.write("Universal AI + Smart Visualization Platform")

# =====================================================

if uploaded_files:

    dfs = []
    for file in uploaded_files:
        temp_df = pd.read_csv(file)
        temp_df["Source_File"] = file.name
        dfs.append(temp_df)

    df = pd.concat(dfs, ignore_index=True)

    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📈 Visualization", "🤖 AI Chat"])

    # ================= DASHBOARD ================= #

    with tab1:
        st.subheader("Dataset Preview")
        st.dataframe(df, use_container_width=True)

        c1, c2 = st.columns(2)
        c1.metric("Rows", df.shape[0])
        c2.metric("Columns", df.shape[1])

    # ================= VISUALIZATION ================= #

    with tab2:
        st.subheader("Smart Visualization Builder")

        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        categorical_cols = df.select_dtypes(include="object").columns.tolist()

        chart_type = st.selectbox(
            "Select Chart Type",
            ["Bar", "Line", "Pie", "Histogram", "Scatter"]
        )

        if chart_type in ["Bar", "Line"] and numeric_cols:
            x = st.selectbox("X Axis", df.columns)
            y = st.selectbox("Y Axis", numeric_cols)
            fig = px.bar(df, x=x, y=y) if chart_type == "Bar" else px.line(df, x=x, y=y)
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Pie" and categorical_cols:
            cat = st.selectbox("Category Column", categorical_cols)
            fig = px.pie(df, names=cat)
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Histogram" and numeric_cols:
            num = st.selectbox("Numeric Column", numeric_cols)
            fig = px.histogram(df, x=num)
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Scatter" and numeric_cols:
            x = st.selectbox("X Axis", numeric_cols)
            y = st.selectbox("Y Axis", numeric_cols)
            fig = px.scatter(df, x=x, y=y)
            st.plotly_chart(fig, use_container_width=True)

    # ================= AI CHAT ================= #

    with tab3:

        st.subheader("AI Data Copilot")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        # -------- DISPLAY CHAT -------- #

        for msg in st.session_state.messages:

            align = "flex-end" if msg["role"] == "user" else "flex-start"
            bg = "#25D366" if msg["role"] == "user" else "#1e1e1e"
            color = "black" if msg["role"] == "user" else "white"

            st.markdown(f"""
            <div style='display:flex; justify-content:{align}; margin-bottom:10px;'>
                <div style='background:{bg}; color:{color};
                            padding:10px 15px; border-radius:15px;
                            max-width:65%; font-size:14px;'>
                    {msg["content"]}
                    <div style='font-size:10px; opacity:0.6; margin-top:5px; text-align:right;'>
                        {msg["time"]}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # SHOW RESULT BELOW MESSAGE
            if msg.get("result") is not None:
                result = msg["result"]

                if isinstance(result, pd.DataFrame):
                    st.dataframe(result)

                    if result.shape[1] == 2:
                        fig = px.bar(result,
                                     x=result.columns[0],
                                     y=result.columns[1])
                        st.plotly_chart(fig,
                                        use_container_width=True,
                                        key=str(msg["time"]))

                elif isinstance(result, pd.Series):
                    st.dataframe(result)

                elif isinstance(result, (int, float)):
                    st.metric("Result", f"{result:,}")

        # -------- INPUT -------- #

        user_input = st.chat_input("Type a message...")

        if user_input:

            timestamp = datetime.now().strftime("%H:%M:%S")

            # USER MESSAGE
            st.session_state.messages.append({
                "role": "user",
                "content": user_input,
                "time": timestamp,
                "result": None
            })

            # TYPING MESSAGE
            st.session_state.messages.append({
                "role": "assistant",
                "content": "🤖 AI is analyzing your data...",
                "time": datetime.now().strftime("%H:%M:%S"),
                "result": None
            })

            st.rerun()

        # -------- PROCESS TYPING -------- #

        if st.session_state.messages and \
           st.session_state.messages[-1]["content"] == "🤖 AI is analyzing your data...":

            user_msg = st.session_state.messages[-2]["content"]

            prompt = f"""
You are an expert pandas data analyst.

DataFrame name: df

Available columns EXACTLY:
{", ".join(df.columns)}

STRICT RULES:
- Only ONE line
- Must start with: result =
- Use only provided columns exactly
- No explanation
- No markdown
- No import
"""

            try:
                response = ollama.chat(
                    model="phi3",
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": user_msg}
                    ]
                )

                code = response["message"]["content"].strip()
                code = re.sub(r"```.*?```", "", code, flags=re.DOTALL)
                code = code.replace("\n", "").strip()

                if not code.startswith("result"):
                    code = "result = " + code

                local_vars = {"df": df}
                exec(code, {}, local_vars)

                result = local_vars.get("result", None)
                reply = "Here is your result 👇"

            except Exception as e:
                result = None
                reply = f"⚠️ Error: {e}"

            # Replace typing message
            st.session_state.messages[-1] = {
                "role": "assistant",
                "content": reply,
                "time": datetime.now().strftime("%H:%M:%S"),
                "result": result
            }

            st.rerun()

    # ================= PDF ================= #

    st.markdown("---")
    if st.button("Generate AI PDF Report"):

        summary_text = df.describe().to_string()

        response = ollama.chat(
            model="phi3",
            messages=[
                {"role": "system", "content": "Create professional business data report."},
                {"role": "user", "content": summary_text}
            ]
        )

        report_text = response["message"]["content"]
        generate_pdf("report.pdf", report_text)

        with open("report.pdf", "rb") as f:
            st.download_button("Download Report", f, file_name="AI_Report.pdf")

else:
    st.info("⬅ Upload CSV files from sidebar to begin.")

# ================= FOOTER ================= #

st.markdown("""
<hr>
<center style='color:rgba(255,255,255,0.6); margin-top:40px;'>
🚀 <b>AI Data Copilot</b><br>
© 2026 Pratik Kumar • Founder & Developer<br>
Built with ❤️ using Streamlit + Local AI (Ollama)
</center>
""", unsafe_allow_html=True)