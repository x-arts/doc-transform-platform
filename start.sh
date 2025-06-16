#!/bin/bash

# 确保使用 bash
if [ -n "$BASH_VERSION" ]; then
    # 获取conda的安装路径并初始化
    CONDA_PATH=$(dirname $(dirname $(which conda)))
    . "$CONDA_PATH/etc/profile.d/conda.sh"

    # 进入项目目录
    cd /root/autodl-tmp/app-server/doc-transform-platform

    # 初始化 conda
    conda init bash

    # 刷新 bash 配置
    source ~/.bashrc

    # 激活 conda 环境
    conda activate mineru

    # 设置 Python 路径
    export PYTHONPATH=.

    # 启动应用
    python app/main.py
else
    echo "请使用 bash 运行此脚本"
    exit 1
fi
