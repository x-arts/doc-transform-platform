# doc-transform-platform
文档转换服务

# 项目运行
1.  拉取项目到本地
```bash
    git clone  https://github.com/x-arts/doc-transform-platform.git
```

2. 安装依赖
```bash
    cd doc-transform-platform
    pip install -r requirements.txt
```
3. 启动项目
```bash
    uvicorn main:app --host 0.0.0.0 --port 8008 --reload
    
    或是后台命令：
    nohup uvicorn app.api:app --host 0.0.0.0 --port 8008 > output.log 2>&1 &
   
```


# 接口说明
## API 接口文档

### 1. 同步文档转换接口

**接口信息：**
- 请求路径：`/api/file-transform/create`
- 请求方法：POST
- Content-Type: multipart/form-data

**请求参数：**
| 参数名 | 类型 | 是否必填 | 说明 |

| file   | File | 是   | 需要转换的文档文件 |

**响应结果：**
```json
{
    "code": 200,
    "data": {
        "file_id": "uuid",
        "filename": "原始文件名",
        "extension": "文件扩展名",
        "content": "转换后的markdown内容"
    },
    "message": "success"
}
```

**错误响应：**
```json
{
    "code": 500,
    "message": "错误信息",
    "data": null
}
```

### 2. 异步文档转换接口

**接口信息：**
- 请求路径：`/api/file-transform/create-async`
- 请求方法：POST
- Content-Type: application/json

**请求参数：**
```json
{
    "fileId": "要转换的文件ID"
}
```

**响应结果：**
```json
{
    "code": 200,
    "data": {
        "status": "processing",
        "taskId": "异步任务ID"
    },
    "message": "success"
}
```

**错误响应：**
```json
{
    "code": 500,
    "message": "错误信息",
    "data": null
}
```

## 使用说明

1. 同步转换接口适用于小文件的快速转换，会直接返回转换结果。
2. 异步转换接口适用于大文件转换，返回任务ID，后续可通过任务ID查询转换进度和结果。
3. 文件ID在上传文件时由系统自动生成，用于在异步接口中指定要转换的文件。

