import os
import json
import re
from matplotlib.font_manager import FontProperties
import mysql.connector
import pdfplumber
import docx
import matplotlib.pyplot as plt
from datetime import datetime
from Component.ResumeAnalysis.prompt_templateops import prompt_template_format_jobrequire, prompt_template_format_resume, prompt_template_format_resume_job_score
from Component.ResumeAnalysis.resume_anaops_mysql import insert_analysis
from zhipuapi import call_gpt_model  # 你需自行封装
from oputils.db_config import DB_CONFIG
import streamlit as st


def parse_model_output(raw_str: str) -> dict:
    """
    处理模型返回的带有 ```json ... ``` 的字符串，去除标记后转换成Python字典。
    """
    cleaned_str = re.sub(r"^```json\s*|```$", "", raw_str.strip(), flags=re.DOTALL)
    try:
        data = json.loads(cleaned_str)
    except Exception as e:
        st.error(f"解析模型返回JSON失败：{e}")
        return {}
    return data


class ResumeProcessor:
    def __init__(self, phonenumber):
        self.phonenumber = phonenumber

    def extract_text(self, file_path):

        ext = os.path.splitext(file_path)[1].lower()

        try:
            if ext == '.pdf':
                with pdfplumber.open(file_path) as pdf:
                    texts = [page.extract_text() for page in pdf.pages if page.extract_text()]
                    return "\n".join(texts)
            elif ext == '.docx':
                doc = docx.Document(file_path)
                return "\n".join([p.text for p in doc.paragraphs])
            else:
                raise ValueError("不支持的文件类型")
        except Exception as e:
            raise RuntimeError(f"简历文本提取失败: {e}")

    def structure_resume_content(self, resume_text, api_url, api_key, api_name):
        prompt_template = prompt_template_format_resume(resume_text)
        try:
            response = call_gpt_model(
                prompt_template=prompt_template,
                api_url=api_url,
                api_key=api_key,
                api_name=api_name,
            )
            structured_resume = parse_model_output(response)
            # print("structured_resume:", repr(structured_resume))
            # print("structured_resume:", type(structured_resume))

            if not isinstance(structured_resume, dict):
                raise ValueError("模型返回的结构化简历不是字典格式")
            return structured_resume
        except Exception as e:
            st.error(f"结构化简历调用失败: {e}")
            return {}
    def structure_job_requirements(self, job_requirements,api_url, api_key, api_name):
        prompt_template = prompt_template_format_jobrequire(job_requirements)
        try:    
            response = call_gpt_model(
                prompt_template=prompt_template,
                api_url=api_url,
                api_key=api_key,
                api_name=api_name,
            )
            structured_jobrequiremnets = parse_model_output(response)
            if not isinstance(structured_jobrequiremnets, dict):
                raise ValueError("模型返回的结构化简历不是字典格式")
            print(structured_jobrequiremnets)
            print(type(structured_jobrequiremnets))
            return structured_jobrequiremnets
        except Exception as e:
            st.error(f"结构化简历调用失败: {e}")
            return {}

    def score_resume_with_llm(self,structured_resume, structured_job, api_url, api_key, api_name):
        prompt = prompt_template_format_resume_job_score(structured_resume, structured_job)

        response = call_gpt_model(
            prompt_template=prompt,
            api_url=api_url,
            api_key=api_key,
            api_name=api_name,
        )
        structured_data = parse_model_output(response)
        print("structured_data:", structured_data)
        # print(type(structured_data))
        try:
            expected_keys = ["education_score", "skills_score", "experience_score","certifications_score", "personal_qualities_score",]
            if all(k in structured_data for k in expected_keys):
                return structured_data
            else:
                raise ValueError("返回结果不包含完整的评分字段")
        except Exception as e:
            st.warning(f"⚠️ 评分解析失败，使用默认评分逻辑。原因：{e}")
            return self.score_resume_against_job(structured_resume, structured_job)  # 兜底用本地评分

    def score_resume_against_job(self, structured_resume, structured_jobrequiremnets):
        if not isinstance(structured_resume, dict):
            raise TypeError("structured_resume必须是字典类型")
        score = {
            "education_score": 0,
            "skills_score": 0,
            "experience_score": 80,  
            "certifications_score": 0,
            "personal_qualities_score": 0,
        }
        # print(job_requirements)


        education_levels = ["高中", "大专", "本科", "硕士", "博士"]
        try:
            edu_index_resume = education_levels.index(structured_resume.get("education", ""))
            edu_index_job = education_levels.index(structured_jobrequiremnets.get("required_education", "本科"))
            score["education_score"] = max(0, 100 - (edu_index_job - edu_index_resume) * 20)
        except Exception:
            score["education_score"] = 50

        def calc_match_score(required, provided):
            if not required:
                return 0
            return int(len(set(required) & set(provided)) / len(required) * 100)

        score['education_score'] = calc_match_score(
            structured_jobrequiremnets.get("required_education", []),
            structured_resume.get("education", [])
        )
        score["skills_score"] = calc_match_score(
            structured_jobrequiremnets.get("required_skills", []),
            structured_resume.get("skills", [])
        )
        score["experience_score"] = calc_match_score(
            structured_jobrequiremnets.get("required_experience", []),
            structured_resume.get("experience", [])
        )
        
        score["certifications_score"] = calc_match_score(
            structured_jobrequiremnets.get("required_certifications", []),
            structured_resume.get("certifications", [])
        )

        score["personal_qualities_score"] = calc_match_score(
            structured_jobrequiremnets.get("desired_personal_qualities", []),
            structured_resume.get("personal_qualities", [])
        )


        return score

    def save_analysis_result(self, resume_id, score_dict, job_id, outcome,json_analysis_result, state="已完成"):
        
        # 设置中文字体
        font = FontProperties(fname=r"C:\Windows\Fonts\simhei.ttf", size=12)
        plt.rcParams['font.family'] = font.get_name()

        plt.rcParams['axes.unicode_minus'] = False

        score = int(sum(score_dict.values()) / len(score_dict))

        analysis_id = insert_analysis(
            self.phonenumber,
            resume_id,
            job_id=job_id,  
            overall_score = score,
            analysis_summary=outcome,
            json_analysis_result=json_analysis_result,
            status=state
        )

        return analysis_id

    def plot_score_radar(self, score_dict):
        labels = ['教育', '知识技能', '经验', '证书', '个人品质']
        scores = [
            score_dict.get("education_score", 0),
            score_dict.get("skills_score", 0),
            score_dict.get("experience_score", 0),
            score_dict.get("certifications_score", 0),
            score_dict.get("personal_qualities_score", 0)
        ]
        angles = [n / float(len(labels)) * 2 * 3.14159 for n in range(len(labels))]
        scores += scores[:1]
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.set_theta_offset(3.14159 / 2)
        ax.set_theta_direction(-1)

        plt.xticks(angles[:-1], labels)
        ax.plot(angles, scores, linewidth=2, linestyle='solid')
        ax.fill(angles, scores, 'b', alpha=0.25)
        plt.title("简历匹配评分雷达图")
        st.pyplot(fig)
