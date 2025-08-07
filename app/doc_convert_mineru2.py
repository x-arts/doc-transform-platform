import os
from pathlib import Path

from magic_pdf.data.data_reader_writer import FileBasedDataWriter, FileBasedDataReader
from magic_pdf.data.dataset import PymuDocDataset
from magic_pdf.model.doc_analyze_by_custom_model import doc_analyze
from magic_pdf.config.enums import SupportedPdfParseMethod
import requests


API_HOST = "http://127.0.0.1:8008"


def api_parse_document(file_path,uuid: str = ""):
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

    # read bytes
    reader1 = FileBasedDataReader("")
    pdf_bytes = reader1.read(pdf_file_name)  # read the pdf content

    # proc
    ## Create Dataset Instance
    ds = PymuDocDataset(pdf_bytes)

    ## inference
    if ds.classify() == SupportedPdfParseMethod.OCR:
        print("Using OCR for PDF parsing...")
        infer_result = ds.apply(doc_analyze, ocr=True)

        ## pipeline
        pipe_result = infer_result.pipe_ocr_mode(image_writer)

    else:
        print("Using PDF for PDF parsing...")
        infer_result = ds.apply(doc_analyze, ocr=False)

        ## pipeline
        pipe_result = infer_result.pipe_txt_mode(image_writer)

    ### draw model result on each page
    infer_result.draw_model(os.path.join(local_md_dir, f"{name_without_suff}_model.pdf"))
    print("Converting to PDF...")

    ### get model inference result
    model_inference_result = infer_result.get_infer_res()

    ### draw layout result on each page
    pipe_result.draw_layout(os.path.join(local_md_dir, f"{name_without_suff}_layout.pdf"))

    ### draw spans result on each page
    pipe_result.draw_span(os.path.join(local_md_dir, f"{name_without_suff}_spans.pdf"))

    ### get markdown content
    md_content = pipe_result.get_markdown(image_dir)

    ### dump markdown
    pipe_result.dump_md(md_writer, f"{name_without_suff}.md", image_dir)

    ### get content list content
    content_list_content = pipe_result.get_content_list(image_dir)

    ### dump content list
    pipe_result.dump_content_list(md_writer, f"{name_without_suff}_content_list.json", image_dir)

    ### get middle json
    middle_json_content = pipe_result.get_middle_json()

    ### dump middle json
    pipe_result.dump_middle_json(md_writer, f'{name_without_suff}_middle.json')

    # 返回输出目录的绝对路径
    return str(output_dir.absolute())

