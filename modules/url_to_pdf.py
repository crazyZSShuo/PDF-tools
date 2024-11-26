import os
import weasyprint
import httpx
import asyncio
from bs4 import BeautifulSoup
import time

class URLToPDFConverter:
    def __init__(self):
        self.supported_sizes = {
            "A4": {"width": "210mm", "height": "297mm"},
            "Letter": {"width": "215.9mm", "height": "279.4mm"},
            "Legal": {"width": "215.9mm", "height": "355.6mm"}
        }
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
    
    async def _fetch_url_content(self, url):
        """异步获取URL内容并进行预处理"""
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            
            # 使用BeautifulSoup处理HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 移除不需要的元素
            for script in soup(["script", "style"]):
                script.decompose()
                
            return str(soup)
        except Exception as e:
            raise Exception(f"获取URL内容失败: {str(e)}")
        finally:
            await self.client.aclose()
    
    async def convert_async(self, url, output_dir, page_size="A4", orientation="纵向"):
        """异步将URL转换为PDF"""
        try:
            # 获取并处理HTML内容
            html_content = await self._fetch_url_content(url)
            
            # 设置PDF样式
            page_size_dict = self.supported_sizes.get(page_size, self.supported_sizes["A4"])
            
            # 处理页面方向
            if orientation == "横向":
                width, height = page_size_dict["height"], page_size_dict["width"]
            else:
                width, height = page_size_dict["width"], page_size_dict["height"]
            
            # 创建CSS样式
            css_string = f"""
                @page {{
                    size: {width} {height};
                    margin: 1cm;
                }}
                body {{
                    font-family: Arial, sans-serif;
                }}
                img {{
                    max-width: 100%;
                    height: auto;
                }}
                @media print {{
                    a {{
                        text-decoration: none;
                        color: black;
                    }}
                }}
            """
            
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            # 生成输出文件路径
            output_path = os.path.join(output_dir, f"converted_{int(time.time())}.pdf")
            
            # 转换为PDF
            html = weasyprint.HTML(string=html_content)
            css = weasyprint.CSS(string=css_string)
            html.write_pdf(output_path, stylesheets=[css])
            
            return output_path
            
        except Exception as e:
            raise Exception(f"URL转换PDF失败: {str(e)}")
    
    def convert(self, url, output_dir, page_size="A4", orientation="纵向"):
        """同步方法包装异步转换功能"""
        return asyncio.run(self.convert_async(url, output_dir, page_size, orientation))
