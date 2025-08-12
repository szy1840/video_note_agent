"""
音频下载工具
负责从视频文件或URL中提取音频
"""

import os
import logging
from pathlib import Path
from typing import Optional
import yt_dlp

class AudioDownloader:
    """音频下载器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def download_audio_from_url(self, url: str, output_dir: str = "temp") -> tuple:
        """
        从URL下载音频
        
        Args:
            url: 视频URL
            output_dir: 输出目录
            
        Returns:
            tuple: (音频文件路径, 视频标题)
        """
        try:
            # 创建输出目录
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # 配置yt-dlp选项
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': str(output_path / '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': False,
                'no_warnings': False
            }
            
            self.logger.info(f"开始下载音频: {url}")
            
            # 下载音频
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'video')
                
            # 查找下载的音频文件
            audio_files = list(output_path.glob(f"{title}*.mp3"))
            if audio_files:
                audio_path = str(audio_files[0])
                self.logger.info(f"音频下载完成: {audio_path}")
                return audio_path, title
            else:
                raise Exception("未找到下载的音频文件")
                
        except Exception as e:
            self.logger.error(f"音频下载失败: {e}")
            raise
    
    def extract_audio_from_video(self, video_path: str, output_dir: str = "temp") -> tuple:
        """
        从本地视频文件提取音频
        
        Args:
            video_path: 视频文件路径
            output_dir: 输出目录
            
        Returns:
            tuple: (音频文件路径, 视频标题)
        """
        try:
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"视频文件不存在: {video_path}")
            
            # 创建输出目录
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # 生成输出文件名
            video_name = Path(video_path).stem
            audio_path = str(output_path / f"{video_name}.mp3")
            
            self.logger.info(f"开始提取音频: {video_path}")
            
            # 使用yt-dlp提取音频
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': audio_path,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': False,
                'no_warnings': False
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_path])
            
            self.logger.info(f"音频提取完成: {audio_path}")
            return audio_path, video_name
            
        except Exception as e:
            self.logger.error(f"音频提取失败: {e}")
            raise
    
    def get_audio_info(self, audio_path: str) -> dict:
        """
        获取音频文件信息
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            dict: 音频信息
        """
        try:
            import librosa
            
            # 加载音频文件
            y, sr = librosa.load(audio_path)
            duration = librosa.get_duration(y=y, sr=sr)
            
            return {
                "path": audio_path,
                "duration": duration,
                "sample_rate": sr,
                "channels": 1 if len(y.shape) == 1 else 2
            }
            
        except Exception as e:
            self.logger.error(f"获取音频信息失败: {e}")
            return {"path": audio_path, "error": str(e)}
