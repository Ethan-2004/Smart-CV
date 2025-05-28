import streamlit as st
import mysql.connector
import hashlib
import os
from streamlit_cookies_manager import EncryptedCookieManager
from datetime import datetime

cookies = EncryptedCookieManager(
    prefix="app_auth/",
    password=os.environ.get("COOKIE_SECRET", "super_secret_cookie_password")
)

if not cookies.ready():
    st.stop()

from oputils.db_config import DB_CONFIG

def get_mysql_connection():
    return mysql.connector.connect(**DB_CONFIG)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user():
    st.subheader("注册")
    username = st.text_input("用户名")
    name = st.text_input("姓名")
    email = st.text_input("邮箱")
    phonenumber = st.text_input("手机号")
    password = st.text_input("密码", type="password")

    if st.button("注册"):
        if not all([username, name, email, phonenumber, password]):
            st.warning("请填写所有字段")
            return

        conn = get_mysql_connection()
        c = conn.cursor()
        try:
            c.execute("""
                INSERT INTO users (username, name, email, phonenumber, password, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (username, name, email, phonenumber, hash_password(password), datetime.now().isoformat()))
            conn.commit()
            st.success("注册成功，请返回登录")
        except mysql.connector.IntegrityError:
            st.error("用户名或手机号已存在")
        finally:
            c.close()
            conn.close()

def login():
    st.subheader("登录")
    username = st.text_input("用户名", key="login_username")
    password = st.text_input("密码", type="password", key="login_password")

    if st.button("登录"):
        conn = get_mysql_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, hash_password(password)))
        user = c.fetchone()
        c.close()
        conn.close()

        if user:
            st.session_state.logged_in = True
            st.session_state.user_info = {
                "id": user[0],
                "username": user[1],
                "name": user[2],
                "email": user[4],
                "phonenumber": user[5]
            }
            cookies["session_user"] = username
            cookies.save()
            st.session_state.page = "home"
            st.rerun()
        else:
            st.error("用户名或密码错误")

def auto_login():
    # st.write("当前 Cookie 内容：", dict(cookies))
    session_user = cookies.get("session_user")
    if session_user:
        conn = get_mysql_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=%s", (session_user,))
        user = c.fetchone()
        c.close()
        conn.close()

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

def logout():
    st.sidebar.markdown("---")
    if st.sidebar.button("退出登录", use_container_width=True):

        cookies.clear()
        cookies.save()

        st.session_state.logged_in = False
        st.session_state.user_info = {}
        st.success("您已退出登录")
        st.rerun()
