#!/usr/bin/env python3
"""
FullScope-MCP: 内容总结运营 MCP Server
支持网页抓取、文件读取、内容总结、主题汇总等功能
作者: yzfly (yz.liu.me@gmail.com)
微信公众号: 云中江树
GitHub: https://github.com/yzfly
"""

import os
import asyncio
import logging
from typing import Any, Optional
from pathlib import Path
import tempfile
import hashlib
from urllib.parse import urlparse

# 第三方库导入
import httpx
import PyPDF2
from bs4 import BeautifulSoup
import requests
from openai import OpenAI

# MCP相关导入
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp import Context
from mcp.types import TextContent, EmbeddedResource

# 环境变量配置
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.minimaxi.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "MiniMax-M1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MAX_INPUT_TOKENS = int(os.getenv("MAX_INPUT_TOKENS", "120000")) 
MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "8000"))

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建MCP服务器实例
mcp = FastMCP("FullScope-MCP")

class ContentSummarizer:
    """内容总结器，使用MiniMax API"""
    
    def __init__(self):
        if not OPENAI_API_KEY:
            raise ValueError("需要设置OPENAI_API_KEY环境变量")
        
        self.client = OpenAI(
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL
        )
    
    async def summarize_content(self, content: str, target_ratio: float = 0.2, 
                              custom_prompt: str = None) -> str:
        """
        使用大模型总结内容
        
        Args:
            content: 要总结的内容
            target_ratio: 目标压缩比例 (默认20%)
            custom_prompt: 自定义总结提示词
        
        Returns:
            总结后的内容
        """
        try:
            # 检查内容长度，避免超出限制
            if len(content) > MAX_INPUT_TOKENS * 3:  # 粗略估算token
                content = content[:MAX_INPUT_TOKENS * 3]
                logger.warning("内容过长，已截断")
            
            # 构建总结提示词
            if custom_prompt:
                prompt = custom_prompt
            else:
                target_length = min(max(int(len(content) * target_ratio), 100), 1000)

                prompt = f"""请将以下内容总结为约{target_length}字的精炼版本，保留核心信息和关键要点：

{content}

总结要求：
1. 保持原文的主要观点和逻辑结构
2. 去除冗余和次要信息
3. 使用简洁明了的语言
4. 确保信息的准确性和完整性"""

            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "你是一个专业的内容总结专家，擅长将长文本压缩为精炼的摘要。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=MAX_OUTPUT_TOKENS,
                temperature=0.1
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"内容总结失败: {e}")
            return f"总结失败: {str(e)}"

class WebScraper:
    """网页抓取器"""
    
    def __init__(self):
        self.session = httpx.AsyncClient(
            timeout=30.0,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
    
    async def scrape_url(self, url: str) -> tuple[str, str]:
        """
        抓取网页内容
        
        Args:
            url: 目标URL
            
        Returns:
            (title, content): 网页标题和清理后的文本内容
        """
        try:
            response = await self.session.get(url)
            response.raise_for_status()
            
            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 获取标题
            title = soup.find('title')
            title = title.get_text().strip() if title else "无标题"
            
            # 移除script和style标签
            for script in soup(["script", "style"]):
                script.decompose()
            
            # 提取主要内容
            content = soup.get_text()
            
            # 清理文本
            lines = (line.strip() for line in content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            content = ' '.join(chunk for chunk in chunks if chunk)
            
            return title, content
            
        except Exception as e:
            logger.error(f"网页抓取失败 {url}: {e}")
            raise Exception(f"无法抓取网页: {str(e)}")
    
    async def save_content_to_file(self, content: str, filename: str = None) -> str:
        """
        保存内容到文件
        
        Args:
            content: 要保存的内容
            filename: 文件名（可选）
            
        Returns:
            保存的文件路径
        """
        if not filename:
            # 生成基于内容哈希的文件名
            content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
            filename = f"scraped_content_{content_hash}.txt"
        
        # 确保文件扩展名为.txt
        if not filename.endswith('.txt'):
            filename += '.txt'
        
        filepath = Path(tempfile.gettempdir()) / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return str(filepath)
        except Exception as e:
            logger.error(f"保存文件失败: {e}")
            raise Exception(f"无法保存文件: {str(e)}")

class FileProcessor:
    """文件处理器"""
    
    @staticmethod
    def read_text_file(filepath: str) -> str:
        """读取文本文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return content
        except Exception as e:
            logger.error(f"读取文本文件失败 {filepath}: {e}")
            raise Exception(f"无法读取文件: {str(e)}")
    
    @staticmethod
    def read_pdf_file(filepath: str) -> str:
        """读取PDF文件"""
        try:
            content = ""
            with open(filepath, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                
                for page in pdf_reader.pages:
                    content += page.extract_text() + "\n"
            
            return content.strip()
        except Exception as e:
            logger.error(f"读取PDF文件失败 {filepath}: {e}")
            raise Exception(f"无法读取PDF文件: {str(e)}")

class RAGProcessor:
    """RAG处理器 - 简化版主题汇总"""
    
    def __init__(self, summarizer: ContentSummarizer):
        self.summarizer = summarizer
    
    async def topic_summary(self, content: str, query: str) -> str:
        """
        基于主题查询的内容总结
        
        Args:
            content: 资料内容
            query: 查询主题/问题
            
        Returns:
            相关内容的总结（2k字符内）
        """
        try:
            # 构建RAG样式的提示词
            prompt = f"""基于以下资料内容，针对查询主题进行总结分析：

查询主题: {query}

资料内容:
{content}

请根据查询主题，从资料中提取最相关的信息，并总结为2000字以内的内容。要求：
1. 重点关注与查询主题相关的内容
2. 保持信息的准确性和逻辑性
3. 如果资料中没有相关信息，请明确说明
4. 提供具体的细节和要点"""

            response = self.summarizer.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "你是一个专业的信息分析师，擅长从大量资料中提取特定主题的相关信息。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=min(MAX_OUTPUT_TOKENS, 120000),  # 限制在120k左右
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            
            return result
            
        except Exception as e:
            logger.error(f"主题汇总失败: {e}")
            return f"主题汇总失败: {str(e)}"

# 初始化组件
summarizer = ContentSummarizer()
scraper = WebScraper()
file_processor = FileProcessor()
rag_processor = RAGProcessor(summarizer)

# MCP工具定义

@mcp.tool()
async def call_model(prompt: str, ctx: Context) -> str:
    """
    调用模型进行回答
    
    Args:
        prompt: 要发送给模型的提示词
    
    Returns:
        模型的回答
    """
    try:
        response = summarizer.client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=MAX_OUTPUT_TOKENS,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        logger.error(f"模型调用失败: {e}")
        return f"模型调用失败: {str(e)}"

@mcp.tool()
async def scrape_webpage(url: str, ctx: Context, save_to_file: bool = False) -> str:
    """
    抓取网页内容，可选保存为txt文件
    
    Args:
        url: 要抓取的网页URL
        save_to_file: 是否保存内容到txt文件
    
    Returns:
        抓取结果和文件路径（如果保存）
    """
    try:
        ctx.info(f"开始抓取网页: {url}")
        
        title, content = await scraper.scrape_url(url)
        
        result = f"网页标题: {title}\n\n网页内容:\n{content}"
        
        if save_to_file:
            # 生成文件名
            parsed_url = urlparse(url)
            filename = f"{parsed_url.netloc}_{title[:20]}.txt".replace(" ", "_")
            # 移除非法字符
            filename = "".join(c for c in filename if c.isalnum() or c in "._-")
            
            filepath = await scraper.save_content_to_file(result, filename)
            result += f"\n\n已保存到文件: {filepath}"
        
        ctx.info("网页抓取完成")
        return result
        
    except Exception as e:
        logger.error(f"网页抓取失败: {e}")
        return f"网页抓取失败: {str(e)}"

@mcp.tool()
async def summarize_content(content: str, ctx: Context, target_ratio: float = 0.2) -> str:
    """
    将任意内容总结为指定比例的长度（默认20%）
    
    Args:
        content: 要总结的内容
        target_ratio: 目标压缩比例，0.1-1.0之间
    
    Returns:
        总结后的内容
    """
    try:
        # 验证参数
        if not 0.1 <= target_ratio <= 1.0:
            return "错误: target_ratio 必须在 0.1 到 1.0 之间"
        
        ctx.info(f"开始总结内容，目标比例: {target_ratio*100}%")
        
        summary = await summarizer.summarize_content(content, target_ratio)
        
        ctx.info("内容总结完成")
        return summary
        
    except Exception as e:
        logger.error(f"内容总结失败: {e}")
        return f"内容总结失败: {str(e)}"

@mcp.tool()
async def summarize_webpage(url: str, ctx: Context, target_ratio: float = 0.2) -> str:
    """
    抓取网页内容并总结为指定比例的长度（默认20%）
    
    Args:
        url: 要抓取和总结的网页URL
        target_ratio: 目标压缩比例，0.1-1.0之间
    
    Returns:
        网页内容总结
    """
    try:
        # 验证参数
        if not 0.1 <= target_ratio <= 1.0:
            return "错误: target_ratio 必须在 0.1 到 1.0 之间"
        
        ctx.info(f"开始抓取并总结网页: {url}")
        
        # 先抓取网页
        title, content = await scraper.scrape_url(url)
        
        # 然后总结
        full_content = f"网页标题: {title}\n\n{content}"
        summary = await summarizer.summarize_content(full_content, target_ratio)
        
        ctx.info("网页抓取和总结完成")
        return f"网页: {url}\n标题: {title}\n\n总结:\n{summary}"
        
    except Exception as e:
        logger.error(f"网页总结失败: {e}")
        return f"网页总结失败: {str(e)}"

@mcp.tool()
async def read_and_summarize_text_file(filepath: str, ctx: Context, target_ratio: float = 0.2) -> str:
    """
    读取txt等格式的文本文件并总结内容（限制2k字符）
    
    Args:
        filepath: 文本文件路径
        target_ratio: 目标压缩比例，0.1-1.0之间
    
    Returns:
        文件内容总结
    """
    try:
        # 验证参数
        if not 0.1 <= target_ratio <= 1.0:
            return "错误: target_ratio 必须在 0.1 到 1.0 之间"
        
        ctx.info(f"开始读取文本文件: {filepath}")
        
        # 读取文件
        content = file_processor.read_text_file(filepath)
        
        # 总结内容
        summary = await summarizer.summarize_content(content, target_ratio)
        
        ctx.info("文本文件读取和总结完成")
        return f"文件: {filepath}\n\n总结:\n{summary}"
        
    except Exception as e:
        logger.error(f"文本文件总结失败: {e}")
        return f"文本文件总结失败: {str(e)}"

@mcp.tool()
async def read_and_summarize_pdf_file(filepath: str, ctx: Context, target_ratio: float = 0.2) -> str:
    """
    读取PDF文件并总结内容（限制2k字符）
    
    Args:
        filepath: PDF文件路径
        target_ratio: 目标压缩比例，0.1-1.0之间
    
    Returns:
        PDF内容总结
    """
    try:
        # 验证参数
        if not 0.1 <= target_ratio <= 1.0:
            return "错误: target_ratio 必须在 0.1 到 1.0 之间"
        
        ctx.info(f"开始读取PDF文件: {filepath}")
        
        # 读取PDF
        content = file_processor.read_pdf_file(filepath)
        
        # 总结内容
        summary = await summarizer.summarize_content(content, target_ratio)
        
        ctx.info("PDF文件读取和总结完成")
        return f"PDF文件: {filepath}\n\n总结:\n{summary}"
        
    except Exception as e:
        logger.error(f"PDF文件总结失败: {e}")
        return f"PDF文件总结失败: {str(e)}"

@mcp.tool()
async def topic_based_summary(content: str, query: str, ctx: Context) -> str:
    """
    主题汇总功能 - 基于给定资料和查询主题，返回最相关的内容总结（2k字符内）
    
    Args:
        content: 资料内容
        query: 查询的主题或问题
    
    Returns:
        基于主题的相关内容总结
    """
    try:
        ctx.info(f"开始主题汇总，查询: {query}")
        
        summary = await rag_processor.topic_summary(content, query)
        
        ctx.info("主题汇总完成")
        return summary
        
    except Exception as e:
        logger.error(f"主题汇总失败: {e}")
        return f"主题汇总失败: {str(e)}"

# 资源定义
@mcp.resource("config://fullscope")
def get_server_config() -> str:
    """获取服务器配置信息"""
    return f"""FullScope-MCP 服务器配置

作者: yzfly
GitHub: https://github.com/yzfly
邮箱: yz.liu.me@gmail.com
微信公众号: 云中江树

当前配置:
- 模型: {OPENAI_MODEL}
- API基础URL: {OPENAI_BASE_URL}
- 最大输入令牌: {MAX_INPUT_TOKENS}
- 最大输出令牌: {MAX_OUTPUT_TOKENS}

支持的功能:
1. 调用模型进行回答
2. 抓取网页内容（可选保存为txt）
3. 总结任意内容（默认20%压缩）
4. 抓取并总结网页内容
5. 读取并总结文本文件（限制2k）
6. 读取并总结PDF文件（限制2k）
7. 主题汇总（类似RAG功能）
"""

def main():
    """主入口函数"""
    # 检查必要的环境变量
    if not OPENAI_API_KEY:
        print("错误: 请设置 OPENAI_API_KEY 环境变量")
        print("示例: export OPENAI_API_KEY='your-api-key-here'")
        exit(1)
    
    # 运行服务器
    mcp.run()

if __name__ == "__main__":
    main()