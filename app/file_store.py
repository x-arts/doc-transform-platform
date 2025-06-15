import requests
from pathlib import Path
import urllib.parse

# API服务器地址配置
API_HOST = "http://127.0.0.1:8000"


def get_file_by_id(file_id: str) -> str:
    # 创建存储目录
    store_dir = Path("doc_cloud_store")
    store_dir.mkdir(exist_ok=True)

    api_url = f"{API_HOST}/api/files/download/{file_id}"
    print(f"开始下载文件，URL: {api_url}")

    # 发送GET请求获取文件
    try:
        response = requests.get(api_url)

        # 打印响应状态和内容以便调试
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {response.headers}")
        if response.status_code != 200:
            print(f"响应内容: {response.text}")

        response.raise_for_status()  # 检查响应状态

        # 从响应头获取文件名，如果没有则使用file_id作为文件名
        content_disposition = response.headers.get('content-disposition', f'filename={file_id}')

        # 处理 filename* 格式
        if 'filename*=' in content_disposition:
            filename = content_disposition.split("filename*=")[-1]
            # 处理 UTF-8 编码的文件名
            if filename.startswith("utf-8''"):
                filename = filename[7:]  # 移除 utf-8'' 前缀
            filename = urllib.parse.unquote(filename)
        else:
            # 处理普通 filename 格式
            filename = content_disposition.split('filename=')[-1]
            filename = filename.replace('"', '')
            filename = urllib.parse.unquote(filename)

        # 构建保存路径
        file_path = store_dir / filename

        # 保存文件
        with open(file_path, 'wb') as f:
            f.write(response.content)

        return str(file_path.absolute())

    except requests.RequestException as e:
        error_msg = f"获取文件失败: 状态码: {getattr(e.response, 'status_code', 'N/A')}, 错误信息: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            error_msg += f", 响应内容: {e.response.text}"
        raise Exception(error_msg)


def upload_file(file_path: str) -> str:
    """
    上传文件到服务器
    :param file_path: 本地文件路径
    :return: 返回服务器端的文件ID
    """
    api_url = f"{API_HOST}/api/files/upload"

    try:
        # 检查文件是否存在
        if not Path(file_path).exists():
            raise Exception(f"文件不存在: {file_path}")

        # 准备文件数据
        files = {
            'file': (
                Path(file_path).name,
                open(file_path, 'rb'),
                'application/octet-stream'
            )
        }

        # 发送POST请求上传文件
        response = requests.post(api_url, files=files)
        response.raise_for_status()
        print("上传相应:", response)

        # 解析响应获取文件ID
        result = response.json()
        print(result)
        if not result.get('data') or 'fileId' not in result['data']:
            raise Exception("上传响应中未包含fileId")

        return result['data']['fileId']

    except requests.RequestException as e:
        raise Exception(f"文件上传失败: {str(e)}")
    finally:
        # 确保文件被关闭
        if 'files' in locals() and 'file' in files:
            files['file'][1].close()
