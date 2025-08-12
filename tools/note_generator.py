"""
LLM生成笔记工具
负责将字幕转换为高质量的Markdown学习笔记
"""

import openai
import logging
from typing import Dict, List, Optional
import json
import re
from pathlib import Path
from config.settings import AI_CONFIG, GPT_CONFIG

class NoteGenerator:
    """笔记生成器"""
    
    def __init__(self, api_key: str = None):
        """
        初始化笔记生成器
        
        Args:
            api_key: OpenAI API密钥
        """
        self.api_key = api_key
        if api_key:
            openai.api_key = api_key
        self.logger = logging.getLogger(__name__)
    
    def generate_learning_notes(self, 
                               transcription: Dict, 
                               video_title: str = "",
                               output_format: str = "markdown") -> Dict:
        """
        基于字幕生成学习笔记
        
        Args:
            transcription: 音频转录结果
            video_title: 视频标题
            output_format: 输出格式 ("markdown" 或 "json")
            
        Returns:
            Dict: 学习笔记
        """
        try:
            # 1. 预处理字幕内容
            processed_content = self._preprocess_subtitle_content(transcription)
            
            # 2. 生成学习笔记
            notes = self._generate_notes_from_subtitle(processed_content, video_title)
            
            # 3. 根据格式输出
            if output_format == "markdown":
                markdown_content = self._convert_to_markdown(notes)
                return {
                    "markdown": markdown_content,
                    "json": notes,
                    "metadata": {
                        "title": video_title,
                        "duration": transcription.get("duration", 0),
                        "segments_count": len(transcription.get("segments", [])),
                        "total_text_length": len(processed_content["full_text"])
                    }
                }
            else:
                return notes
                
        except Exception as e:
            self.logger.error(f"学习笔记生成失败: {e}")
            raise
    
    def _preprocess_subtitle_content(self, transcription: Dict) -> Dict:
        """预处理字幕内容"""
        try:
            # 提取完整文本
            full_text = transcription.get("full_text", "")
            segments = transcription.get("segments", [])
            
            # 按时间轴组织内容
            timeline_content = []
            for segment in segments:
                timeline_content.append({
                    "timestamp": segment.get("start", 0),
                    "text": segment.get("text", ""),
                    "confidence": segment.get("confidence", 0)
                })
            
            return {
                "full_text": full_text,
                "timeline_content": timeline_content,
                "original_segments": segments
            }
            
        except Exception as e:
            self.logger.error(f"字幕内容预处理失败: {e}")
            raise
    
    def _generate_notes_from_subtitle(self, processed_content: Dict, title: str) -> Dict:
        """从字幕生成学习笔记"""
        try:
            # 构建增强的prompt
            prompt = self._build_enhanced_prompt(processed_content, title)
            
            # 调用GPT生成笔记
            response = self._call_gpt_for_notes(prompt, title)
            
            # 解析响应
            notes = self._parse_notes_response(response)
            
            return notes
            
        except Exception as e:
            self.logger.error(f"笔记生成失败: {e}")
            raise
    
    def _build_enhanced_prompt(self, processed_content: Dict, title: str) -> str:
        """构建增强的prompt"""
        
        # print("="*100)
        # print(processed_content['full_text'])
        
        prompt = f"""
你是一位专业的历史学者和教育专家。请基于以下历史视频的转文字字幕内容，帮助学生生成一份高质量的Markdown格式学习笔记。

视频标题：{title}

字幕内容：
{processed_content['full_text']}

请严格按照以下要求生成学习笔记：

## 标题要求
请使用视频标题作为笔记的主标题，格式为：`# {title}`

## 格式要求
1. 使用Markdown格式
2. 注重信息之间的逻辑联系，不要拘泥于时间顺序
3. 在首次出现时为西方人名地名使用括号标注英文，例如：马略(Marius)、高卢人(Gauls)
4. 对重要概念和关键词进行**加粗**处理，例如：**马略改革**、**元老院**
5. 对于历史名词请根据上下文和历史知识使用最准确的中文表达

## 内容要求
1. **地图优先**：在讲述具体历史事件之前，先提供相关地图搜索建议，帮助读者建立地理概念
   - 格式：[地图标题] - 搜索关键词
   - 例如：[布匿战争地图] - "第一次布匿战争地图 西西里岛 迦太基"

2. **知识扩展**：使用引用格式(>)适当加入相关知识/观点来帮助理解和深化内容
   - 补充重要的历史背景和前后逻辑关系
   - 解释关键概念和历史意义
   - 引用内容要简洁且有价值

3. **问答环节**：用斜体格式模拟学习者的思考、提问并模拟历史教授的回答
   - 格式：*Q：问题内容*  
   - 格式：*A：回答内容*
   - 问题和回答都要有深度、有启发性、有针对性，避免模板化
   - 回答要简洁有力
   - 例如，当发现A文明和B文明在相似的情况时平民有不同的反应，就可以横向对比，提出问题（为什么？）

4. **内容完善**：由于字幕信息有限，请在合适程度进行知识完善和扩展
   - 补充重要的历史知识和前后逻辑关系
   - 解释关键概念
   - 但不改变原意

5. **学习重点**：
   - 不要花大量笔墨描写战争细节，重点概括有价值的战争胜败原因
   - 关注制度变迁、社会结构变化等深层内容，特别注重逻辑性
   - 注重历史事件之间的因果关系和影响

## 注意事项
- 避免使用模板化的问答，问题要有针对性，回答要简洁有力
- 地图建议放在相关内容的最前面，帮助读者建立地理概念
- 注重补充字幕中缺失的重要历史背景和逻辑关系
- 保持内容的连贯性和逻辑性

请生成一份结构清晰、内容丰富、适合学习的Markdown笔记。
"""
        
        return prompt
    
    def _call_gpt_for_notes(self, prompt: str, video_title: str = "历史学习笔记") -> str:
        """调用GPT生成笔记"""
        try:
            # 使用新版本的OpenAI API
            client = openai.OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model=AI_CONFIG["default_model"],
                messages=[
                    {"role": "system", "content": "你是一位专业的历史学者和教育专家，擅长将历史视频的字幕内容转化为高质量的学习笔记。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=GPT_CONFIG["temperature"]
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"GPT调用失败: {e}")
            return response.choices[0].message.content
    
    def _parse_notes_response(self, response: str) -> Dict:
        """解析GPT响应"""
        try:
            return {
                "content": response,
                "sections": self._extract_sections(response),
                "keywords": self._extract_keywords(response),
                "maps": self._extract_map_suggestions(response)
            }
        except Exception as e:
            self.logger.error(f"响应解析失败: {e}")
            return {"content": response, "sections": [], "keywords": [], "maps": []}
    
    def _extract_sections(self, content: str) -> List[str]:
        """提取章节标题"""
        sections = []
        lines = content.split('\n')
        for line in lines:
            if line.strip().startswith('#'):
                sections.append(line.strip())
        return sections
    
    def _extract_keywords(self, content: str) -> List[str]:
        """提取关键词（加粗内容）"""
        keywords = re.findall(r'\*\*(.*?)\*\*', content)
        return list(set(keywords))
    
    def _extract_map_suggestions(self, content: str) -> List[str]:
        """提取地图搜索建议"""
        maps = re.findall(r'\[(.*?)\] - "(.*?)"', content)
        return [f"{title}: {keyword}" for title, keyword in maps]
    
    def _convert_to_markdown(self, notes: Dict) -> str:
        """转换为Markdown格式"""
        return notes.get("content", "")
    

    def save_notes_to_file(self, notes: Dict, output_path: str, video_title: str = "", filename: str = None):
        """保存笔记到文件"""
        try:
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 使用视频标题作为文件名，如果没有提供则使用默认名称
            if filename is None:
                if video_title:
                    # 清理文件名中的特殊字符
                    safe_title = re.sub(r'[<>:"/\\|?*]', '_', video_title)
                    filename = f"{safe_title}.md"
                else:
                    filename = "learning_notes.md"
            
            # 保存Markdown文件
            markdown_path = output_dir / filename
            with open(markdown_path, "w", encoding="utf-8") as f:
                # 优先使用markdown字段，如果没有则使用json.content，最后使用content
                markdown_content = notes.get("markdown") or notes.get("json", {}).get("content") or notes.get("content", "")
                f.write(markdown_content)
            
            # 保存JSON文件（包含元数据）
            json_path = output_dir / f"{Path(filename).stem}.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(notes, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"笔记已保存到: {markdown_path}")
            return str(markdown_path)
            
        except Exception as e:
            self.logger.error(f"笔记保存失败: {e}")
            raise
