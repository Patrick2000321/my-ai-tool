import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import google.generativeai as genai
import io

# 设置页面配置
st.set_page_config(page_title="AI 数据分析助手", layout="wide")

# 配置 Gemini API (建议通过 Secrets 管理)
def init_gemini(api_key):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')

# 界面标题
st.title("📊 AI 数据分析与报告生成器")

# 侧边栏配置
with st.sidebar:
    st.header("配置")
    api_key = st.text_input("输入 Gemini API Key", type="password")
    uploaded_file = st.file_uploader("上传 Excel 文件", type=["xlsx", "xls"])

if uploaded_file and api_key:
    # 1. 读取数据
    df = pd.read_excel(uploaded_file)
    st.subheader("数据预览")
    st.dataframe(df.head())

    # 2. 生成基础统计摘要
    buffer = io.StringIO()
    df.info(buf=buffer)
    info_str = buffer.getvalue()
    summary_stats = df.describe(include='all').to_string()

    # 3. AI 分析逻辑
    if st.button("开始 AI 深度分析"):
        model = init_gemini(api_key)
        
        prompt = f"""
        你是一位专业的数据分析师。请分析以下数据集并提供报告：
        
        【数据集结构】:
        {info_str}
        
        【统计摘要】:
        {summary_stats}
        
        请完成以下任务：
        1. 用中文总结数据的主要特征和潜在规律。
        2. 识别数据中的 2-3 个关键洞察（Insights）。
        3. 建议适合该数据的 2 个图表类型。
        """
        
        with st.spinner('AI 正在思考中...'):
            response = model.generate_content(prompt)
            st.markdown("---")
            st.subheader("🤖 AI 自动分析报告")
            st.write(response.text)

    # 4. 指定图表绘制 (示例：数值型列的趋势)
    st.subheader("趋势分析图表")
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    if numeric_cols:
        selected_col = st.selectbox("选择要查看趋势的字段", numeric_cols)
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(df[selected_col])
        ax.set_title(f"{selected_col} 趋势图")
        st.pyplot(fig)
else:
    st.info("请在左侧侧边栏上传文件并配置 API Key 以开始。")