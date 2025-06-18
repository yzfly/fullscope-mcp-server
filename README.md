# FullScope-MCP

> 内容总结运营 MCP Server，支持网页抓取、文件读取、内容总结、主题汇总等功能

<a href="https://glama.ai/mcp/servers/@yzfly/fullscope-mcp-server">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@yzfly/fullscope-mcp-server/badge" alt="FullScope-MCP MCP server" />
</a>

## 🌟 功能特性

FullScope-MCP 是一个功能全面的 Model Context Protocol (MCP) 服务器，专门用于内容总结和运营场景。支持以下核心功能：

1. **🤖 模型调用**: 直接调用大语言模型进行回答
2. **🌐 网页抓取**: 抓取网页内容，可选保存为 txt 文本文件  
3. **📝 内容总结**: 将任意内容总结为指定长度（默认原来的 20%，脱水版）
4. **🔗 网页总结**: 获取网页内容并自动总结为精炼版本
5. **📄 文本文件总结**: 读取 txt 等格式的文本文件并总结内容（限制返回 2k 字符）
6. **📚 PDF 文件总结**: 读取 PDF 文件并总结文本内容（限制返回 2k 字符）
7. **🎯 主题汇总**: 类似 RAG 功能，给定资料内容和查询主题，返回最相关的内容总结（2k 字符内）

## 📦 安装

### 使用 uvx 安装（推荐）

```bash
uvx fullscope-mcp-server
```

### 使用 pip 安装

```bash
pip install fullscope-mcp-server
```

### 从源码安装

```bash
git clone https://github.com/yzfly/fullscope-mcp
cd fullscope-mcp
pip install -e .
```

## ⚙️ 配置

### 环境变量配置

在使用之前，需要配置以下环境变量：

#### 必需配置

```bash
# MiniMax API Key（必需）
export OPENAI_API_KEY="your-minimax-api-key"
```

#### 可选配置

```bash
# API 基础 URL（默认使用 MiniMax）
export OPENAI_BASE_URL="https://api.minimaxi.com/v1"

# 使用的模型（默认 MiniMax-M1）
export OPENAI_MODEL="MiniMax-M1"

# 输入上下文最大 token 数（默认 120000）
export MAX_INPUT_TOKENS="120000"

# 输出上下文最大 token 数（默认 8000）  
export MAX_OUTPUT_TOKENS="8000"
```

### Claude Desktop 配置

在 Claude Desktop 中使用时，请添加以下配置到 `claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "fullscope-mcp": {
      "command": "uvx",
      "args": ["fullscope-mcp-server"],
      "env": {
        "OPENAI_API_KEY": "your-minimax-api-key-here",
        "OPENAI_BASE_URL": "https://api.minimaxi.com/v1",
        "OPENAI_MODEL": "MiniMax-M1",
        "MAX_INPUT_TOKENS": "900000",
        "MAX_OUTPUT_TOKENS": "8000"
      }
    }
  }
}
```

或者使用 pip 安装版本：

```json
{
  "mcpServers": {
    "fullscope-mcp": {
      "command": "python",
      "args": ["-m", "fullscope_mcp_server"],
      "env": {
        "OPENAI_API_KEY": "your-minimax-api-key-here",
        "OPENAI_BASE_URL": "https://api.minimaxi.com/v1",
        "OPENAI_MODEL": "MiniMax-M1",
        "MAX_INPUT_TOKENS": "900000",
        "MAX_OUTPUT_TOKENS": "8000"
      }
    }
  }
}
```

## 🚀 使用方法

### 1. 模型调用

```python
# 工具名: call_model
# 参数: prompt (str) - 要发送给模型的提示词
# 返回: 模型的回答
```

### 2. 网页抓取

```python
# 工具名: scrape_webpage  
# 参数: 
#   - url (str) - 要抓取的网页URL
#   - save_to_file (bool) - 是否保存内容到txt文件
# 返回: 抓取结果和文件路径（如果保存）
```

### 3. 内容总结

```python
# 工具名: summarize_content
# 参数:
#   - content (str) - 要总结的内容  
#   - target_ratio (float) - 目标压缩比例，0.1-1.0之间，默认0.2
# 返回: 总结后的内容
```

### 4. 网页总结

```python
# 工具名: summarize_webpage
# 参数:
#   - url (str) - 要抓取和总结的网页URL
#   - target_ratio (float) - 目标压缩比例，默认0.2
# 返回: 网页内容总结
```

### 5. 文本文件总结

```python
# 工具名: read_and_summarize_text_file
# 参数:
#   - filepath (str) - 文本文件路径
#   - target_ratio (float) - 目标压缩比例，默认0.2
# 返回: 文件内容总结
```

### 6. PDF文件总结

```python
# 工具名: read_and_summarize_pdf_file  
# 参数:
#   - filepath (str) - PDF文件路径
#   - target_ratio (float) - 目标压缩比例，默认0.2
# 返回: PDF内容总结
```

### 7. 主题汇总

```python
# 工具名: topic_based_summary
# 参数:
#   - content (str) - 资料内容
#   - query (str) - 查询的主题或问题
# 返回: 基于主题的相关内容总结（2k字符内）
```

## 📖 使用示例

### 在 Claude Desktop 中使用

1. **网页内容总结**
   ```
   请帮我总结这个网页的内容：https://example.com/article
   ```

2. **文档总结**
   ```
   请读取并总结这个PDF文件：/path/to/document.pdf
   ```

3. **主题分析**
   ```
   基于这段资料内容，帮我分析"人工智能发展趋势"相关的信息
   ```

### 直接运行服务器

```bash
# 设置环境变量
export OPENAI_API_KEY="your-api-key"

# 运行服务器
python fullscope_mcp_server.py
```

## 🔧 开发指南

### 项目结构

```
fullscope-mcp/
├── src/
│   └── fullscope_mcp_server/
│       ├── __init__.py
│       └── server.py
├── README.md
├── pyproject.toml
└── LICENSE
```

### 本地开发

```bash
# 克隆项目
git clone https://github.com/yzfly/fullscope-mcp
cd fullscope-mcp

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest
```

### 代码格式化

```bash
# 格式化代码
black src/
isort src/

# 类型检查
mypy src/
```

## 🌐 支持的模型

本服务器主要针对 MiniMax API 设计，但通过配置 `OPENAI_BASE_URL` 和相关参数，也可以支持其他兼容 OpenAI API 格式的模型服务：

- **MiniMax-M1** (默认推荐)
- **MiniMax-Text-01**  
- 其他支持 OpenAI API 格式的服务

### MiniMax API 配置说明

MiniMax API 支持最大 1,000,192 tokens 的上下文长度，非常适合处理长文档和大量内容的总结任务。

- 获取 API Key: [MiniMax 开放平台](https://api.minimaxi.com/)
- API 文档: [MiniMax API 文档](https://api.minimaxi.com/document)

## 🚀 发布到 PyPI 的步骤

### 1. 准备发布

```bash
# 安装构建工具
pip install build twine

# 构建包
python -m build

# 检查包
twine check dist/*
```

### 2. 发布到 TestPyPI (测试)

```bash
# 上传到 TestPyPI
twine upload --repository testpypi dist/*

# 从 TestPyPI 安装测试
pip install --index-url https://test.pypi.org/simple/ fullscope-mcp-server
```

### 3. 发布到正式 PyPI

```bash
# 上传到 PyPI
twine upload dist/*
```

## 📝 更新日志

### v1.0.0 (2024-12-19)

- ✨ 首次发布
- 🌐 支持网页抓取和保存
- 📝 支持内容总结（可配置压缩比例）
- 📄 支持文本文件和PDF文件读取总结
- 🎯 支持主题汇总（RAG功能）
- 🤖 支持直接模型调用
- ⚙️ 完善的环境变量配置
- 📦 支持 uvx 和 pip 安装

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 👨‍💻 作者

**yzfly**

- GitHub: [@yzfly](https://github.com/yzfly)
- Email: yz.liu.me@gmail.com
- 微信公众号: 云中江树
- NPM: [@langgpt](https://www.npmjs.com/~langgpt)

## 🙏 致谢

- [Model Context Protocol](https://modelcontextprotocol.io/) - 协议标准
- [MiniMax API](https://api.minimaxi.com/) - AI 模型服务
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) - HTML 解析
- [PyPDF2](https://pypdf2.readthedocs.io/) - PDF 处理

## ❓ 常见问题

### Q: 如何获取 MiniMax API Key？

A: 访问 [MiniMax 开放平台](https://api.minimaxi.com/)，注册账号后在账户管理-接口密钥中获取。

### Q: 可以使用其他模型吗？

A: 可以！通过配置 `OPENAI_BASE_URL` 和 `OPENAI_MODEL` 环境变量，可以使用任何兼容 OpenAI API 格式的模型服务。

### Q: 文件大小有限制吗？

A: 是的，为了性能考虑：
- 文本文件和PDF文件内容限制在约 120k 字符以内
- 网页内容会根据模型的上下文限制自动截断
- 主题汇总结果限制在 2k 字符以内

### Q: 如何在 Claude Desktop 中使用？

A: 按照上面的配置说明，将配置添加到 `claude_desktop_config.json` 文件中，重启 Claude Desktop 即可。

---

如果你觉得这个项目有用，请给个 ⭐ 星！