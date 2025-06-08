import json
from typing import TypedDict, Optional
import redis
from redis.exceptions import AuthenticationError, ConnectionError


class TaskMessage(TypedDict):
    taskId: str
    status: str
    fileId: str


class MessagePusher:
    # Redis 消息主题常量
    FILE_TRANSFORM_TOPIC = 'FILE_TRANSFORM_TOPIC'
    _instance = None

    def __init__(self, host='127.0.0.1', port=6379, db=0, password='123456'):
        """初始化 Redis 客户端"""
        try:
            self.redis_client = redis.Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=True,
                socket_connect_timeout=5
            )
            # 测试连接
            self.redis_client.ping()
            print(f"Redis 连接成功，host: {host}, port: {port}")
        except (AuthenticationError, ConnectionError) as e:
            print(f"Redis 连接失败: {str(e)}")
            raise

    @classmethod
    def get_instance(cls) -> 'MessagePusher':
        """使用单例模式获取 MessagePusher 实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def push_task_message(self, message: TaskMessage) -> bool:
        """
        推送任务状态消息到Redis
        :param message: 包含taskId、status和fileId的消息对象
        :return: 是否推送成功
        """
        try:
            # 将消息对象转换为JSON字符串
            message_str = json.dumps(message)

            # 发布消息到指定主题
            publish_result = self.redis_client.publish(self.FILE_TRANSFORM_TOPIC, message_str)

            if publish_result > 0:
                print(f"消息发送成功: {message_str}")
            else:
                print("消息已发送，但没有订阅者")

            return publish_result > 0

        except redis.RedisError as e:
            print(f"发送消息失败: {str(e)}")
            return False
        except Exception as e:
            print(f"发送消息时发生未知错误: {str(e)}")
            return False


def push_task_message(message: TaskMessage) -> bool:
    """
    使用默认配置推送任务状态消息
    :param message: 包含taskId、status和fileId的消息对象
    :return: 是否推送成功
    """
    try:
        pusher = MessagePusher.get_instance()
        return pusher.push_task_message(message)
    except Exception as e:
        print(f"消息推送服务初始化失败: {str(e)}")
        return False
