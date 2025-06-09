from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import shutil
import os
import uuid
import uvicorn
import asyncio
from . import doc_convert_handle
from . import doc_convert
from app.common.response import ResponseHandler


app = FastAPI()

# 用于存储文件ID和文件名的映射
UPLOAD_DIR = "doc_local_store"

@app.get("/")
async def root():
    return ResponseHandler.success(message="Hello World")

@app.get("/hello/{name}")
async def say_hello(name: str):

    return ResponseHandler.success({"message": f"Hello {name}"})


class FileTransformRequest(BaseModel):
    fileId: str

@app.post("/api/file-transform/create-async")
async def create_async_transform(request: FileTransformRequest):
    task_id = str(uuid.uuid4())
    fileId = request.fileId

    # 在后台启动异步转换任务
    asyncio.create_task(doc_convert_handle.convert_file_to_md(fileId, task_id))

    return ResponseHandler.success({
        "status": "processing",
        "taskId": task_id
    })


@app.post("/api/file-transform/create")
async def file_transform(file: UploadFile = File(...)):
    try:
        # 生成唯一的文件ID
        file_id = str(uuid.uuid4())

        # 获取文件后缀名
        _, file_extension = os.path.splitext(file.filename)

        # 创建文件ID对应的目录
        file_dir = os.path.join(UPLOAD_DIR, file_id)
        os.makedirs(file_dir, exist_ok=True)

        # 构建文件保存路径（使用原始文件名）
        file_location = os.path.join(file_dir, file.filename)

        # 保存文件
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)

        # 调用文档转换服务
        output_dir = doc_convert.local_file_convert(file_location, file_id)

        # 在输出目录中查找 markdown 文件
        md_content = ""
        for file_name in os.listdir(output_dir):
            if file_name.endswith('.md'):
                md_file_path = os.path.join(output_dir, file_name)
                with open(md_file_path, 'r', encoding='utf-8') as md_file:
                    md_content = md_file.read()
                break

        if not md_content:
            return ResponseHandler.failed("No markdown content generated")

        return ResponseHandler.success({
            "file_id": file_id,
            "filename": file.filename,
            "extension": file_extension,
            "content": md_content
        })

    except Exception as e:
        print(f"处理失败: {str(e)}")
        return ResponseHandler.error(str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8008)
