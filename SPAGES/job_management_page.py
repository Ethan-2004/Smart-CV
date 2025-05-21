from datetime import datetime
import streamlit as st
import Component as co
import json
import time
import random

def job_manager_page():
    st.subheader("🗂 职位管理")

    # 初始化 session state
    if "job_imported" not in st.session_state:
        st.session_state.job_imported = False
    if "uploader_key" not in st.session_state:
        st.session_state.uploader_key = str(random.randint(1000, 9999))  # 初始化上传器 key
    if "show_delete_confirm" not in st.session_state:
        st.session_state.show_delete_confirm = False


    # 📦 JSON导入导出
    with st.expander("📁 JSON导入/导出", expanded=False):
        col1, col2 = st.columns([1, 1])

        with col1:
            uploaded_file = st.file_uploader("导入 JSON 文件", type=["json"], key=st.session_state.uploader_key)

            if uploaded_file is not None and not st.session_state.job_imported:
                try:
                    file_content = uploaded_file.read().decode("utf-8")
                    content = json.loads(file_content)

                    if not isinstance(content, list):
                        st.error("导入失败：JSON 文件内容应为职位对象的列表。")
                    else:
                        progress_bar = st.progress(0, text="正在导入职位...")
                        total = len(content)

                        imported_count = co.add_jobs_batch_sqlalchemy(content)

                        for i in range(100):
                            progress_bar.progress(i / 100.0, text=f"已导入 {imported_count} / {total} 个职位")
                            time.sleep(0.01)

                        progress_bar.empty()
                        if imported_count > 0:
                            st.success(f"✅ 成功导入 {imported_count} 个职位！")
                        else:
                            st.warning("未导入任何职位，请检查文件内容是否正确。")

                        st.session_state.job_imported = True
                        st.session_state.uploader_key = str(random.randint(1000, 9999))  # 触发 file_uploader 重置
                        st.rerun()

                except Exception as e:
                    st.error(f"导入失败：{e}")

        with col2:
            jobs = co.get_all_jobs()
            if st.button("📤 导出 JSON"):
                job_list = []
                for job in jobs:
                    job_list.append({
                        "name": job[1],
                        "category": job[2],
                        "description": job[3],
                        "created_at": job[4].strftime("%Y-%m-%d %H:%M:%S") if isinstance(job[4], datetime) else job[4]

                    })
                json_data = json.dumps(job_list, ensure_ascii=False, indent=2)
                st.download_button("点击下载 JSON 文件", data=json_data, file_name="jobs_export.json", mime="application/json")

    st.write("\t")

    # ➕ 新增职位表单
    with st.expander("➕ 新增职位", expanded=False):
        with st.form("add_job_form"):
            new_name = st.text_input("职位名称", max_chars=50)
            new_category = st.text_input("职位类别", max_chars=30)
            new_description = st.text_area("职位描述", height=100, max_chars=300)
            submitted = st.form_submit_button("添加职位")
            if submitted:
                if new_name.strip() and new_category.strip():
                    co.add_job(new_name, new_category, new_description)
                    st.success("职位添加成功！")
                    st.rerun()
                else:
                    st.error("职位名称和类别不能为空！")

    st.markdown("---")
    st.subheader("📃 职位列表")

    jobs = co.get_all_jobs()
    if not jobs:
        st.info("暂无职位信息。")
        return

    s1,s2=st.columns([2,1])
    with s1:
        # 🔍 模糊搜索框（默认显示全部）
        search_keyword = st.text_input("🔍 搜索职位（名称或类别，留空显示全部）", "")

        # 🔍 过滤结果
        if search_keyword.strip():
            jobs = [
                job for job in jobs
                if search_keyword.lower() in job[1].lower() or search_keyword.lower() in job[2].lower()
            ]
            if not jobs:
                st.warning("未找到匹配的职位。")
    with s2:          
        # 一键删除所有职位按钮及确认
        st.write("\t")
        _ , col_del = st.columns([1, 1])
        with col_del:
            # 用 st.button 加 tooltip (simulated by st.markdown + hover style)
            delete_button = st.button("🗑️ 一键删除", help="⚠️ 点击后会删除数据库所有职位，操作不可恢复，请谨慎！")

        if delete_button:
            try:
                co.delete_all_jobs()
                st.success("✅ 所有职位已被删除！")
                st.session_state.show_delete_confirm = False
                # 刷新页面
                st.rerun()
            except Exception as e:
                st.error(f"删除失败: {e}")
                st.session_state.show_delete_confirm = False



    st.write("---")
    # ⬇️ 展示每一个职位
    for job in jobs:
        id, job_name, job_category, job_description, created_at = job
        with st.container():
            st.markdown(
                f"""
                <div style="
                    border:1px solid #d1d5db; 
                    border-radius:8px; 
                    padding:12px 18px; 
                    margin-bottom:12px; 
                    background: #f8fafc;
                    font-family: Arial, sans-serif;
                ">
                <h4 style="margin-bottom:4px; color:#0B3D91; font-size:18px;">{job_name}</h4>
                <p style="color: #6B7280; margin:0 0 8px 0; font-size:14px;">类别: {job_category}  |  创建时间: {created_at}</p>
                </div>
                """, unsafe_allow_html=True
            )
            with st.expander("编辑职位详情", expanded=False):
                with st.form(f"edit_form_{job_name}_{id}"):
                    edited_name = st.text_input("职位名称", value=job_name, max_chars=50, key=f"name_{job_name}_{id}")
                    edited_category = st.text_input("职位类别", value=job_category, max_chars=30, key=f"category_{job_name}_{id}")
                    edited_description = st.text_area("职位描述", value=job_description, height=110, max_chars=300, key=f"description_{job_name}_{id}")

                    col1, col2 = st.columns([1, 1])
                    with col1:
                        update_btn = st.form_submit_button("更新职位")
                    with col2:
                        delete_btn = st.form_submit_button("删除职位")

                    if update_btn:
                        if edited_name.strip() and edited_category.strip():
                            co.update_job(id, edited_name, edited_category, edited_description)
                            st.success(f"职位“{edited_name}”更新成功！")
                            st.rerun()
                        else:
                            st.error("职位名称和类别不能为空！")

                    if delete_btn:
                        co.delete_job(id)
                        st.success(f"职位“{job_name}”已删除！")
                        st.rerun()
