# Video Note Agent - 视频智能笔记生成器

一个目前专门针对历史学习视频的AI智能笔记生成工具，能够从历史视频中自动提取音频、生成字幕，并转换为高质量的Markdown学习笔记。修改prompt也可以适用于其它类型的视频。

## 🚀 功能特性

### 核心功能
- **🎬 历史视频处理**: 支持本地视频文件和在线视频URL
- **🎤 语音转文字**: 使用OpenAI Whisper进行高精度语音识别
- **📝 智能字幕生成**: 自动生成SRT、VTT、TXT格式字幕
- **📚 学习笔记生成**: 将字幕转换为结构化的Markdown学习笔记
- **🏷️ 自动标题提取**: 自动从视频中提取标题作为笔记标题
- **🗺️ 地图搜索建议**: 自动识别并提供相关历史地图搜索关键词


### 智能特性
- **知识扩展**: 使用引用格式添加相关知识背景
- **问答环节**: 模拟学习者提问并回答，深化理解
- **逻辑组织**: 注重信息间的逻辑联系，不局限于时间顺序
- **关键词标注**: 自动加粗重要概念和关键词
- **英文标注**: 为西方人名地名添加英文标注
- **内容完善**: 基于历史知识补充和扩展字幕内容

## 📋 系统要求

- Python 3.8+
- FFmpeg (用于音频处理)
- OpenAI API密钥（用于笔记生成）
- 至少2GB RAM

## 🛠️ 安装指南

### 1. 克隆项目
```bash
git clone https://github.com/your-username/video-note-agent.git
cd video-note-agent
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 安装FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
下载并安装 [FFmpeg](https://ffmpeg.org/download.html)

### 4. 配置设置
编辑 `config/settings.py` 文件，在文件顶部设置您的配置：

```python
# OpenAI API密钥 - 请替换为您的API密钥
OPENAI_API_KEY = "your-api-key-here"

# 默认视频链接或文件路径 - 可以在此处设置默认的视频地址
DEFAULT_VIDEO_PATH = ""  # 例如: "https://www.bilibili.com/video/BV1xxx"

# 默认视频标题（当无法从视频中提取标题时使用）
DEFAULT_VIDEO_TITLE = "历史学习笔记"
```

## 🎯 快速开始

### 方法1: 配置后命令行使用
```bash
# 处理本地视频文件（自动提取视频标题）
python main.py "path/to/your/video.mp4"

# 处理在线视频（自动提取视频标题）
python main.py "https://www.bilibili.com/video/BV1xxx"

# 指定输出目录和模型
python main.py "video.mp4" -o "output" -m "base"

# 自定义视频标题（可选）
python main.py "video.mp4" -t "自定义标题"

# 不保存字幕文件
python main.py "video.mp4" --no-subtitles
```

### 方法2: 配置后直接运行
在 `config/settings.py` 中设置默认视频地址后，直接运行：
```bash
python main.py
```

## 📖 详细使用指南

### 1. 音频处理

```python
from tools.audio_downloader import AudioDownloader
from tools.subtitle_generator import SubtitleGenerator

# 初始化音频下载器
downloader = AudioDownloader()

# 从本地视频提取音频
audio_path, title = downloader.extract_audio_from_video("video.mp4")

# 从URL下载音频
audio_path, title = downloader.download_audio_from_url("https://www.bilibili.com/video/BV1xxx")

# 初始化字幕生成器
generator = SubtitleGenerator(model_size="base")  # 可选: tiny, base, small, medium, large

# 转录音频
transcription = generator.transcribe_audio(audio_path, language="zh")

# 保存字幕文件
generator.save_subtitle_file(transcription, "subtitle.srt", "srt")
generator.save_subtitle_file(transcription, "subtitle.vtt", "vtt")
generator.save_subtitle_file(transcription, "subtitle.txt", "txt")
```

### 2. 学习笔记生成

```python
from tools.note_generator import NoteGenerator

# 初始化笔记生成器
generator = NoteGenerator(api_key="your-openai-api-key")

# 生成学习笔记
notes = generator.generate_learning_notes(
    transcription=transcription,
    video_title="罗马历史学习笔记",
    output_format="markdown"
)

# 保存笔记
markdown_path = generator.save_notes_to_file(
    notes, 
    "output", 
    video_title="罗马历史学习笔记"
)
```




## 📁 输出文件结构

```
output/
├── 视频标题_学习笔记.md          # 主要的学习笔记文件
├── 视频标题_学习笔记.json        # 包含元数据的JSON文件
├── transcription_data.json      # 原始转录数据
└── subtitles/                   # 字幕文件目录
    ├── subtitle.srt            # SRT格式字幕
    ├── subtitle.vtt            # VTT格式字幕
    └── subtitle.txt            # 纯文本字幕
```
