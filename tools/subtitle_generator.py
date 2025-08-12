"""
音频转字幕工具
负责将音频转换为字幕文件
"""

import whisper
import torch
import logging
from pathlib import Path
from typing import Dict, List
import json
import re

class SubtitleGenerator:
    """字幕生成器"""
    
    def __init__(self, model_size: str = "base"):
        """
        初始化字幕生成器
        
        Args:
            model_size: Whisper模型大小 (tiny, base, small, medium, large)
        """
        self.logger = logging.getLogger(__name__)
        self.model = self._load_model(model_size)
        self.model_size = model_size
    
    def _load_model(self, model_size: str):
        """加载Whisper模型"""
        try:
            # 检查是否有GPU
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.logger.info(f"使用设备: {device}")
            self.logger.info(f"加载Whisper模型: {model_size}")
            
            model = whisper.load_model(model_size, device=device)
            self.logger.info("Whisper模型加载成功")
            return model
        except Exception as e:
            self.logger.error(f"模型加载失败: {e}")
            raise
    
    def transcribe_audio(self, audio_path: str, language: str = "zh") -> Dict:
        """
        转录音频文件，生成带时间戳的字幕
        
        Args:
            audio_path: 音频文件路径
            language: 识别语言，默认中文
            
        Returns:
            Dict: 包含时间戳的转录结果
        """
        try:
            self.logger.info(f"开始转录音频: {audio_path}")
            
            # 转录选项 - 使用initial_prompt确保生成简体中文
            options = {
                "language": "zh",  # 使用中文
                "task": "transcribe",
                "word_timestamps": True,  # 获取词级时间戳
                "verbose": False,
                "initial_prompt": "以下是普通话的句子。"  # 确保生成简体中文
            }
            
            # 执行转录
            result = self.model.transcribe(audio_path, **options)
            
            # 处理结果
            processed_result = self._process_transcription_result(result)
            
            self.logger.info(f"音频转录完成，共 {len(processed_result['segments'])} 个段落")
            return processed_result
            
        except Exception as e:
            self.logger.error(f"音频转录失败: {e}")
            raise
    
    def _process_transcription_result(self, result: Dict) -> Dict:
        """处理转录结果"""
        try:
            # 提取完整文本
            full_text = result.get("text", "")
            
            # 处理段落
            segments = []
            for segment in result.get("segments", []):
                segment_text = segment.get("text", "")
                
                corrected_segment = {
                    "start": segment.get("start", 0),
                    "end": segment.get("end", 0),
                    "text": segment_text,
                    "confidence": segment.get("confidence", 0)
                }
                segments.append(corrected_segment)
            
            return {
                "full_text": full_text,
                "segments": segments,
                "language": result.get("language", "zh"),
                "duration": result.get("duration", 0)
            }
            
        except Exception as e:
            self.logger.error(f"转录结果处理失败: {e}")
            raise
    

    def save_subtitle_file(self, transcription: Dict, output_path: str, format_type: str = "srt") -> str:
        """
        保存字幕文件
        
        Args:
            transcription: 转录结果
            output_path: 输出文件路径
            format_type: 格式类型 (srt, vtt, txt)
            
        Returns:
            str: 保存的文件路径
        """
        try:
            segments = transcription.get("segments", [])
            
            if format_type == "srt":
                content = self._format_srt(segments)
            elif format_type == "vtt":
                content = self._format_vtt(segments)
            elif format_type == "txt":
                content = self._format_txt(segments)
            else:
                raise ValueError(f"不支持的格式类型: {format_type}")
            
            # 保存文件
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            self.logger.info(f"字幕文件已保存: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"字幕文件保存失败: {e}")
            raise
    
    def _format_srt(self, segments: List[Dict]) -> str:
        """格式化为SRT格式"""
        srt_content = []
        for i, segment in enumerate(segments, 1):
            start_time = self._format_time(segment["start"])
            end_time = self._format_time(segment["end"])
            text = segment["text"].strip()
            
            srt_content.append(f"{i}\n{start_time} --> {end_time}\n{text}\n")
        
        return "\n".join(srt_content)
    
    def _format_vtt(self, segments: List[Dict]) -> str:
        """格式化为VTT格式"""
        vtt_content = ["WEBVTT\n"]
        
        for segment in segments:
            start_time = self._format_time_vtt(segment["start"])
            end_time = self._format_time_vtt(segment["end"])
            text = segment["text"].strip()
            
            vtt_content.append(f"{start_time} --> {end_time}\n{text}\n")
        
        return "\n".join(vtt_content)
    
    def _format_txt(self, segments: List[Dict]) -> str:
        """格式化为纯文本格式"""
        txt_content = []
        for segment in segments:
            timestamp = self._format_time(segment["start"])
            text = segment["text"].strip()
            txt_content.append(f"[{timestamp}] {text}")
        
        return "\n".join(txt_content)
    
    def _format_time(self, seconds: float) -> str:
        """格式化时间为SRT格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
    
    def _format_time_vtt(self, seconds: float) -> str:
        """格式化时间为VTT格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millisecs:03d}"
    
    def get_transcription_stats(self, transcription: Dict) -> Dict:
        """获取转录统计信息"""
        segments = transcription.get("segments", [])
        full_text = transcription.get("full_text", "")
        
        return {
            "total_segments": len(segments),
            "total_text_length": len(full_text),
            "average_confidence": sum(s.get("confidence", 0) for s in segments) / len(segments) if segments else 0,
            "duration": transcription.get("duration", 0)
        }
