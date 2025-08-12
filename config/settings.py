"""
字幕转学习笔记工具配置文件
用户配置区域 - 请在此处修改您的设置

使用说明：
1. 将您的OpenAI API密钥填入 OPENAI_API_KEY 变量
2. 可选：在 DEFAULT_VIDEO_PATH 中设置默认的视频链接或文件路径
3. 可选：修改 DEFAULT_VIDEO_TITLE 设置默认的视频标题

然后运行：
  python main.py <视频路径或URL>
  或
  python main.py  # 如果设置了默认视频路径
"""

# ============================================================================
# 用户配置区域 - 请在此处修改您的设置
# ============================================================================

# OpenAI API密钥 - 请替换为您的API密钥
OPENAI_API_KEY = ""

# 默认视频链接或文件路径 - 可以在此处设置默认的视频地址，也可以通过命令行指定
DEFAULT_VIDEO_PATH = ""  # 例如: "https://www.bilibili.com/video/BV1xxx" 或 "path/to/video.mp4"

# 默认视频标题
DEFAULT_VIDEO_TITLE = "历史学习笔记"

# ============================================================================
# 高级配置 - 一般不需要修改
# ============================================================================

import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 输出目录
OUTPUT_DIR = PROJECT_ROOT / "output"

# 创建必要的目录
OUTPUT_DIR.mkdir(exist_ok=True)

# GPT模型配置
GPT_CONFIG = {
    "model": "gpt-5",
    "temperature": 1
}

# Whisper模型配置
WHISPER_CONFIG = {
    "default_model": "base",  # tiny, base, small, medium, large
    "default_language": "zh"
}

# 音频处理配置
AUDIO_CONFIG = {
    "default_model": WHISPER_CONFIG["default_model"],
    "default_language": WHISPER_CONFIG["default_language"],
    "supported_formats": [".mp3", ".wav", ".m4a", ".flac"]
}

# 视频处理配置
VIDEO_CONFIG = {
    "max_duration": 7200,  # 最大处理时长（秒）
    "supported_formats": [".mp4", ".avi", ".mov", ".mkv"],
    "download_timeout": 300  # 下载超时时间（秒）
}

# AI配置
AI_CONFIG = {
    "openai_api_key": OPENAI_API_KEY,
    "default_model": GPT_CONFIG["model"],
    "temperature": GPT_CONFIG["temperature"]
}

# 日志配置
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
}
