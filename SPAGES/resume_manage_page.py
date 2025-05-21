import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
import Component as co
from oputils.haxi import calculate_file_hash  # 你已有的数据库和解析逻辑模块

# 加载中国省份数据
@st.cache_data
def load_provinces():
    with open("assets/provinces.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        return [item["name"] for item in data]

def select_province(label="地区筛选"):
    provinces = load_provinces()
    selected = st.selectbox(label, ["全部"] + provinces, index=0)
    return None if selected == "全部" else selected

# 新增这个函数：状态更新逻辑
def update_state_callback(resume_id, selectbox_key):
    new_state = st.session_state[selectbox_key]
    co.update_resume(resume_id, "state", new_state)
    st.success(f"状态已更新为：{new_state}")

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

                # 判断是否已经上传相同文件（通过哈希值）
                if co.check_resume_by_hash(file_hash):
                    st.warning(f"文件重复：{file_name}（已上传过）")
                    
                else:
                    save_dir = "uploaded_resumes"
                    os.makedirs(save_dir, exist_ok=True)
                    save_path = os.path.join(save_dir, file_name)

                    with open(save_path, "wb") as f:
                        f.write(file_bytes)

                    text = co.extract_text_from_pdf(save_path) if suffix == "pdf" else co.extract_text_from_docx(save_path)
                    fields = co.extract_fields_from_text(text)

                    co.insert_resume(
                        phonenumber=phonenumber,
                        resume_name=file_name,
                        save_path=save_path,
                        content_summary=text[:500],
                        school=fields.get("school", ""),
                        education=fields.get("education", ""),
                        expected_salary=fields.get("expected_salary", ""),
                        age=fields.get("age", ""),
                        region=fields.get("region", ""),
                        gender=fields.get("gender", ""),
                        state="已上传",
                        file_hash=file_hash  # 存入哈希值
                    )

                    st.success(f"成功处理：{file_name}")
            except Exception as e:
                st.error(f"解析失败：{file.name}，错误：{e}")


    # 显示上传历史
    st.subheader("📑 上传记录")
    rows = co.get_all_resumes(phonenumber)
    if not rows:
        st.info("暂无简历上传记录")
        return

    df = pd.DataFrame(rows, columns=["ID", "手机号", "简历名", "保存路径", "上传时间", "内容摘要", "学校", "学历", "薪资", "年龄", "地区", "性别", "状态","文件哈希"])

    with st.expander("筛选条件", expanded=True):
        st.markdown("**🔍 筛选条件**")
        edu_filter = st.selectbox("按学历筛选", ["全部", "专科", "本科", "硕士", "研究生", "博士生", "博士后"], index=0)
        gender_filter = st.selectbox("按性别筛选", ["全部", "男", "女"], index=0)
        province_filter = select_province("按地区筛选（省级）")
        keyword = st.text_input("关键词搜索（任意字段）")

    # 筛选逻辑
    if edu_filter != "全部":
        df = df[df["学历"] == edu_filter]
    if gender_filter != "全部":
        df = df[df["性别"] == gender_filter]
    if province_filter:
        df = df[df["地区"].str.contains(province_filter, na=False)]
    if keyword:
        df = df[df.apply(lambda row: row.astype(str).str.contains(keyword, case=False).any(), axis=1)]

    st.dataframe(df[["简历名", "上传时间", "学校", "学历", "薪资", "年龄", "地区", "性别", "状态","文件哈希"]], use_container_width=True)

    # 每条简历的详细信息和操作
    states = ["已上传", "已失效", "已录用", "观察中"]

    for _, row in df.iterrows():
        st.markdown(f"### {row['简历名']}")
        with st.expander("🔧 操作", expanded=False):
            cols = st.columns([3, 2])

            with cols[0]:
                st.markdown("#### 信息摘要")
                st.write({
                    "内容摘要": row['内容摘要'],
                    "学校": row['学校'],
                    "学历": row['学历'],
                    "薪资": row['薪资'],
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

