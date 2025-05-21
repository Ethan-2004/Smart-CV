#!/bin/bash

# 1. 更新系统
sudo apt update && sudo apt upgrade -y

# 2. 安装依赖工具
sudo apt install -y wget git unzip nginx

# 3. 安装 Miniconda（Python 3 最新版）
MINICONDA=Miniconda3-latest-Linux-x86_64.sh
wget https://repo.anaconda.com/miniconda/$MINICONDA -O /tmp/$MINICONDA
bash /tmp/$MINICONDA -b -p $HOME/miniconda
rm /tmp/$MINICONDA

# 4. 初始化 conda 命令
eval "$($HOME/miniconda/bin/conda shell.bash hook)"

# 5. 创建并激活 conda 环境
conda create -y -n smartcv_env python=3.11
conda activate smartcv_env

# 6. 安装Python依赖（假设你项目有requirements.txt）
# 如果没有，你可以替换为具体的包名列表，例如：pip install streamlit sqlalchemy pymysql matplotlib python-docx pypdf2
if [ ! -d "$HOME/SmartResumesV4" ]; then
  git clone https://github.com/yourusername/SmartResumesV4.git $HOME/SmartResumesV4
fi
pip install --upgrade pip
pip install -r $HOME/SmartResumesV4/requirements.txt

# 7. 启动 Streamlit 应用（后台运行）
# 先杀掉已有的占用8501端口的进程，避免冲突
sudo fuser -k 8501/tcp || true

# 使用 nohup 保证关闭终端后也继续运行
nohup streamlit run $HOME/SmartResumesV4/main.py --server.port=8501 --server.headless=true > $HOME/streamlit.log 2>&1 &

# 8. 配置 Nginx 反向代理 Streamlit

sudo tee /etc/nginx/sites-available/smartresumes <<EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:8501/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
EOF

# 9. 启用配置
sudo ln -sf /etc/nginx/sites-available/smartresumes /etc/nginx/sites-enabled/

# 10. 测试Nginx配置是否正确
sudo nginx -t

# 11. 重启Nginx
sudo systemctl restart nginx

echo "部署完成！请通过服务器IP访问：http://your-server-ip/"
