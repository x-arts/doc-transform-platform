import subprocess
import os

def convert_pdf(input_file: str, output_path: str) -> bool:
    """
    将文档转换为PDF格式

    Args:
        input_file (str): 输入word文件的路径
        output_path (str): PDF输出目录的路径

    Returns:
        bool: 转换成功返回True，失败返回False
    """
    try:
        # 确保输出目录存在
        os.makedirs(output_path, exist_ok=True)

        # 执行转换命令
        result = subprocess.run([
            'soffice',
            '--headless',
            '--convert-to',
            'pdf',
            input_file,
            '--outdir',
            output_path
        ], capture_output=True, text=True)

        return result.returncode == 0
    except Exception as e:
        print(f"转换过程中出现错误: {str(e)}")
        return False
