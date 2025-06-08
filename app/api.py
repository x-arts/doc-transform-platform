

from fastapi.responses import FileResponse
from fastapi import FastAPI, UploadFile, File, Body
from pydantic import BaseModel
import shutil
import os
import uuid
import uvicorn
import file_store
import doc_convert
import message_push


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
    fileId = request.fileId
    print(fileId)
    file_pah =  file_store.get_file_by_id(fileId)
    print(file_pah)

    doc_convert.local_file_convert(file_pah, fileId)


    return {
        "status": "success",
        "fileId": request.fileId,
        "message": "File transform task created"
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
