#!/bin/bash

# 获取conda的安装路径并初始化
CONDA_PATH=$(dirname $(dirname $(which conda)))
source $CONDA_PATH/etc/profile.d/conda.sh

# 进入项目目录
cd /root/autodl-tmp/app-server/doc-transform-platform

# 激活 conda 环境
conda activate mineru

# 设置 Python 路径
export PYTHONPATH=.

# 启动应用
python app/main.py
