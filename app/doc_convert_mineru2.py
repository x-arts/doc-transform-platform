import os
import json
from pathlib import Path

from magic_pdf.data.data_reader_writer import FileBasedDataWriter
import requests


API_HOST = "http://127.0.0.1:8007"


def save_content_to_file(content: str, file_path: Path, content_type: str = ""):
    """
    将内容保存到指定文件
    
    Args:
        content: 要保存的内容
        file_path: 保存的文件路径
        content_type: 内容类型（用于日志）
    """
    try:
        # 确保父目录存在
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 如果内容是字符串形式的JSON，先格式化它
        if str(file_path).endswith('.json') and isinstance(content, str):
            try:
                # 尝试解析JSON并格式化
                json_data = json.loads(content)
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
            except json.JSONDecodeError:
                # 如果不是有效的JSON，直接写入
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
        else:
            # 普通文本文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
        print(f"{content_type} 已保存到: {file_path}")
        return True
    except Exception as e:
        print(f"保存 {content_type} 到 {file_path} 时出错: {e}")
        return False


def api_parse_document(file_path):
    """
    调用 MinerU API 解析文档
    """

    url = f"{API_HOST}/file_parse"

    # 准备文件
    with open(file_path, 'rb') as f:
        files = {'files': (file_path, f, 'application/pdf')}

        # 请求参数
        data = {
            'output_dir': '/root/autodl-tmp/api-out-file/',
            'lang_list': ['ch'],  # 中文
            'backend': 'vlm-sglang-engine',
            'parse_method': 'auto',
            'formula_enable': True,
            'table_enable': False,
            'return_md': True,
            'return_middle_json': True,
            'return_model_output': True,
            'return_content_list': True,
            'return_images': False
        }

        # 发送请求
        response = requests.post(url, files=files, data=data)

        if response.status_code == 200:
            result = response.json()
            #  middle_json  md_content   content_list

            print(f"请求成功  result: {result}")
            print(f"请求成功  result-middle_json: {result['results']['1']['middle_json']}")
            return result
        else:
            print(f"请求失败: {response.status_code}")
            print(response.text)
            return None


        # 本地的文件转换 使用 minerU 转换 markdown
def local_file_convert(file_path: str, uuid: str = "") -> str:
    # 获取当前文件的目录作为基础路径
    base_dir = Path(os.path.dirname(os.path.abspath(__file__)))

    # args
    pdf_file_name = file_path
    name_without_suff = Path(pdf_file_name).stem  # 使用 Path 来更安全地获取文件名

    # prepare env
    output_dir = base_dir / "output"
    if uuid:
        output_dir = output_dir / uuid
    local_image_dir = output_dir / "images"
    local_md_dir = output_dir
    image_dir = "images"  # 这个是相对路径，用于 markdown 文件中的图片引用

    # 确保两个目录都存在
    output_dir.mkdir(parents=True, exist_ok=True)
    local_image_dir.mkdir(parents=True, exist_ok=True)

    print(f"输出目录: {output_dir}")
    print(f"图片目录: {local_image_dir}")

    image_writer = FileBasedDataWriter(str(local_image_dir))
    md_writer = FileBasedDataWriter(str(local_md_dir))

    parse_result = api_parse_document(file_path)
    middle_json_str  = parse_result['results']['1']['middle_json']

    md_content_str = parse_result['results']['1']['md_content']

    content_list_str = parse_result['results']['1']['content_list']

    # 使用新的函数保存文件内容
    middle_json_file_path = output_dir / f"{name_without_suff}_middle.json"
    save_content_to_file(middle_json_str, middle_json_file_path, "middle_json")

    md_file_path = output_dir / f"{name_without_suff}.md"
    save_content_to_file(md_content_str, md_file_path, "markdown 内容")

    content_list_file_path = output_dir / f"{name_without_suff}_content_list.json"
    save_content_to_file(content_list_str, content_list_file_path, "content_list")

    # 返回输出目录的绝对路径
    return str(output_dir.absolute())

