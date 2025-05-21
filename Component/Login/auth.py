# # # auth.py
# # import streamlit as st
# # import streamlit_authenticator as stauth
# # import yaml
# # from yaml.loader import SafeLoader
# # from streamlit_authenticator import LoginError, ForgotError

# # def login_register():
# #     with open('config.yaml', 'r', encoding='utf-8') as file:
# #         config = yaml.load(file, Loader=SafeLoader)

# #     authenticator = stauth.Authenticate(
# #         config['credentials'],
# #         config['cookie']['name'],
# #         config['cookie']['key'],
# #         config['cookie']['expiry_days']
# #     )

# #     if 'authentication_status' not in st.session_state:
# #         st.session_state['authentication_status'] = None

# #     tab1, tab2 = st.tabs(["登录", "注册"])
    
# #     # 登录页面
# #     with tab1:
# #         try:
# #             authenticator.login()
# #         except LoginError as e:
# #             st.error(e)

# #         if st.session_state["authentication_status"]:
# #             st.success(f"欢迎 {st.session_state['name']}，登录成功")
# #             st.session_state.page = "home"
# #             st.rerun()
# #         elif st.session_state["authentication_status"] is False:
# #             st.error("用户名或密码错误")
# #         elif st.session_state["authentication_status"] is None:
# #             st.warning("请输入用户名和密码")

# #         with st.expander("忘记密码？"):
# #             try:
# #                 username, email, new_password = authenticator.forgot_password()
# #                 if username:
# #                     st.success("新密码已发送")
# #                 elif username is False:
# #                     st.error("找不到该用户")
# #             except Exception as e:
# #                 st.error(e)

# #     with tab2:
# #         try:
# #             phonenumber = st.text_input("手机号")
# #             email, username, name = authenticator.register_user()
            
# #             if email:
# #                 st.success("注册成功，请返回登录")
# #                 st.session_state["phonenumber"] = phonenumber

# #                 # 保存手机号进数据库
# #                 import sqlite3
# #                 conn = sqlite3.connect("jobs.db")
# #                 cursor = conn.cursor()
# #                 cursor.execute('''
# #                     INSERT INTO users (username, name, email, phonenumber)
# #                     VALUES (?, ?, ?, ?)
# #                 ''', (username, name, email, phonenumber))
# #                 conn.commit()
# #                 conn.close()

# #                 # 保存到 config.yaml
# #                 with open('config.yaml', 'w', encoding='utf-8') as file:
# #                     yaml.dump(config, file, default_flow_style=False, allow_unicode=True)
# #         except ForgotError as e:
# #             st.error(e)

# # auth_cookie.py
# import streamlit as st
# import sqlite3
# import hashlib
# import os
# from streamlit_cookies_manager import EncryptedCookieManager
# from datetime import datetime

# # 初始化 Cookie 管理器
# cookies = EncryptedCookieManager(
#     prefix="app_auth/",
#     password=os.environ.get("COOKIE_SECRET", "super_secret_cookie_password")
# )

# if not cookies.ready():
#     st.stop()

# DB_NAME = "jobs.db"

# def hash_password(password):
#     return hashlib.sha256(password.encode()).hexdigest()

# # def init_db():
# #     conn = sqlite3.connect(DB_NAME)
# #     c = conn.cursor()
# #     c.execute("PRAGMA foreign_keys = ON;")
# #     c.execute("""
# #     CREATE TABLE IF NOT EXISTS users (
# #         id INTEGER PRIMARY KEY AUTOINCREMENT,
# #         username TEXT UNIQUE,
# #         name TEXT,
# #         email TEXT,
# #         phonenumber TEXT UNIQUE,
# #         password TEXT,
# #         created_at TEXT
# #     );
# #     """)
# #     conn.commit()
# #     conn.close()

# def register_user():
#     st.subheader("注册")
#     username = st.text_input("用户名")
#     name = st.text_input("姓名")
#     email = st.text_input("邮箱")
#     phonenumber = st.text_input("手机号")
#     password = st.text_input("密码", type="password")

#     if st.button("注册"):
#         if not all([username, name, email, phonenumber, password]):
#             st.warning("请填写所有字段")
#             return

#         conn = sqlite3.connect(DB_NAME)
#         c = conn.cursor()
#         try:
#             c.execute("INSERT INTO users (username, name, email, phonenumber, password, created_at) VALUES (?, ?, ?, ?, ?, ?)",
#                     (username, name, email, phonenumber, hash_password(password), datetime.now().isoformat()))
#             conn.commit()
#             st.success("注册成功，请返回登录")
#         except sqlite3.IntegrityError:
#             st.error("用户名或手机号已存在")
#         finally:
#             conn.close()

# def login():
#     st.subheader("登录")
#     username = st.text_input("用户名", key="login_username")
#     password = st.text_input("密码", type="password", key="login_password")

#     if st.button("登录"):
#         conn = sqlite3.connect(DB_NAME)
#         c = conn.cursor()
#         c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hash_password(password)))
#         user = c.fetchone()
#         conn.close()

#         if user:
#             st.session_state.logged_in = True
#             st.session_state.user_info = {
#                 "id": user[0],
#                 "username": user[1],
#                 "name": user[2],
#                 "email": user[4],
#                 "phonenumber": user[5]
#             }
#             cookies["session_user"] = username
#             cookies.save()
#             st.session_state.page = "home"
#             st.rerun()
#         else:
#             st.error("用户名或密码错误")

# def auto_login():
#     st.write("当前 Cookie 内容：", dict(cookies))
#     session_user = cookies.get("session_user")
#     if session_user:
#         conn = sqlite3.connect(DB_NAME)
#         c = conn.cursor()
#         c.execute("SELECT * FROM users WHERE username=?", (session_user,))
#         user = c.fetchone()
#         conn.close()
#         if user:
#             print(user)
#             st.session_state.logged_in = True
#             st.session_state.user_info = {
#                 "id": user[0],
#                 "username": user[1],
#                 "name": user[2],
#                 "email": user[4],
#                 "phonenumber": user[5]
#             }
#         st.session_state.page = "home"
#         st.rerun()

# def logout():
#     st.sidebar.markdown("---")
#     if st.sidebar.button("退出登录", use_container_width=True):
#         # 删除当前会话中所有的 Cookie
#         cookies.clear()  # ⚠️ 更保险的方法，删除所有 app_auth/ 前缀的 Cookie
#         cookies.save()   # ⚠️ 别忘了保存变更

#         # 清空 session_state 中的登录信息
#         st.session_state.logged_in = False
#         st.session_state.user_info = {}
#         st.success("您已退出登录")
#         st.rerun()




