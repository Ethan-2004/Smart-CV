import streamlit as st
from datetime import datetime
import Component as co
import streamlit as st
from oputils.config_utils import get_model_config, update_model_config
def mask_api_key(api_key: str) -> str:
    if len(api_key) <= 6:
        return "*" * len(api_key)
    return f"{api_key[:3]}{'*' * (len(api_key) - 6)}{api_key[-3:]}"

def api_config_page(phonenumber):
    st.markdown("## 🔧 API 配置管理")
    st.markdown("---")

    if not phonenumber:
        st.warning("请先登录后管理API配置。")
        return

    # 读取已有API配置
    api_list = co.get_analysis_api(phonenumber)


    st.subheader("🧩 模型配置")
    # ➤ 从数据库 API 配置中构建可选项
    api_options = {f"{api['api_name']}": api for api in api_list}
    selected_label = st.selectbox("选择默认模型 API 配置", list(api_options.keys()))
    selected_api = api_options[selected_label]
    if  selected_label:
        api_url = selected_api["api_url"]
        api_key = selected_api["api_key"]
        model_name = selected_api["api_name"]
        update_model_config(model_name, api_url, api_key)
    st.write("---")
    
    # 添加新API配置表单
    with st.expander("➕ 添加新的API配置", expanded=False):
        with st.form("add_api_form"):
            api_name = st.text_input("API名称", key="add_api_name")
            api_url = st.text_input("API地址", key="add_api_url")
            api_key = st.text_input("API Key", key="add_api_key")
            submitted = st.form_submit_button("添加API配置")
            if submitted:
                if not api_name or not api_url or not api_key:
                    st.error("API名称、地址和Key不能为空！")
                else:
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    co.insert_analysis_api(phonenumber, api_name, api_url, api_key, now)
                    st.success("API配置添加成功！")
                    st.rerun()

    st.markdown("---")
    st.markdown("### 📋 已配置的API列表")

    if not api_list:
        st.info("你还没有添加任何API配置。")
        return

    for api in api_list:
        with st.expander(f"📌 **{api['api_name']}**", expanded=False):  # API名称作为加粗标题

            st.text_input("📛 API 名称", value=api["api_name"], key=f"name_{api['id']}", disabled=True)
            st.text_input("🌐 API 地址", value=api["api_url"], key=f"url_{api['id']}", disabled=True)

            # 处理 API Key 显示（始终加密，只保留前3和后3位）
            masked_key = mask_api_key(api["api_key"])
            st.text_input("🔑 API Key", value=masked_key, key=f"key_input_{api['id']}", disabled=True)

            # 删除按钮（如果你想隐藏按钮样式，也可用CSS隐藏）
            if st.button("🗑️ 删除此API", key=f"delete_api_{api['id']}"):
                co.delete_analysis_api(api["id"])
                st.success(f"已删除 API 配置：{api['api_name']}")
                st.rerun()


    


