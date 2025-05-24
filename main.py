# main.py

import streamlit as st
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu

# ------------------- 自定义模块导入 -------------------
from SPAGES import (
    display_homepage,
    display_resume_upload,
    display_analysis,
    myinfo_page,
    api_config_page,
    job_manager_page
)
from SPAGES.HR_insights_page import hr_insights_page
from DB.database import init_db
from Component.Login.auth_mysql import auto_login, login, logout, register_user
from Component.Display.style_load import load_lottie, load_css

# ------------------- 页面基础设置 -------------------
st.set_page_config(
    page_title="欢迎使用智能简历优化平台",
    layout="wide",
    page_icon="💼",
    initial_sidebar_state="collapsed"
)

# ------------------- 初始化资源 -------------------
init_db()
animation = load_lottie("./assets/hello_diplay.json")

if "page" not in st.session_state:
    st.session_state.page = "intro"

# ------------------- 页面逻辑控制 -------------------

# 1. 欢迎引导页
if st.session_state.page == "intro":
    st.write("---")
    load_css("./styles/styles.css")
    col1, col2 = st.columns([1.6, 1])
    with col1:
        st_lottie(animation, height=320)
    with col2:
        st.markdown("## 💼 智能简历优化平台")
        st.markdown("<h1>让你的简历脱颖而出</h1>", unsafe_allow_html=True)
        st.markdown("""
        <p>
        我们提供基于AI的大数据智能简历优化服务，<br>
        自动提取关键词、智能匹配岗位，提升求职效率。<br><br>
        简历优化、评分、建议，一键搞定。
        </p>
        """, unsafe_allow_html=True)
        if st.button("🚀 开始使用"):
            st.session_state.page = "login"
            st.rerun()

# 2. 登录注册页
elif st.session_state.page == "login":
    auto_login()
    if st.session_state.get("logged_in"):
        st.session_state.page = "home"
        st.rerun()
    else:
        tab1, tab2 = st.tabs(["登录", "注册"])
        with tab1:
            login()
        with tab2:
            register_user()

# 3. 主页面（已登录）
elif st.session_state.page == "home":

    # 顶部退出按钮
    st.markdown('<div class="header-right">', unsafe_allow_html=True)
    if st.columns([8, 2])[1].button("退出登录", key="logout_btn"):
        logout()
        st.session_state.page = "intro"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # 左侧导航栏
    with st.sidebar:
        st_lottie(load_lottie("./assets/ai_resume.json"), height=90)
        selected = option_menu(
            "导航栏",
            ["首页", "职位管理", "简历管理", "简历分析", "HR", "我的主页", "API配置"],
            icons=['house', 'person-badge', 'upload', 'search', 'person-workspace', 'person-circle', 'gear'],
            menu_icon="cast",
            default_index=0
        )
        
        if "user_info" in st.session_state:
            load_css("./styles/sidebar_profile.css")
            username = st.session_state.user_info["username"]
            phonenumber = st.session_state.user_info["phonenumber"]
            # st.markdown("---",) unsafe_allow_html=True)
            st.markdown(f"""
                <div class="profile-box">
                    <div class="profile-header">
                        <img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png">
                        <strong>{username}</strong>
                    </div>
                    <div class="profile-phone">📱 {phonenumber}</div>
                </div>
            """, unsafe_allow_html=True)

    # 页面跳转逻辑
    phonenumber = st.session_state.user_info.get("phonenumber", None) if "user_info" in st.session_state else None
    username = st.session_state.user_info.get("username", None) if "user_info" in st.session_state else None

    if selected == "首页":
        display_homepage()

    elif selected == "职位管理":
        job_manager_page() if phonenumber else st.warning("尚未登录或用户信息未保存")

    elif selected == "简历管理":
        display_resume_upload(phonenumber) if phonenumber else st.warning("请先登录后使用该功能。")

    elif selected == "简历分析":
        display_analysis(phonenumber, username) if phonenumber else st.warning("请先登录后使用该功能。")

    elif selected == "HR":
        hr_insights_page(phonenumber)

    elif selected == "我的主页":
        myinfo_page(phonenumber, username)

    elif selected == "API配置":
        api_config_page(phonenumber)
