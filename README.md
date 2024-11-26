# PDF工具集

一个基于Streamlit的PDF处理工具网站，提供多种PDF相关功能。

## 功能特性

### 第一阶段功能
- URL转PDF
  - 支持自定义页面大小和方向
  - 支持A4、Letter、Legal等格式
- PDF转Word
  - 保持原有格式
  - 支持表格和图片
- PDF处理工具
  - PDF加密/解密
  - PDF压缩
  - PDF拆分

## 安装说明

1. 克隆仓库：
```bash
git clone [repository-url]
cd pdf-tools
```

2. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

## 运行应用

```bash
streamlit run app.py
```

访问 http://localhost:8501 查看应用。

## 使用说明

### URL转PDF
1. 在侧边栏选择"URL转PDF"
2. 输入要转换的网页URL
3. 选择输出PDF的页面大小和方向
4. 点击"转换为PDF"按钮
5. 等待转换完成后下载生成的PDF文件

### PDF转Word
1. 在侧边栏选择"PDF转Word"
2. 上传需要转换的PDF文件
3. 点击"转换为Word"按钮
4. 等待转换完成后下载生成的Word文档

### PDF处理工具
1. 在侧边栏选择"PDF处理工具"
2. 上传需要处理的PDF文件
3. 选择要执行的操作（加密/解密/压缩/拆分）
4. 根据选择的操作提供必要的参数（如密码、页面范围等）
5. 点击相应的处理按钮
6. 等待处理完成后下载生成的PDF文件

## 注意事项

- 文件大小限制：100MB
- 支持的文件格式：PDF文件（用于转换和处理）
- 临时文件会在24小时后自动清理
- 每个用户会话都有独立的工作空间

## 技术栈

- Python 3.8+
- Streamlit
- WeasyPrint
- pdf2docx
- PyPDF2
- Beautiful Soup 4

## 贡献指南

欢迎提交问题和功能建议！

## 许可证

MIT License
