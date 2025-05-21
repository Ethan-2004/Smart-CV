from streamlit_option_menu import option_menu
import streamlit as st
from streamlit_lottie import st_lottie
import os
import json
from Component.Display.style_load import load_css, load_lottie

def load_lottie_file(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def display_homepage():
    load_css("./styles/home.css")

    # st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.title('🎉 欢迎来到智能简历优化平台')
    st.markdown("""
        <div class="light-green-text">
        本平台致力于通过AI技术帮助你更高效地提升简历质量，实现更优的岗位匹配与推荐。
        </div>
        """, unsafe_allow_html=True)

    st.write("---")
    col1, col2 = st.columns([1, 1])

    with col1:
        
        # st.markdown(f'<div class="sub-text">👋 你好，<strong>{st.session_state.user_info.get("name", "访客")}</strong>！</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="sub-text">
        
        <h4>🔍 功能一览：</h4>
        
        <br>
        
        📄 简历上传与管理<br>
        
        🤖 智能简历分析与评分<br>
        
        💡 岗位匹配推荐<br>
        
        🎯 标签与关键词标注<br>
        
        🧠 AI辅助内容优化与建议<br>
        
        📊 历史记录与趋势追踪
        
        </div>
        """, unsafe_allow_html=True)

    with col2:
        lottie_path = os.path.join("assets", "home.json")
        if os.path.exists(lottie_path):
            st_lottie(load_lottie_file(lottie_path), speed=1, height=320, key="ai_animation")
        else:
            st.image("https://cdn-icons-png.flaticon.com/512/4285/4285406.png", width=280)



    # 模块切换
    st.write("---")
    st.markdown('<div class="section-title">🚀 平台核心模块</div>', unsafe_allow_html=True)

    selected = option_menu(
        menu_title=None,
        options=["📂 简历管理", "🧠 AI智能分析", "💼 岗位匹配"],
        orientation="horizontal",
        styles={
            "container": {"margin": "0px !important"},
            "nav-link-selected": {"background-color": "#f0f2f6", "font-weight": "bold"},
        }
    )

    # 公共样式
    gray_text_style = "style='color: gray; font-size: 1.05rem; text-align: center;'"
    title_style = "style='text-align: center; font-weight: bold;'"

    if selected == "📂 简历管理":
        with st.container():
            st_lottie(load_lottie_file("assets/resume.json"), height=300, key="resume_anim")
            st.markdown(f"<h4 {title_style}>📂 简历管理</h4>", unsafe_allow_html=True)
            st.markdown(f"<p {gray_text_style}>上传、预览和筛选你的简历，一目了然地管理多份文档。</p>", unsafe_allow_html=True)

    elif selected == "🧠 AI智能分析":
        with st.container():
            st_lottie(load_lottie_file("assets/analysis.json"), height=300, key="ai_analysis_anim")
            st.markdown(f"<h4 {title_style}>🧠 AI智能分析</h4>", unsafe_allow_html=True)
            st.markdown(f"<p {gray_text_style}>通过大模型对简历内容进行语义理解、打分与优化建议。</p>", unsafe_allow_html=True)

    elif selected == "💼 岗位匹配":
        with st.container():
            st_lottie(load_lottie_file("assets/match.json"), height=300, key="match_anim")
            st.markdown(f"<h4 {title_style}>💼 岗位匹配</h4>", unsafe_allow_html=True)
            st.markdown(f"<p {gray_text_style}>根据简历关键词与岗位描述匹配，精准推荐适配岗位。</p>", unsafe_allow_html=True)



