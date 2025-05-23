#!/bin/bash

# 脚本必须用 root 或 sudo 执行

# 设置变量
ENV_NAME="smartcv_venv"
CONDA_PATH="/root/miniconda3"
PROJECT_DIR="/var/www/SmartResumesV4"
GIT_REPO="https://github.com/你的账号/SmartResumesV4.git"
PYTHON_VERSION="3.11"
PORT=8501

echo "🔧 安装基本工具..."
apt update -y
apt install -y wget git unzip nginx

echo "📦 安装 Miniconda..."
cd /root
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
bash miniconda.sh -b -p $CONDA_PATH
eval "$($CONDA_PATH/bin/conda shell.bash hook)"

echo "🐍 创建 Conda 环境: $ENV_NAME"
conda create -y -n $ENV_NAME python=$PYTHON_VERSION
conda activate $ENV_NAME

echo "📁 克隆项目代码..."
rm -rf $PROJECT_DIR
git clone $GIT_REPO $PROJECT_DIR

cd $PROJECT_DIR

echo "📦 安装 Python 依赖..."
pip install -r requirements.txt

echo "🚀 后台运行 Streamlit..."
nohup streamlit run main.py --server.port $PORT --server.headless true > streamlit.log 2>&1 &

echo "🌐 配置 nginx（如果你已有配置文件）"
if [ -f /etc/nginx/sites-available/smartresumes ]; then
    ln -sf /etc/nginx/sites-available/smartresumes /etc/nginx/sites-enabled/
    nginx -t && systemctl restart nginx
else
    echo "⚠️ 未找到 nginx 配置文件，请手动配置 /etc/nginx/sites-available/smartresumes"
fi

echo "✅ 部署完成！"
echo "👉 打开浏览器访问：http://你的公网IP:$PORT"
