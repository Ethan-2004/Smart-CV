#!/bin/bash

# 激活conda环境
source /root/miniconda3/bin/activate smartcv_venv

# 进入项目目录
cd /var/www/SmartResumesV4

# 启动streamlit服务
streamlit run main.py --server.port 8501 --server.headless true
