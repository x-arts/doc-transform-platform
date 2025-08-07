import unittest
from pathlib import Path
import json
import os
import requests
from app.doc_convert_mineru2 import api_parse_document, local_file_convert


class TestDocConvertMinerU2(unittest.TestCase):
    def setUp(self):
        """测试前的设置"""
        self.test_uuid = "test-uuid-123"
        self.test_pdf_path = "/Users/xuewenke/code/python-project/doc-transform-platform/soffice/pdf/1.pdf"
        self.api_host = "http://127.0.0.1:8008"
        
        # 检查测试文件是否存在
        if not Path(self.test_pdf_path).exists():
            self.skipTest(f"测试PDF文件不存在: {self.test_pdf_path}")
    
    def check_api_server(self):
        """检查API服务是否可用"""
        try:
            response = requests.get(f"{self.api_host}/health", timeout=5)
            return response.status_code == 200
        except:
            return False

    def test_api_parse_document_with_real_pdf(self):
        """测试 api_parse_document 使用真实PDF文件和API"""
        print(f"\n开始测试API解析文档: {self.test_pdf_path}")

        
        # 调用真实的API
        result = api_parse_document(self.test_pdf_path, self.test_uuid)
        
        # 打印结果供查看
        # print(f"API调用结果: {result}")
        
        # 基本验证
        if result is not None:
            print("✅ API调用成功，返回了结果")
            self.assertIsInstance(result, dict, "返回结果应该是字典类型")
        else:
            print("❌ API调用失败，返回None")
            self.fail("API调用失败")

    def test_api_parse_document_with_different_pdfs(self):
        """测试使用不同PDF文件调用API"""
        pdf_files = [
            "/Users/xuewenke/code/python-project/doc-transform-platform/soffice/pdf/1.pdf",
            "/Users/xuewenke/code/python-project/doc-transform-platform/soffice/pdf/车辆购置及维保.pdf"
        ]
        
        # 检查API服务是否可用
        if not self.check_api_server():
            self.skipTest(f"API服务不可用: {self.api_host}")
        
        for pdf_file in pdf_files:
            if Path(pdf_file).exists():
                print(f"\n测试文件: {pdf_file}")
                with self.subTest(pdf_file=pdf_file):
                    result = api_parse_document(pdf_file, f"test-{Path(pdf_file).stem}")
                    print(f"文件 {Path(pdf_file).name} 的解析结果: {result}")
                    
                    if result is not None:
                        print(f"✅ 文件 {Path(pdf_file).name} 解析成功")
                    else:
                        print(f"❌ 文件 {Path(pdf_file).name} 解析失败")

    def test_api_parse_document_without_uuid(self):
        """测试不提供UUID参数的情况"""
        print(f"\n测试不提供UUID参数")
        
        # 检查API服务是否可用
        if not self.check_api_server():
            self.skipTest(f"API服务不可用: {self.api_host}")
        
        # 调用API但不提供UUID
        result = api_parse_document(self.test_pdf_path)
        
        print(f"不提供UUID的API调用结果: {result}")
        
        if result is not None:
            print("✅ 不提供UUID时API调用成功")
            self.assertIsInstance(result, dict, "返回结果应该是字典类型")
        else:
            print("❌ 不提供UUID时API调用失败")

    def test_api_parse_document_with_non_existent_file(self):
        """测试使用不存在的文件"""
        non_existent_file = "/path/to/non_existent_file.pdf"
        
        print(f"\n测试不存在的文件: {non_existent_file}")
        
        # 调用API，应该会抛出文件不存在的异常
        with self.assertRaises(FileNotFoundError):
            api_parse_document(non_existent_file, self.test_uuid)
        
        print("✅ 正确处理了文件不存在的情况")

    def test_api_server_status(self):
        """测试API服务器状态"""
        print(f"\n检查API服务器状态: {self.api_host}")
        
        is_available = self.check_api_server()
        
        if is_available:
            print("✅ API服务器可用")
        else:
            print("❌ API服务器不可用")
            
        # 这个测试不会失败，只是用来检查服务状态
        print(f"API服务器状态: {'可用' if is_available else '不可用'}")


if __name__ == '__main__':
    # 设置测试运行的详细程度
    unittest.main(verbosity=2)
