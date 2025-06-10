import requests
from pathlib import Path


def get_file_by_id(file_id: str) -> str:
    # 创建存储目录
    store_dir = Path("doc_cloud_store")
    store_dir.mkdir(exist_ok=True)

    # 从配置文件获取 API URL
    # file_service_config = config['FILE_SERVICE']
    api_url = f"http://47.119.16.20:8000/api/files/download/{file_id}"

    # 发送GET请求获取文件
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # 检查响应状态

        # 从响应头获取文件名，如果没有则使用file_id作为文件名
        filename = response.headers.get(
            'content-disposition',
            f'filename={file_id}'
        ).split('filename=')[-1]

        # 清理文件名中的双引号
        filename = filename.replace('"', '')

        # 构建保存路径
        file_path = store_dir / filename

        # 保存文件
        with open(file_path, 'wb') as f:
            f.write(response.content)

        return str(file_path.absolute())

    except requests.RequestException as e:
        raise Exception(f"获取文件失败: {str(e)}")


def upload_file(file_path: str) -> str:
    """
    上传文件到服务器
    :param file_path: 本地文件路径
    :return: 返回服务器端的文件ID
    """
    # 从配置文件获取上传 API URL
    # file_service_config = config['FILE_SERVICE']
    api_url = "http://47.119.16.20:8000/api/files/upload"

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
        if 'fileId' not in result:
            raise Exception("上传响应中未包含fileId")

        return result['fileId']

    except requests.RequestException as e:
        raise Exception(f"文件上传失败: {str(e)}")
    finally:
        # 确保文件被关闭
        if 'files' in locals() and 'file' in files:
            files['file'][1].close()

