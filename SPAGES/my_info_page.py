import streamlit as st
import Component as co
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def myinfo_page(phonenumber,username):
    st.title("🏠 用户主页")

    if not username or not phonenumber:
        st.warning("请先登录。")
        return

    st.header(f"欢迎，{username}！")

    resumes = co.get_user_resumes(phonenumber)
    if resumes:
        st.subheader("📄 你的简历列表")
        df_resumes = pd.DataFrame(resumes, columns=["ID", "简历名称", "上传日期", "学校", "学历", "期望薪资", "年龄", "地区", "性别", "状态"])
        st.dataframe(df_resumes)
    else:
        st.info("你还没有上传任何简历。")

    analysis = co.get_resume_analysis_by_number(phonenumber)

    if analysis:
        st.subheader("📊 简历分析结果统计")

        df_analysis = pd.DataFrame(analysis, columns=[
            "简历名称", "职位名称",
            "分数", "分析时间", "结果", "状态"
        ])

        st.dataframe(df_analysis)

        import matplotlib.pyplot as plt
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体为黑体
        plt.rcParams['axes.unicode_minus'] = False   
        
        plt.figure(figsize=(8,4))
        sns.histplot(df_analysis['分数'], bins=10, kde=True, color='skyblue')
        plt.title("简历分析分数分布")
        plt.xlabel("分数")
        plt.ylabel("频数")
        st.pyplot(plt)

        latest = df_analysis.sort_values(by="分析时间", ascending=False).iloc[0]
        st.markdown(f"**最近一次分析时间:** {latest['分析时间']}")
        st.markdown(f"**分析分数:** {latest['分数']}")
        st.markdown(f"**分析结果:** {latest['结果']}")
    else:
        st.info("暂无简历分析数据。")

    st.write("---")
    st.subheader("💼 职位分类统计")
    page1,page2=st.columns([1,1])
    job_cat_count, total_jobs = co.get_jobs_summary()
    with page1:  
        if job_cat_count:
            
            df_jobs = pd.DataFrame(job_cat_count, columns=["职位分类", "数量"])
            st.dataframe(df_jobs)

            
        else:
            st.info("暂无职位数据。")
    with page2:
        import matplotlib.pyplot as plt
        plt.rcParams['font.sans-serif'] = ['SimHei']  
        plt.rcParams['axes.unicode_minus'] = False   

        plt.figure(figsize=(8,5))
        sns.barplot(data=df_jobs, x="职位分类", y="数量", palette="pastel")
        plt.title(f"职位分类数量统计（总职位数: {total_jobs}）")
        plt.xlabel("职位分类")
        plt.ylabel("职位数量")
        plt.xticks(rotation=45)
        st.pyplot(plt)