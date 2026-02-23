import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import ollama
import re
from report_generator import generate_pdf

st.set_page_config(page_title="AI Data Copilot", layout="wide")

# ---------------- BACKGROUND ---------------- #

def set_bg(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.90)),
                    url("data:image/jpg;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    section[data-testid="stSidebar"] {{
        background: rgba(10,10,25,0.95);
    }}
    .title {{
        font-size: 42px;
        font-weight: 700;
        background: linear-gradient(90deg,#00F5A0,#00D9F5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    </style>
    """, unsafe_allow_html=True)

set_bg("background.jpg")

# ---------------- SIDEBAR ---------------- #

st.sidebar.title("📂 Upload CSV Files")

uploaded_files = st.sidebar.file_uploader(
    "Upload one or more CSV files",
    type=["csv"],
    accept_multiple_files=True
)

st.sidebar.markdown("---")
st.sidebar.markdown("🚀 Powered by Phi3")

# ---------------- TITLE ---------------- #

st.markdown("<div class='title'>AI Data Copilot</div>", unsafe_allow_html=True)
st.write("Universal AI + Smart Visualization Platform")

# =====================================================

if uploaded_files:

    # -------- MERGE FILES -------- #

    dfs = []
    for file in uploaded_files:
        df_temp = pd.read_csv(file)
        df_temp["Source_File"] = file.name
        dfs.append(df_temp)

    df = pd.concat(dfs, ignore_index=True)

    # -------- TABS -------- #

    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📈 Data Visualization", "🤖 AI Chat"])

    # =====================================================
    # 📊 DASHBOARD TAB
    # =====================================================

    with tab1:

        st.subheader("Dataset Preview")
        st.dataframe(df, use_container_width=True)

        col1, col2 = st.columns(2)
        col1.metric("Rows", df.shape[0])
        col2.metric("Columns", df.shape[1])

        numeric_cols = df.select_dtypes(include="number").columns
        if len(numeric_cols) > 0:
            st.metric("Total Numeric Sum", int(df[numeric_cols].sum().sum()))

    # =====================================================
    # 📈 VISUALIZATION TAB
    # =====================================================

    with tab2:

        st.subheader("Smart Visualization Builder")

        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        categorical_cols = df.select_dtypes(include="object").columns.tolist()

        chart_type = st.selectbox(
            "Select Chart Type",
            ["Bar Chart", "Line Chart", "Pie Chart", "Histogram", "Scatter Plot"]
        )

        if chart_type in ["Bar Chart", "Line Chart"]:
            x_axis = st.selectbox("Select X Axis", df.columns)
            y_axis = st.selectbox("Select Y Axis", numeric_cols)

            if chart_type == "Bar Chart":
                fig = px.bar(df, x=x_axis, y=y_axis)
            else:
                fig = px.line(df, x=x_axis, y=y_axis)

            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Pie Chart":
            cat_col = st.selectbox("Select Category Column", categorical_cols)
            fig = px.pie(df, names=cat_col)
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Histogram":
            num_col = st.selectbox("Select Numeric Column", numeric_cols)
            fig = px.histogram(df, x=num_col)
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Scatter Plot":
            x_axis = st.selectbox("Select X Axis", numeric_cols)
            y_axis = st.selectbox("Select Y Axis", numeric_cols)
            fig = px.scatter(df, x=x_axis, y=y_axis)
            st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # 🤖 AI CHAT TAB
    # =====================================================

    with tab3:

        st.subheader("AI Data Copilot")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        if "last_result" not in st.session_state:
            st.session_state.last_result = None

        user_input = st.chat_input("Ask anything about your dataset...")

        if user_input:

            st.session_state.messages.append(
                {"role": "user", "content": user_input}
            )

            prompt = f"""
You are a data analyst.

A pandas DataFrame named df exists.

Columns:
{df.columns.tolist()}

Return ONLY one line pandas code.
Store final output in variable named result.
No explanation.
No markdown.
"""

            response = ollama.chat(
                model="phi3",
                messages=[{"role": "user", "content": prompt + "\nQuestion: " + user_input}]
            )

            generated_code = response["message"]["content"].strip()

            generated_code = re.sub(r"```.*?\n", "", generated_code)
            generated_code = generated_code.replace("```", "").strip()

            if not generated_code.startswith("result"):
                generated_code = "result = " + generated_code

            try:
                local_vars = {"df": df}
                exec(generated_code, {}, local_vars)
                result = local_vars.get("result", None)
                st.session_state.last_result = result
                final_answer = "Here is your result 👇"
            except:
                final_answer = "⚠️ Could not process that query."
                st.session_state.last_result = None

            st.session_state.messages.append(
                {"role": "assistant", "content": final_answer}
            )

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        result = st.session_state.last_result

        if isinstance(result, pd.DataFrame):
            st.dataframe(result)
        elif isinstance(result, (int, float)):
            st.metric("Result", f"{result:,}")
        elif result is not None:
            st.write(result)

    # =====================================================
    # 📄 REPORT
    # =====================================================

    st.markdown("---")
    if st.button("Generate AI PDF Report"):

        summary_text = df.describe().to_string()

        response = ollama.chat(
            model="phi3",
            messages=[
                {"role": "system", "content": "Create a professional business data report."},
                {"role": "user", "content": summary_text}
            ]
        )

        report_text = response["message"]["content"]

        generate_pdf("report.pdf", report_text)

        with open("report.pdf", "rb") as f:
            st.download_button("Download Report", f, file_name="AI_Report.pdf")

else:
    st.info("⬅ Upload CSV files from sidebar to begin.")

st.markdown("""
<style>

.footer-container {
    margin-top: 80px;
    padding: 40px 20px;
    text-align: center;
    width: 100%;
    border-radius: 0px;
    background: linear-gradient(90deg, rgba(0,245,160,0.1), rgba(0,217,245,0.1));
    border-top: 1px solid rgba(255,255,255,0.1);
    backdrop-filter: blur(10px);
}

.footer-title {
    font-size: 20px;
    font-weight: 600;
    background: linear-gradient(90deg,#00F5A0,#00D9F5);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: glow 2s ease-in-out infinite alternate;
}

.footer-text {
    color: rgba(255,255,255,0.6);
    font-size: 14px;
    margin-top: 10px;
}

.footer-links a {
    color: #00F5A0;
    margin: 0 15px;
    text-decoration: none;
    font-size: 14px;
    transition: 0.3s;
}

.footer-links a:hover {
    color: #00D9F5;
    text-shadow: 0 0 10px #00F5A0;
}

@keyframes glow {
    from { text-shadow: 0 0 5px #00F5A0; }
    to { text-shadow: 0 0 20px #00D9F5; }
}

</style>

<div class="footer-container">

<div class="footer-title">
🚀 AI Data Copilot
</div>

<div class="footer-text">
© 2026 Pratik Kumar • Founder & Developer  
Built with ❤️ using Streamlit + Local AI (Ollama)
</div>

<div class="footer-links">
<a href="https://www.linkedin.com/" target="_blank">LinkedIn</a>
<a href="https://github.com/" target="_blank">GitHub</a>
</div>

</div>
""", unsafe_allow_html=True)
st.markdown("""
<style>
div[data-testid="stChatInput"] {
    border: 1px solid rgba(0,245,160,0.3);
    border-radius: 30px;
    transition: 0.3s;
}
div[data-testid="stChatInput"]:focus-within {
    box-shadow: 0 0 20px rgba(0,245,160,0.6);
    border: 1px solid #00F5A0;
}
</style>
""", unsafe_allow_html=True)