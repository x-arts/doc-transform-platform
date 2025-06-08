from fastapi import FastAPI, UploadFile, File, Body
from pydantic import BaseModel
import shutil
import os
import uuid
import uvicorn
import doc_convert_handle
import message_push
import asyncio


app = FastAPI()

# 用于存储文件ID和文件名的映射

UPLOAD_DIR = "uploads"

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    message = {
        "taskId": "123",
        "status": "processing",
        "fileId": "abc-xyz"
    }
    message_push.push_task_message(message)

    return {"message": f"Hello {name}"}


class FileTransformRequest(BaseModel):
    fileId: str
@app.post("/api/file-transform/create-async")
async def create_async_transform(request: FileTransformRequest):
    task_id = str(uuid.uuid4())
    fileId = request.fileId

    # 在后台启动异步转换任务
    asyncio.create_task(doc_convert_handle.convert_file_to_md(fileId, task_id))

    return {
        "status": "processing",
        "taskId": task_id
    }


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
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

    return {
        "file_id": file_id,
        "filename": file.filename,
        "extension": file_extension
    }



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8008)
