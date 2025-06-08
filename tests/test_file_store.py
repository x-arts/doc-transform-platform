import unittest
from unittest.mock import patch, mock_open
from pathlib import Path
import json
from app.file_store import get_file_by_id, upload_file


class TestFileStore(unittest.TestCase):
    def setUp(self):
        # 测试数据
        self.test_file_id = "test123"
        self.test_filename = "test.pdf"
        self.test_file_content = b"test content"
        self.test_file_path = "/path/to/test.pdf"

    @patch('app.file_store.requests.get')
    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.mkdir')
    def test_get_file_by_id(self, mock_mkdir, mock_file_open, mock_get):
        # 模拟请求响应
        mock_response = unittest.mock.Mock()
        mock_response.headers = {
            'content-disposition': f'filename={self.test_filename}'
        }
        mock_response.content = self.test_file_content
        mock_get.return_value = mock_response

        # 调用函数
        result = get_file_by_id(self.test_file_id)

        # 验证是否调用了正确的URL
        mock_get.assert_called_once_with(
            f'http://localhost:8000/api/files/download/{self.test_file_id}'
        )

        # 验证是否创建了目录
        mock_mkdir.assert_called_once_with(exist_ok=True)

        # 验证是否正确写入文件
        mock_file_open.assert_called_once()
        mock_file_open().write.assert_called_once_with(self.test_file_content)

        # 验证返回路径中包含文件名
        self.assertTrue(self.test_filename in result)

    @patch('app.file_store.requests.post')
    @patch('pathlib.Path.exists')
    def test_upload_file_success(self, mock_exists, mock_post):
        # 模拟文件存在
        mock_exists.return_value = True

        # 模拟上传响应
        mock_response = unittest.mock.Mock()
        mock_response.json.return_value = {'fileId': self.test_file_id}
        mock_post.return_value = mock_response

        # 调用上传函数
        result = upload_file(self.test_file_path)

        # 验证结果
        self.assertEqual(result, self.test_file_id)
        mock_post.assert_called_once()

    @patch('pathlib.Path.exists')
    def test_upload_file_not_exists(self, mock_exists):
        # 模拟文件不存在
        mock_exists.return_value = False

        # 验证是否抛出异常
        with self.assertRaises(Exception) as context:
            upload_file(self.test_file_path)

        self.assertTrue('文件不存在' in str(context.exception))

    @patch('app.file_store.requests.post')
    @patch('pathlib.Path.exists')
    def test_upload_file_missing_file_id(self, mock_exists, mock_post):
        # 模拟文件存在
        mock_exists.return_value = True

        # 模拟响应中没有fileId
        mock_response = unittest.mock.Mock()
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        # 验证是否抛出异常
        with self.assertRaises(Exception) as context:
            upload_file(self.test_file_path)

        self.assertTrue('未包含fileId' in str(context.exception))


if __name__ == '__main__':
    unittest.main()
