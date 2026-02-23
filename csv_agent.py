import streamlit as st
import pandas as pd
from llm_engine import generate_pandas_code, explain_result

class CSVChatbot:

    def __init__(self, df):
        self.df = df

    def answer_query(self, query):

        code = generate_pandas_code(query, list(self.df.columns))

        try:
            result = eval(code, {"df": self.df})

            # Number result
            if isinstance(result, (int, float)):
                st.success(result)

            # Series result
            elif isinstance(result, pd.Series):
                st.dataframe(result)
                st.bar_chart(result)

            # DataFrame result
            elif isinstance(result, pd.DataFrame):
                st.dataframe(result)
                numeric_cols = result.select_dtypes(include='number')
                if not numeric_cols.empty:
                    st.bar_chart(numeric_cols)

            else:
                st.write(result)

            # ✅ Explanation inside function
            explanation = explain_result(query, result)
            st.info(explanation)

        except Exception as e:
            st.error(f"Execution Error: {e}")