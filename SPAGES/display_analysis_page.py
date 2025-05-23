import os
import io
import time
import json
import random
import hashlib
import datetime
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import mysql.connector
import pdfplumber
import docx
import pytesseract
from PIL import Image
from datetime import date, datetime
from Component.Analysis_record.analysis_recoreds_ops import get_resume_score_detail_by_analysis_id
from Component.ResumeAnalysis.resume_processor import ResumeProcessor

import Component as co
from Component import get_user_resumes, get_resume_analysis, delete_analysis, get_all_jobs, get_job_by_id, get_all_models
from Component.ResumeManeger.resume_ops_mysql import update_json_resume_data
from oputils.db_config import DB_CONFIG
from oputils.secret import decrypt_api_key
from oputils.haxi import calculate_file_hash
from Component.ResumeAnalysis.resume_anaops_mysql import get_resume_json_by_resume_id, save_analysis_result
from zhipuapi import call_gpt_model

api_name = api_url = decode_apikey = job_data = score_dict =job_data_row= None

# ...（省略 import 部分）

def display_analysis(phonenumber, username):
    st.title("📊 简历分析中心")

    resumes = co.get_user_resumes(phonenumber)
    if not resumes:
        st.info("暂无简历，请上传。")
        return

    resume_dict = {row[1]: row[0] for row in resumes}
    resume_name = st.selectbox("请选择要分析的简历", list(resume_dict.keys()))
    resume_id = resume_dict[resume_name]
    resume = co.get_resume_by_id(resume_id)

    def resume_analysis_page(phonenumber):
        st.markdown("---")

        api_name = api_url = decode_apikey = job_data = choose_job = None
        co1, co2 = st.columns([1, 1])
        with co1:
            jobs = co.get_all_jobs()
            job_options = [f"{job[1]} - {job[2]}" for job in jobs]
            job_mapping = {f"{job[1]} - {job[2]}": job[0] for job in jobs}

            selected_job_label = st.selectbox("选择职位", job_options, index=0)

            if st.button("➕ 创建新职位"):
                st.switch_page("job_management_page")

            job_description = ""
            if selected_job_label:
                job_id = job_mapping[selected_job_label]
                job_data_row = co.get_job_by_id(job_id)
                # st.success(f"已选职位：{job_data_row[0]} ")
                job_description = job_data_row[3]
                choose_job = f"{job_data_row[1]} - {job_data_row[2]}"
                st.success(f"已选职位：{choose_job}")
                job_data = f"{choose_job} - {job_description}"

        with co2:
            models = co.get_all_models(phonenumber)
            model_options = [model['api_name'] for model in models]
            model_mapping = {model['api_name']: model for model in models}

            selected_model_label = st.selectbox("选择模型", model_options, index=0)

            if selected_model_label:
                model_info = model_mapping[selected_model_label]
                api_name = model_info["api_name"]
                api_url = model_info["api_url"]
                api_key = model_info["api_key"]
                decode_apikey = decrypt_api_key(api_key)
                st.success(f"已选模型：{api_name}")

        if selected_job_label and selected_model_label:
            st.write(f"简历路径：{resume[4]}")

        # 修改返回语句，增加 job_data_row
        return api_name, api_url, decode_apikey, job_data, choose_job, job_data_row


    # 修改 unpack 变量，添加 job_data_row
    api_name, api_url, decode_apikey, job_data, choose_job, job_data_row = resume_analysis_page(phonenumber)


    def process_resume_main(file_path, resume_id, job_data, api_url, api_key, api_name, phonenumber, job_data_raw,choose_job):
        processor = ResumeProcessor(phonenumber=phonenumber)

        # ✅ 先尝试从数据库读取结构化简历
        structured_resume = get_resume_json_by_resume_id(resume_id)

        # 如果数据库中没有已解析数据，则提取文本并调用大模型解析
        if not structured_resume:
            raw_text = processor.extract_text(file_path)
            structured_resume = processor.structure_resume_content(raw_text, api_url, api_key, api_name)
            st.success("✅ 结构化简历完成")
            if structured_resume:
                update_json_resume_data(resume_id, structured_resume)


        def stringify_dict(d):
            return {k: ", ".join(v) if isinstance(v, list) else str(v) for k, v in d.items()}

        safe_resume = stringify_dict(structured_resume)
        resume_df = pd.DataFrame(safe_resume.items(), columns=["字段", "内容"])
        st.subheader("结构化简历内容")
        st.table(resume_df)

        structured_jobrequirements = processor.structure_job_requirements(job_data, api_url, api_key, api_name)
        st.success("✅ 结构化岗位完成")

        safe_job = stringify_dict(structured_jobrequirements)
        job_df = pd.DataFrame(safe_job.items(), columns=["字段", "要求"])
        st.subheader("🧾 结构化岗位要求")
        st.table(job_df)

        st.write("📝 简历与岗位匹配评分")
        score_dict = processor.score_resume_with_llm(structured_resume, structured_jobrequirements, api_url, api_key, api_name)
        st.success("✅ 匹配评分完成")

        outcome = f"""该简历的整体评分为 {int(sum(score_dict.values()) / len(score_dict))} 分。各项得分如下：
- 教育: {score_dict['education_score']} 分
- 技能: {score_dict['skills_score']} 分
- 经验: {score_dict['experience_score']} 分
- 证书: {score_dict['certifications_score']} 分
- 个人品质: {score_dict['personal_qualities_score']} 分
"""
        
        st.info(outcome)
        job_id =job_data_row[0]
        json_analysis_result = str(score_dict)
        analysis_id = processor.save_analysis_result(resume_id, score_dict, job_id, outcome,json_analysis_result,state="已完成")
        
        co.save_resume_score_detail(analysis_id=analysis_id,
                                    score_data=score_dict,
                                    job_name=choose_job
                                    )
# {'education_score': 80, 'knowledge_score': 70, 'certification_score': 50, 'personal_quality_score': 75, 'experience_score': 85}
        return analysis_id, score_dict, structured_resume, outcome
    file_path=resume[4]
    if st.button("开始分析"):
        process_resume_main(file_path, resume_id, job_data, api_url, decode_apikey, api_name, phonenumber,job_data_row,choose_job)

    st.markdown("---")

    with st.expander("📅 分析记录筛选（按日期）", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("开始日期", value=date(2024, 1, 1))
        with col2:
            end_date = st.date_input("结束日期", value=date.today())

    analysis_records = co.get_resume_analysis(
        resume_id=resume_id,
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d")
    )

    df = pd.DataFrame(analysis_records, columns=["ID", "分数", "分析时间", "结果", "状态"])

    if df.empty:
        st.info("该简历在所选时间段内暂无分析记录。")
    else:
        st.subheader("📄 分析记录")
        st.dataframe(df, use_container_width=True)

        export_format = st.radio("导出格式", ["CSV", "Excel"], horizontal=True)
        if st.button("📤 导出分析记录"):
            if export_format == "CSV":
                st.download_button("点击下载 CSV 文件", df.to_csv(index=False).encode('utf-8'), file_name="analysis.csv")
            else:
                towrite = io.BytesIO()
                df.to_excel(towrite, index=False, engine='openpyxl')
                towrite.seek(0)
                st.download_button("点击下载 Excel 文件", towrite, file_name="analysis.xlsx")

        # 图表展示
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        pic1, pic2, pic3 = st.columns([1, 1, 1])

        with pic1:
            st.subheader("🎯 分数分布图")
            plt.clf()
            plt.figure(figsize=(6, 3))
            sns.histplot(df["分数"], kde=True, bins=10, color="skyblue")
            plt.xlabel("分析分数")
            st.pyplot(plt)

        with pic2:
            st.subheader("📈 分析趋势图")
            plt.clf()
            df["分析时间"] = pd.to_datetime(df["分析时间"])
            df_sorted = df.sort_values("分析时间")
            plt.figure(figsize=(6, 3))
            sns.lineplot(data=df_sorted, x="分析时间", y="分数", marker="o", color="orange")
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(plt)

        with pic3:
            st.subheader("📊 雷达图")
            processor = ResumeProcessor(phonenumber=phonenumber)

            options = [
                f"ID:{record[0]} - 分数:{record[1]} - 时间:{record[2].strftime('%Y-%m-%d %H:%M:%S')}"
                for record in analysis_records
            ]

            selected_option = st.selectbox("选择分析记录", options, index=0)
            selected_analysis_id = int(selected_option.split(" ")[0].split(":")[1])

            score_dict = get_resume_score_detail_by_analysis_id(selected_analysis_id)
            if score_dict:
                st.write(score_dict)
                processor.plot_score_radar(score_dict)
            else:
                st.info("该分析记录暂无评分详情数据。")

    with st.expander("🗑️ 删除分析记录"):
        if not df.empty:
            del_id = st.selectbox("选择要删除的记录 ID", df["ID"])
            if st.button("确认删除记录"):
                co.delete_analysis(del_id)
                st.success("删除成功")
                st.experimental_rerun()
