# oputils.py
import json
import streamlit as st

def load_lottie(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def load_css(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
