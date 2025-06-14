import asyncio
import os

from app import message_push, file_store, doc_convert, docx_convert_pdf
from app.view.miner_u_result_file import MinerUResultFile, SOfficeResultFile

# 将 Word 文档转换为 PDF 并获取信息
def convert_word_to_pdf_info(file_id: str) -> SOfficeResultFile:
    # 下载好的文件路径
    file_path = file_store.get_file_by_id(file_id)

    print("file_path is", file_path)

    # 转换文件
    bool = docx_convert_pdf.convert_pdf(file_path)

    print("bool is", bool)

    # 从根目录开始获取 output_dir
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(root_dir, 'soffice', 'pdf')

    print("output_dir is", output_dir)

    # 获取原始文件名（不带后缀）
    original_filename = os.path.splitext(os.path.basename(file_path))[0]
    expected_pdf_name = original_filename + '.pdf'

    print("expected_pdf_name is", expected_pdf_name)

    # 直接查找对应的PDF文件
    pdf_file_path = os.path.join(output_dir, expected_pdf_name)

    print("pdf_file_path is", pdf_file_path)

    sOfficeRes = SOfficeResultFile()
    if os.path.exists(pdf_file_path):
        pdf_file_id = file_store.upload_file(pdf_file_path)
        sOfficeRes.pdf_file_id = pdf_file_id

    return sOfficeRes


#  pdf 转换为 markdown 并获取信息
def convert_pdf_to_md_info(file_id: str) -> MinerUResultFile:
    # 下载好的文件路径
    file_path = file_store.get_file_by_id(file_id)

    # 转换文件的 out 目录
    output_dir = doc_convert.local_file_convert(file_path,file_id)

    minerURes = MinerUResultFile()

    for file_name in os.listdir(output_dir):
        if file_name.endswith('.md'):
            md_file_path = os.path.join(output_dir, file_name)
            markdown_file_id = file_store.upload_file(md_file_path)
            minerURes.md_file_id = markdown_file_id
        if file_name.endswith('middle.json'):
            middle_file_path = os.path.join(output_dir, file_name)
            middle_file_id = file_store.upload_file(middle_file_path)
            minerURes.middle_file_id = middle_file_id

        if file_name.endswith('content_list.json'):
            content_list_file_path = os.path.join(output_dir, file_name)
            content_list_file_id = file_store.upload_file(content_list_file_path)
            minerURes.content_list_file_id = content_list_file_id

    return minerURes



async def convert_pdf_to_md(file_id: str, task_id: str):
    """
    异步处理文件转换任务
    :param file_id: 原始文件ID
    :param task_id: 任务ID
    """
    try:
        # 发送开始处理的消息
        message_push.push_task_message({
            "taskId": task_id,
            "status": "processing",
            "fileId": file_id
        })

        # 使用 run_in_executor 在线程池中执行同步操作
        loop = asyncio.get_event_loop()

        # 下载文件
        file_path = await loop.run_in_executor(None, file_store.get_file_by_id, file_id)

        # 转换文件
        output_dir = await loop.run_in_executor(None, doc_convert.local_file_convert, file_path, task_id)

        # 查找生成的 markdown 文件
        md_file = None
        for file in os.listdir(output_dir):
            if file.endswith('.md'):
                md_file = os.path.join(output_dir, file)
                break

        if not md_file:
            raise Exception("No markdown file generated")

        # 上传转换后的文件
        markdown_file_id = await loop.run_in_executor(None, file_store.upload_file, md_file)

        # 发送完成消息
        message_push.push_task_message({
            "taskId": task_id,
            "status": "success",
            "fileId": markdown_file_id
        })

    except Exception as e:
        print(f"转换失败: {str(e)}")
        # 发送错误消息
        message_push.push_task_message({
            "taskId": task_id,
            "status": "failed",
            "fileId": file_id
        })
        raise
