import asyncio
from . import file_store
from . import doc_convert
from . import message_push
import os


async def convert_file_to_md(file_id: str, task_id: str):
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
