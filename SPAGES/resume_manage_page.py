import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
import Component as co
from Component.ResumeAnalysis.resume_processor import ResumeProcessor
from oputils.config_utils import get_model_config
from oputils.haxi import calculate_file_hash


@st.cache_resource
def load_provinces():
    with open("assets/provinces.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        return [item["name"] for item in data]

def select_province(label="地区筛选"):
    provinces = load_provinces()
    selected = st.selectbox(label, ["全部"] + provinces, index=0)
    return None if selected == "全部" else selected

def update_state_callback(resume_id, selectbox_key):
    new_state = st.session_state[selectbox_key]
    co.update_resume(resume_id, "state", new_state)
    st.success(f"状态已更新为：{new_state}")
    st.rerun()

def display_resume_upload(phonenumber):
    st.title("📄 批量上传简历")
    uploaded_files = st.file_uploader("上传 PDF 或 Word 简历（支持多个）", type=["pdf", "docx"], accept_multiple_files=True)

    if uploaded_files:
        for file in uploaded_files:
            try:
                file_name = file.name
                suffix = file_name.split(".")[-1].lower()
                file_bytes = file.getbuffer()
                file_hash = calculate_file_hash(file_bytes)

                if co.check_resume_by_hash(file_hash):
                    st.warning(f"文件重复：{file_name}（已上传过）")
                else:
                    save_dir = "uploaded_resumes"
                    os.makedirs(save_dir, exist_ok=True)
                    save_path = os.path.join(save_dir, file_name)

                    with open(save_path, "wb") as f:
                        f.write(file_bytes)

                    processor = ResumeProcessor(phonenumber=phonenumber)
                    raw_text = processor.extract_text(save_path)
                    # print(raw_text)

                    model_config = get_model_config()
                    api_name = model_config.get("model_name")
                    api_url = model_config.get("api_url")
                    api_key = model_config.get("api_key")

                    structured_resume = processor.structure_resume_content(
                        raw_text, api_url, api_key, api_name
                    )


                    st.write("## 简历结构化结果")
                    json_resume_data = str(structured_resume)

                    content_summary = raw_text[:500]
                    school = structured_resume.get("school", "")
                    education = structured_resume.get("education", "")
                    expected_salary = structured_resume.get("expected_salary", "")
                    age = structured_resume.get("age", "")
                    region = structured_resume.get("region", "")
                    gender = structured_resume.get("gender", "")


                    co.insert_resume(
                        phonenumber=phonenumber,
                        resume_name=file_name,
                        save_path=save_path,
                        file_hash=file_hash,
                        upload_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        content_summary=content_summary,
                        school=school,
                        education=education,
                        expected_salary=expected_salary,
                        age=age,
                        region=region,
                        gender=gender,
                        state="已上传",
                        json_resume_data = json_resume_data,
                    )
                    
                    st.success(f"成功处理：{file_name}")

            except Exception as e:
                st.error(f"解析失败：{file.name}，错误：{e}")


    st.subheader("📑 上传记录")
    rows = co.get_all_resumes(phonenumber)
    if not rows:
        st.info("暂无简历上传记录")
        return


    rows_str = []
    for row in rows:

        row_list = list(row)

        if isinstance(row_list[-1], dict):
            row_list[-1] = json.dumps(row_list[-1], ensure_ascii=False)
        row_str = tuple(row_list)
        rows_str.append(row_str)

    df = pd.DataFrame(rows, columns=[
        "ID", "手机号", "简历名", "文件哈希", "保存路径", "上传时间", "内容摘要",
        "学校", "学历", "期望薪资", "年龄", "地区", "性别", "状态", "结构化简历"
    ])

    with st.expander("筛选条件", expanded=True):
        st.markdown("**🔍 筛选条件**")
        edu_filter = st.selectbox("按学历筛选", ["全部", "专科", "本科", "硕士", "研究生", "博士生", "博士后"], index=0)
        gender_filter = st.selectbox("按性别筛选", ["全部", "男", "女"], index=0)
        province_filter = select_province("按地区筛选（省级）")
        keyword = st.text_input("关键词搜索（任意字段）")

    if edu_filter != "全部":
        df = df[df["学历"] == edu_filter]
    if gender_filter != "全部":
        df = df[df["性别"] == gender_filter]
    if province_filter:
        df = df[df["地区"].str.contains(province_filter, na=False)]
    if keyword:
        df = df[df.apply(lambda row: row.astype(str).str.contains(keyword, case=False).any(), axis=1)]

    states = ["已上传", "已失效", "已录用", "观察中"]

    for _, row in df.iterrows():
        st.markdown(f"### {row['简历名']}")
        with st.expander("🔧 操作", expanded=False):
            cols = st.columns([3, 2])
            with cols[0]:
                st.markdown("#### 信息摘要")
                st.json({
                    "内容摘要": row['内容摘要'],
                    "学校": row['学校'],
                    "学历": row['学历'],
                    "期望薪资": row['期望薪资'],
                    "年龄": row['年龄'],
                    "地区": row['地区'],
                    "性别": row['性别'],
                })

            with cols[1]:
                selectbox_key = f"resume_state_{row['ID']}"
                current_state = row['状态']
                st.selectbox(
                    "修改状态",
                    options=states,
                    index=states.index(current_state) if current_state in states else 0,
                    key=selectbox_key,
                    on_change=update_state_callback,
                    args=(row['ID'], selectbox_key)
                )

                if st.button("删除", key=f"delete_{row['ID']}"):
                    co.delete_resume(row['ID'])
                    st.warning("已删除")
                    st.rerun()
