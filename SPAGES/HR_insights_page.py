import re
import streamlit as st
import pandas as pd
import json
from datetime import datetime
from Component.ResumeAnalysis.resume_anaops_mysql import get_analy_json_by_analysis_id, get_resume_analysis
from Component.HR_ops.hr_insights_ops import (
    get_performance_by_user, save_performance,
    get_training_by_analysis, save_training,
    get_retention_by_user, save_retention
)
from Component.ResumeAnalysis.resume_processor import ResumeProcessor
from oputils.secret import decrypt_api_key
from oputils.config_utils import get_model_config
from zhipuapi import call_gpt_model
import Component as co

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
def hr_insights_page(phonenumber):
  st.title("🚀 HR 智能洞察")

  # 1. 先让用户选手机号下的分析记录
  ph =  phonenumber
  if not ph:
      st.warning("请先登录。")
      st.stop()
      
  resumes = co.get_user_resumes(phonenumber)
  if not resumes:
      st.info("暂无简历，请上传。")
      return

  resume_dict = {row[1]: row[0] for row in resumes}
  resume_name = st.selectbox("请选择要分析的简历", list(resume_dict.keys()))
  resume_id = resume_dict[resume_name]
  resume = co.get_resume_by_id(resume_id)
  # st.write(resume)
  resume_name = resume[2]
  resume_json = resume[6]

  analyses = co.get_resume_analysis(resume_id)  # 改造：可按手机号筛选

  options = [
      f"ID:{record[0]} - 分数:{record[1]} - 时间:{record[2].strftime('%Y-%m-%d %H:%M:%S')}"
      for record in analyses 
  ]
  selected_option = st.selectbox("选择分析记录", options , index=0)
  analysis_id = int(selected_option.split(" ")[0].split(":")[1])
  analy_json = get_analy_json_by_analysis_id(analysis_id)
  job_name = analy_json["job_name"]
  # 构造选项：ID - 时间 - 分数
  options = [
      f"ID:{r[0]}  时间:{r[2].strftime('%Y-%m-%d %H:%M')}  分数:{r[1]}"
      for r in analyses
  ]

  cfg = get_model_config()
  api_url = cfg["api_url"]
  api_key = cfg["api_key"]
  api_name = cfg["model_name"]
  # st.write(cfg)
  
  # ── Tab 1: 绩效评估 ──
  tab1, tab2, tab3 = st.tabs(["📈 绩效评估", "🎯 培训推荐", "❤️ 满意度预测"])
  prompt_template1 = """你是一个企业人力绩效分析专家。请根据以下内容评估员工本次的工作绩效情况。

岗位：{job_name}
岗位匹配度和技能适配度分析：{analy_json}
员工近期工作成果（由用户填写）：{work_summary}

请从以下维度分别打分（0-100）：
1. 岗位匹配度（job_fit）
2. 技能适配度（skill_match）
3. 沟通与协作能力（communication）

返回标准 JSON 格式如下：
{{
  "job_fit": 0,
  "skill_match": 0,
  "communication": 0,
  "summary": "评估总结性描述"
}}
"""
  with tab1:
    st.subheader("历史绩效记录")
    perf = get_performance_by_user(ph,resume_id)
    if perf:
        df = pd.DataFrame(perf)
        df["scores"] = df["scores"].map(lambda s: json.loads(s))
        st.dataframe(df[["created_at", "scores", "summary"]])
        st.line_chart(pd.DataFrame([
            {**json.loads(r["scores"]), "时间": r["created_at"]} for r in perf
        ]).set_index("时间"))
    else:
        st.info("暂无绩效数据。")

    work_summary = st.text_area("请输入该员工近期的工作成果：", "")
    if st.button("生成本次绩效评估") and work_summary.strip():
        prompt = prompt_template1.format(
            job_name=job_name,
            work_summary=work_summary,
            analy_json=analy_json
        )

        resp = call_gpt_model(prompt, api_name,api_url, api_key)
        try:
            data = parse_model_output(resp)
            scores = {
                "job_fit": data.get("job_fit", 0),
                "skill_match": data.get("skill_match", 0),
                "communication": data.get("communication", 0)
            }
            summary = data.get("summary", "系统生成总结")
            save_performance(ph, resume_id,analysis_id, scores, summary)
            st.success("已保存本次绩效评估。")
            st.rerun()
        except Exception as e:
            st.error(f"绩效评估解析失败: {e}")

  prompt_template2 = """你是企业培训师。请根据以下内容，为员工设计个性化培训推荐。

岗位名称：{job_name}
简历内容：{resume_text}
岗位匹配分析：{analysis_result}

请推荐 2-3 个培训主题，并说明每个主题的理由，返回以下 JSON 格式：
{{
  "recommendations": [
    {{
      "topic": "沟通技巧提升",
      "reason": "该员工在沟通能力方面存在短板。"
    }},
    {{
      "topic": "Python 高级编程",
      "reason": "技术能力可进一步加强以匹配岗位要求。"
    }}
  ]
}}
"""
  with tab2:
    st.subheader("最新培训推荐")
    train = get_training_by_analysis(analysis_id)
    if train:
        st.markdown(train["content"])
    else:
        st.info("暂无培训推荐。")

    if st.button("一键生成培训方案"):
        prompt = prompt_template2.format(
            job_name=job_name,
            resume_text=resume_json,
            analysis_result=json.dumps(analy_json, ensure_ascii=False)
        )
        resp = call_gpt_model(prompt, api_name,api_url, api_key)
        try:
            data = parse_model_output(resp)
            # print(data)
            md = "\n".join([f"- **{item['topic']}**：{item['reason']}" for item in data.get("recommendations", [])])
            save_training(ph,resume_id,analysis_id,md)
            st.success("已生成并保存培训方案。")
            st.rerun()
        except Exception as e:
            st.error(f"培训推荐解析失败: {e}")

  prompt_template3 = """你是一个人力资源专家，请根据以下岗位匹配分析数据，预测该员工的离职风险，并说明理由。

分析编号：{analysis_id}
岗位名称：{job_name}
岗位匹配分析结果（JSON）：{analysis_result}

请返回标准 JSON 格式：
{{
  "risk_level": "",  // 可选值：低、中、高
  "reason": "" // 离职风险原因
}}
"""
  with tab3:
      st.subheader("离职风险预测")
      
      preds = get_retention_by_user(ph, resume_id)
      
      risk_map = {"高": 3, "中": 2, "低": 1, "未知": 0}

      if preds:
          df2 = pd.DataFrame(preds)
          df2["details"] = df2["details"].map(lambda s: json.loads(s) if s else {})
          df2["risk_score"] = df2["risk_level"].map(risk_map)
          df2["created_at"] = pd.to_datetime(df2["created_at"])

          # 展示数据表
          st.dataframe(df2[["created_at", "risk_level", "details"]])

          # 折线图展示风险等级趋势
          st.markdown("#### 📈 风险等级趋势图")
          chart_data = df2[["created_at", "risk_score"]].set_index("created_at").sort_index()
          st.line_chart(chart_data)

      else:
          st.info("暂无预测数据。")

      # 生成预测按钮
      if st.button("生成离职风险预测"):
          prompt = prompt_template3.format(
              analysis_id=analysis_id,
              job_name=job_name,
              analysis_result=json.dumps(analy_json, ensure_ascii=False)
          )
          resp = call_gpt_model(prompt, api_name, api_url, api_key)
          try:
              data = parse_model_output(resp)
              save_retention(ph, resume_id, analysis_id, data.get("risk_level", "未知"), data)
              st.success("已生成并保存离职风险预测。")
              st.rerun()
          except Exception as e:
              st.error(f"离职风险预测解析失败: {e}")

