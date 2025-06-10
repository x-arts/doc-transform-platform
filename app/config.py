import os
from typing import Dict, Any

# 尝试从环境变量获取配置，如果没有则使用默认值
config: Dict[str, Any] = {
    # Redis 配置
    'REDIS': {
        'HOST': os.getenv('REDIS_HOST', '47.119.16.20'),
        'PORT': int(os.getenv('REDIS_PORT', 6379)),
        'DB': int(os.getenv('REDIS_DB', 0)),
        'PASSWORD': os.getenv('REDIS_PASSWORD', '123456'),
    },

    # 文件服务配置
    'FILE_SERVICE': {
        'BASE_URL': os.getenv('FILE_SERVICE_URL', 'http://localhost:8000'),
        'UPLOAD_ENDPOINT': '/api/files/upload',
        'DOWNLOAD_ENDPOINT': '/api/files/download/{file_id}',
    }
}
