# main.py
import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
import mysql.connector
from datetime import datetime
import bcrypt

from Component.HR_ops.hr_insights_ops import get_mysql_connection
from DB.mysql_db import init_mysql_db
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
from Component.Display.style_load import load_lottie, load_css

# ------------------- 页面基础设置 -------------------
st.set_page_config(
    page_title="欢迎使用智能简历优化平台",
    layout="wide",
    page_icon="💼",
    initial_sidebar_state="collapsed"
)

# ------------------- Cookie 管理 -------------------
cookie_manager = EncryptedCookieManager(
    prefix="myapp_",
    password="a-very-secure-password-32chars!!"
)
if not cookie_manager.ready():
    st.stop()

# ------------------- 初始化 -------------------
animation = load_lottie("./assets/hello_diplay.json")
if "page" not in st.session_state:
    st.session_state.page = "intro"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_info" not in st.session_state:
    st.session_state.user_info = {}

# ------------------- 账户相关逻辑 -------------------
import hashlib
import os
import hmac
import base64

# 盐的长度
SALT_SIZE = 16  # 16字节

# 迭代次数
ITERATIONS = 100_000

# 哈希算法
ALGORITHM = 'sha256'

def hash_password(password: str) -> str:
    salt = os.urandom(SALT_SIZE)
    pwd_hash = hashlib.pbkdf2_hmac(ALGORITHM, password.encode(), salt, ITERATIONS)
    return base64.b64encode(salt).decode() + '$' + base64.b64encode(pwd_hash).decode()

# 验证密码
def verify_password(password: str, stored_password: str) -> bool:
    try:
        salt_b64, hash_b64 = stored_password.split('$')
        salt = base64.b64decode(salt_b64)
        stored_hash = base64.b64decode(hash_b64)
        pwd_hash = hashlib.pbkdf2_hmac(ALGORITHM, password.encode(), salt, ITERATIONS)
        return hmac.compare_digest(pwd_hash, stored_hash)
    except Exception as e:
        print("密码验证失败：", e)
        return False


def logout():
    if "login_user" in cookie_manager:
        cookie_manager["login_user"] = ""
        cookie_manager["login_status"] = "logout"
        cookie_manager.save()

    st.session_state.logged_in = False
    st.session_state.user_info = {}
    st.session_state.page = "intro"
    st.success("退出登录成功")
    st.rerun()

def login_page():


    tab1, tab2 = st.tabs(["登录", "注册"])
    with tab1:
        st.subheader("登录")
        name = st.text_input("姓名",key='login_name')
        phone = st.text_input("手机号")
        password = st.text_input("密码", type="password")
        if st.button("登录"):
            conn = get_mysql_connection()
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE phonenumber = %s", (phone,))
            user = c.fetchone()
            c.close()
            conn.close()

            if not user:
                st.error("手机号未注册")
                return
            print(user[3])
            if verify_password(password,user[3]):  # password在第6列
                st.session_state.logged_in = True
                st.session_state.user_info = {
                    "id": user[0],
                    "username": user[1],
                    "name": user[2],
                    "email": user[4],
                    "phonenumber": user[5]
                }
                cookie_manager["login_status"] = "login"
                cookie_manager["login_user"] = phone
                cookie_manager.save()
                st.success("登录成功")
                st.session_state.page = "home"
                st.rerun()
            else:
                st.error("密码错误")

    with tab2:
        st.subheader("注册")
        username = st.text_input("用户名")
        name = st.text_input("姓名")
        email = st.text_input("邮箱")
        phone_reg = st.text_input("注册手机号")
        password_reg = st.text_input("注册密码", type="password")

        if st.button("注册"):
            if not all([username, name, email, phone_reg, password_reg]):
                st.warning("请填写所有字段")
                return

            conn = get_mysql_connection()
            c = conn.cursor()
            try:
                hashed_pwd = hash_password(password_reg)
                c.execute("""
                    INSERT INTO users (username, name, email, phonenumber, password, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (username, name, email, phone_reg, hashed_pwd, datetime.now()))
                conn.commit()
                st.success("注册成功，请返回登录")
            except mysql.connector.IntegrityError:
                st.error("用户名或手机号已存在")
            finally:
                c.close()
                conn.close()

# ------------------- 页面控制 -------------------
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

elif st.session_state.page == "login":
    if cookie_manager.get("login_status") == "login":
        phone = cookie_manager.get("login_user", "")
        conn = get_mysql_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE phonenumber = %s", (phone,))
        user = c.fetchone()
        if user:
            st.session_state.logged_in = True
            st.session_state.user_info = {
                "id": user[0],
                "username": user[1],
                "name": user[2],
                "email": user[4],
                "phonenumber": user[5]
            }
            st.session_state.page = "home"
            st.rerun()
    else:
        login_page()

elif st.session_state.page == "home":
    # 顶部退出按钮
    st.markdown('<div class="header-right">', unsafe_allow_html=True)
    if st.columns([8, 2])[1].button("退出登录", key="logout_btn"):
        logout()
        st.session_state.page = "intro"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    with st.sidebar:
        st_lottie(load_lottie("./assets/ai_resume.json"), height=90)
        selected = option_menu(
            "导航栏",
            ["首页", "职位管理", "简历管理", "简历分析", "HR", "我的主页", "API配置"],
            icons=['house', 'person-badge', 'upload', 'search', 'person-workspace', 'person-circle', 'gear'],
            menu_icon="cast",
            default_index=0
        )

        if st.session_state.get("user_info"):
            user = st.session_state.user_info
            load_css("./styles/sidebar_profile.css")
            st.markdown(f"""
                <div class="profile-box">
                    <div class="profile-header">
                        <img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png">
                        <strong>{user['username']}</strong>
                    </div>
                    <div class="profile-phone">📱 {user['phonenumber']}</div>
                </div>
            """, unsafe_allow_html=True)

    user = st.session_state.user_info
    phonenumber = user.get("phonenumber", None)
    username = user.get("username", None)

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
