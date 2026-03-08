import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import google.generativeai as genai
import io

# ==========================================
#  Gemini API Key
# ==========================================
GEMINI_API_KEY = "AIzaSyDNM0NB1RHHo78_slFRkkXgVCV-WERsbJw" 
# ==========================================

# 设置页面配置，优化 iPad 横屏显示效果
st.set_page_config(page_title="AI 数据分析助手", layout="wide")

# 初始化 Gemini 模型
def init_gemini():
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel('gemini-1.5-flash')

st.title("📊 专用 AI 数据分析工具")
st.caption("上传 Excel 文件，由 Gemini AI 自动生成深度分析报告")

# 侧边栏仅保留文件上传功能
with st.sidebar:
    st.header("操作面板")
    uploaded_file = st.file_uploader("第一步：上传 Excel 文件", type=["xlsx", "xls"])
    st.info("提示：上传成功后，点击下方的分析按钮。")

if uploaded_file:
    # 1. 读取数据
    try:
        df = pd.read_excel(uploaded_file)
        st.subheader("📋 数据预览 (前 5 行)")
        st.dataframe(df.head(), use_container_width=True)

        # 2. 准备发送给 AI 的数据摘要
        buffer = io.StringIO()
        df.info(buf=buffer)
        info_str = buffer.getvalue()
        summary_stats = df.describe(include='all').to_string()

        # 3. AI 分析触发器
        if st.button("🚀 开始 AI 深度分析报告", type="primary"):
            model = init_gemini()
            
            # 编写面向同事风格的 Prompt
            prompt = f"""
            你是一位资深数据分析专家。请根据以下提供的 Excel 数据摘要进行深度分析。
            
            【数据结构信息】:
            {info_str}
            
            【统计学指标摘要】:
            {summary_stats}
            
            请输出一份专业的中文报告，包含以下内容：
            1. 核心结论：用一句话概括数据反映的现状。
            2. 关键发现：列出 3 个值得关注的趋势或异常点。
            3. 行动建议：基于数据，给出 2 条可落地的业务建议。
            4. 绘图建议：说明哪些字段适合做可视化展示（如柱状图、散点图）。
            """
            
            with st.spinner('AI 正在全力分析中，请稍候...'):
                try:
                    response = model.generate_content(prompt)
                    st.markdown("---")
                    st.success("✅ 分析报告生成完毕")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"AI 接口调用失败：{str(e)}")

        # 4. 自动化可视化展示
        st.markdown("---")
        st.subheader("📈 数据可视化预览")
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        if numeric_cols:
            col1, col2 = st.columns(2)
            with col1:
                selected_col = st.selectbox("选择分析字段", numeric_cols)
            with col2:
                chart_type = st.radio("选择图表类型", ["折线图", "柱状图"], horizontal=True)

            fig, ax = plt.subplots(figsize=(10, 5))
            # 解决 Matplotlib 中文显示问题（macOS 常用字体）
            plt.rcParams['font.sans-serif'] = ['Arial Unicode MS'] 
            
            if chart_type == "折线图":
                ax.plot(df[selected_col], marker='o', linestyle='-', color='#007bff')
            else:
                ax.bar(df.index, df[selected_col], color='#28a745')
                
            ax.set_title(f"{selected_col} 数据分布", fontsize=14)
            ax.set_xlabel("样本序号")
            ax.set_ylabel("数值")
            st.pyplot(fig)
        else:
            st.warning("未在文件中检测到数值型列，无法生成图表。")

    except Exception as e:
        st.error(f"文件读取错误：{str(e)}")
else:
    st.info("👋 请在左侧上传 Excel 文件开始工作。")
