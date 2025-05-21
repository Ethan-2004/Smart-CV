import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, date
import Component as co
import random  # 模拟评分与分析结果
import io

def display_analysis(phonenumber):
    st.title("📊 简历分析中心")



    resumes = co.get_user_resumes(phonenumber)
    # st.write(resumes)
    if not resumes:
        st.info("暂无简历，请上传。")
        return

    # 简历选择
    resume_dict = {row[1]: row[0] for row in resumes}
    resume_name = st.selectbox("请选择要分析的简历", list(resume_dict.keys()))
    resume_id = resume_dict[resume_name]

    st.markdown("---")

    # 日期筛选
    with st.expander("📅 分析记录筛选（按日期）", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("开始日期", value=date(2024, 1, 1))
        with col2:
            end_date = st.date_input("结束日期", value=date.today())

    # 获取记录
    records = co.get_resume_analysis(
        resume_id=resume_id,
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d")
    )

    df = pd.DataFrame(records, columns=["ID", "分数", "分析时间", "结果", "状态"])

    if df.empty:
        st.info("该简历在所选时间段内暂无分析记录。")
    else:
        st.subheader("📄 分析记录")
        st.dataframe(df, use_container_width=True)

        # 导出
        export_format = st.radio("导出格式", ["CSV", "Excel"], horizontal=True)
        if st.button("📤 导出分析记录"):
            if export_format == "CSV":
                st.download_button("点击下载 CSV 文件", df.to_csv(index=False).encode('utf-8'), file_name="analysis.csv")
            else:
                towrite = io.BytesIO()
                df.to_excel(towrite, index=False, engine='openpyxl')
                towrite.seek(0)
                st.download_button("点击下载 Excel 文件", towrite, file_name="analysis.xlsx")

        # 图表
        import matplotlib.pyplot as plt
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体为黑体
        plt.rcParams['axes.unicode_minus'] = False   
        
        st.subheader("🎯 分数分布图")
        plt.figure(figsize=(8, 4))
        sns.histplot(df["分数"], kde=True, bins=10, color="skyblue")
        plt.xlabel("分析分数")
        st.pyplot(plt)

        st.subheader("📈 分析趋势图")
        df["分析时间"] = pd.to_datetime(df["分析时间"])
        df_sorted = df.sort_values("分析时间")
        plt.figure(figsize=(8, 4))
        sns.lineplot(data=df_sorted, x="分析时间", y="分数", marker="o", color="orange")
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(plt)

    # 删除记录
    with st.expander("🗑️ 删除分析记录"):
        if not df.empty:
            del_id = st.selectbox("选择要删除的记录 ID", df["ID"])
            if st.button("确认删除记录"):
                co.delete_analysis(del_id)
                st.success("删除成功")
                st.rerun()

    # 模拟生成分析记录
    st.markdown("---")
    st.subheader("🚀 模拟分析简历")
    if st.button("开始分析当前简历"):
        fake_score = random.randint(60, 95)
        fake_outcome = "简历内容完整度高，符合岗位要求。" if fake_score > 80 else "建议优化项目经历与技能描述。"
        co.insert_analysis(phonenumber, resume_id, fake_score, fake_outcome)
        st.success("分析完成并保存！")
        st.rerun()
