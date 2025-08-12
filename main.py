#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字幕转学习笔记工具 - 主程序
整合音频下载、字幕生成和笔记生成三个工具
"""

import sys
import os
import logging
import argparse
from pathlib import Path
from typing import Optional

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent))

# 导入工具模块
from tools.audio_downloader import AudioDownloader
from tools.subtitle_generator import SubtitleGenerator
from tools.note_generator import NoteGenerator

# 导入配置
from config.settings import OPENAI_API_KEY, WHISPER_CONFIG, OUTPUT_DIR, LOGGING_CONFIG, DEFAULT_VIDEO_PATH, DEFAULT_VIDEO_TITLE

def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=LOGGING_CONFIG.get("level", logging.INFO),
        format=LOGGING_CONFIG.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def process_video_to_notes(video_path: str, 
                          output_dir: str = None,
                          model_size: str = None,
                          api_key: Optional[str] = None,
                          video_title: str = None,
                          save_subtitles: bool = True) -> dict:
    """
    将视频转换为学习笔记的完整流程
    
    Args:
        video_path: 视频文件路径或URL
        output_dir: 输出目录
        model_size: Whisper模型大小
        api_key: OpenAI API密钥
        video_title: 视频标题（可选）
        save_subtitles: 是否保存字幕文件
        
    Returns:
        dict: 处理结果
    """
    logger = logging.getLogger(__name__)
    
    try:
        # 设置输出目录
        if output_dir is None:
            output_dir = OUTPUT_DIR
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 如果没有提供标题，从文件名提取
        if video_title is None:
            video_title = Path(video_path).stem
        
        # 设置默认参数
        if model_size is None:
            model_size = WHISPER_CONFIG["default_model"]
        if api_key is None:
            api_key = OPENAI_API_KEY
        
        logger.info(f"开始处理视频: {video_path}")
        logger.info(f"视频标题: {video_title}")
        logger.info(f"输出目录: {output_path}")
        
        # 步骤1: 音频下载/提取
        logger.info("=" * 50)
        logger.info("步骤1: 音频下载/提取")
        logger.info("=" * 50)
        
        audio_downloader = AudioDownloader()
        
        # 判断是URL还是本地文件
        if video_path.startswith(('http://', 'https://')):
            logger.info("检测到URL，开始下载音频...")
            audio_path, extracted_title = audio_downloader.download_audio_from_url(video_path, str(output_path / "temp"))
        else:
            logger.info("检测到本地文件，开始提取音频...")
            audio_path, extracted_title = audio_downloader.extract_audio_from_video(video_path, str(output_path / "temp"))
        
        # 如果没有提供标题，使用从视频中提取的标题
        if not video_title or video_title == DEFAULT_VIDEO_TITLE:
            video_title = extracted_title
            logger.info(f"使用从视频中提取的标题: {video_title}")
        
        # 获取音频信息
        audio_info = audio_downloader.get_audio_info(audio_path)
        logger.info(f"音频信息: {audio_info}")
        
        # 步骤2: 音频转字幕
        logger.info("=" * 50)
        logger.info("步骤2: 音频转字幕")
        logger.info("=" * 50)
        
        subtitle_generator = SubtitleGenerator(model_size=model_size)
        transcription = subtitle_generator.transcribe_audio(audio_path)
        
        # 获取转录统计信息
        transcription_stats = subtitle_generator.get_transcription_stats(transcription)
        logger.info(f"转录统计: {transcription_stats}")
        
        # 保存字幕文件
        if save_subtitles:
            logger.info("保存字幕文件...")
            subtitles_dir = output_path / "subtitles"
            subtitles_dir.mkdir(exist_ok=True)
            
            subtitle_generator.save_subtitle_file(transcription, str(subtitles_dir / "subtitle.srt"), "srt")
            subtitle_generator.save_subtitle_file(transcription, str(subtitles_dir / "subtitle.vtt"), "vtt")
            subtitle_generator.save_subtitle_file(transcription, str(subtitles_dir / "subtitle.txt"), "txt")
        
        # 步骤3: 生成学习笔记
        logger.info("=" * 50)
        logger.info("步骤3: 生成学习笔记")
        logger.info("=" * 50)
        
        note_generator = NoteGenerator(api_key=api_key)
        notes = note_generator.generate_learning_notes(
            transcription=transcription,
            video_title=video_title,
            output_format="markdown"
        )
        
        # 保存笔记
        logger.info("保存学习笔记...")
        markdown_path = note_generator.save_notes_to_file(
            notes, 
            str(output_path), 
            video_title=video_title
        )
        
        # 保存原始数据
        import json
        with open(output_path / "transcription_data.json", "w", encoding="utf-8") as f:
            json.dump(transcription, f, ensure_ascii=False, indent=2)
        
        logger.info("=" * 50)
        logger.info("处理完成！")
        logger.info("=" * 50)
        
        return {
            "success": True,
            "output_dir": str(output_path),
            "markdown_path": markdown_path,
            "subtitles_dir": str(subtitles_dir) if save_subtitles else None,
            "audio_path": audio_path,
            "notes": notes,
            "statistics": {
                "duration": transcription.get("duration", 0),
                "segments_count": len(transcription.get("segments", [])),
                "total_text_length": len(transcription.get("full_text", "")),
                "keywords_count": len(notes.get("json", {}).get("keywords", [])),
                "maps_count": len(notes.get("json", {}).get("maps", []))
            }
        }
        
    except Exception as e:
        logger.error(f"处理失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="字幕转学习笔记工具")
    parser.add_argument("video_path", nargs="?", default=DEFAULT_VIDEO_PATH, 
                       help="视频文件路径或URL（如果未提供，将使用配置文件中的默认值）")
    parser.add_argument("-o", "--output", help="输出目录")
    parser.add_argument("-m", "--model", default=None,
                       choices=["tiny", "base", "small", "medium", "large"],
                       help="Whisper模型大小")
    parser.add_argument("-k", "--api-key", help="OpenAI API密钥")
    parser.add_argument("-t", "--title", help="视频标题（可选，如果不提供将自动从视频中提取）")
    parser.add_argument("--no-subtitles", action="store_true", help="不保存字幕文件")
    
    args = parser.parse_args()
    
    # 检查是否提供了视频路径
    if not args.video_path:
        print("❌ 错误：请提供视频文件路径或URL")
        print("使用方法：")
        print("  python main.py <视频路径或URL>")
        print("  python main.py https://www.bilibili.com/video/BV1xxx")
        print("  python main.py path/to/video.mp4")
        print("\n或者您可以在 config/settings.py 中设置 DEFAULT_VIDEO_PATH")
        sys.exit(1)
    
    # 设置日志
    setup_logging()
    
    # 如果没有提供标题，使用默认标题
    if not args.title:
        args.title = DEFAULT_VIDEO_TITLE
    
    print("🎬 字幕转学习笔记工具")
    print("=" * 50)
    
    # 处理视频
    result = process_video_to_notes(
        video_path=args.video_path,
        output_dir=args.output,
        model_size=args.model,
        api_key=args.api_key,
        video_title=args.title,
        save_subtitles=not args.no_subtitles
    )
    
    if result["success"]:
        print("\n✅ 处理成功！")
        print(f"📁 输出目录: {result['output_dir']}")
        print(f"📝 学习笔记: {result['markdown_path']}")
        if result['subtitles_dir']:
            print(f"📄 字幕文件: {result['subtitles_dir']}")
        print(f"🎵 音频文件: {result['audio_path']}")
        
        # 显示统计信息
        stats = result["statistics"]
        print(f"\n📊 统计信息:")
        print(f"   ⏱️  视频时长: {stats['duration']:.1f}秒")
        print(f"   📝 字幕段落: {stats['segments_count']}个")
        print(f"   📄 文本长度: {stats['total_text_length']}字符")
        print(f"   🔑 关键词: {stats['keywords_count']}个")
        print(f"   🗺️  地图建议: {stats['maps_count']}个")
        
        # 显示关键词
        keywords = result["notes"]["json"].get("keywords", [])
        if keywords:
            print(f"\n🔑 主要关键词:")
            for keyword in keywords[:10]:  # 显示前10个
                print(f"   • {keyword}")
        
        # 显示地图建议
        maps = result["notes"]["json"].get("maps", [])
        if maps:
            print(f"\n🗺️  地图搜索建议:")
            for map_suggestion in maps[:5]:  # 显示前5个
                print(f"   • {map_suggestion}")
        
    else:
        print(f"\n❌ 处理失败: {result['error']}")
        sys.exit(1)

if __name__ == "__main__":
    main()
