import os
import time
import fitz  # PyMuPDF
from PIL import Image
import io
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import uuid

class PDFProcessor:
    def __init__(self):
        # 新版本PyMuPDF不再使用LINK_JPEG等常量
        self.supported_image_types = {
            'jpeg': ['jpeg', 'jpg'],
            'png': ['png'],
            'all': ['jpeg', 'jpg', 'png']
        }
    
    def get_page_count(self, pdf_path):
        """获取PDF页数"""
        with open(pdf_path, 'rb') as file:
            reader = PdfReader(file)
            return len(reader.pages)
    
    def encrypt_pdf(self, pdf_path, password):
        """加密PDF文件"""
        try:
            output_dir = os.path.dirname(pdf_path)
            output_path = os.path.join(output_dir, f"encrypted_{int(time.time())}.pdf")
            
            reader = PdfReader(pdf_path)
            writer = PdfWriter()
            
            # 复制所有页面
            for page in reader.pages:
                writer.add_page(page)
            
            # 设置加密
            writer.encrypt(password)
            
            # 保存加密后的PDF
            with open(output_path, "wb") as output_file:
                writer.write(output_file)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"PDF加密失败: {str(e)}")
    
    def decrypt_pdf(self, pdf_path, password):
        """解密PDF文件"""
        try:
            output_dir = os.path.dirname(pdf_path)
            output_path = os.path.join(output_dir, f"decrypted_{int(time.time())}.pdf")
            
            reader = PdfReader(pdf_path)
            writer = PdfWriter()
            
            # 尝试解密
            if reader.is_encrypted:
                reader.decrypt(password)
            
            # 复制所有页面
            for page in reader.pages:
                writer.add_page(page)
            
            # 保存解密后的PDF
            with open(output_path, "wb") as output_file:
                writer.write(output_file)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"PDF解密失败: {str(e)}")
    
    def compress_pdf(self, pdf_path):
        """压缩PDF文件"""
        try:
            output_dir = os.path.dirname(pdf_path)
            output_path = os.path.join(output_dir, f"compressed_{int(time.time())}.pdf")
            
            reader = PdfReader(pdf_path)
            writer = PdfWriter()
            
            # 复制页面并应用压缩
            for page in reader.pages:
                writer.add_page(page)
                
            # 设置压缩选项
            writer.add_metadata(reader.metadata)
            
            # 保存压缩后的PDF
            with open(output_path, "wb") as output_file:
                writer.write(output_file)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"PDF压缩失败: {str(e)}")
    
    def split_pdf(self, pdf_path, start_page, end_page):
        """拆分PDF文件"""
        try:
            output_dir = os.path.dirname(pdf_path)
            output_path = os.path.join(output_dir, f"split_{int(time.time())}.pdf")
            
            reader = PdfReader(pdf_path)
            writer = PdfWriter()
            
            # 检查页码范围
            if start_page < 1 or end_page > len(reader.pages):
                raise ValueError("页码范围无效")
            
            # 复制选定范围的页面
            for page_num in range(start_page - 1, end_page):
                writer.add_page(reader.pages[page_num])
            
            # 保存拆分后的PDF
            with open(output_path, "wb") as output_file:
                writer.write(output_file)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"PDF拆分失败: {str(e)}")
    
    def merge_pdfs(self, pdf_paths, output_dir):
        """合并多个PDF文件"""
        try:
            writer = PdfWriter()
            
            # 遍历所有PDF文件并添加页面
            for pdf_path in pdf_paths:
                reader = PdfReader(pdf_path)
                for page in reader.pages:
                    writer.add_page(page)
            
            # 生成输出文件路径
            output_path = os.path.join(output_dir, "merged.pdf")
            
            # 保存合并后的PDF
            with open(output_path, "wb") as output_file:
                writer.write(output_file)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"PDF合并失败: {str(e)}")
    
    def rotate_pdf(self, pdf_path, rotation_angle, pages='all'):
        """旋转PDF页面
        :param pdf_path: PDF文件路径
        :param rotation_angle: 旋转角度（90、180、270）
        :param pages: 'all'表示所有页面，或者页码列表[1,2,3]
        """
        try:
            reader = PdfReader(pdf_path)
            writer = PdfWriter()
            
            # 确定需要旋转的页面
            if pages == 'all':
                pages = list(range(len(reader.pages)))
            else:
                # 将页码转换为索引（页码从1开始，索引从0开始）
                pages = [p-1 for p in pages]
            
            # 处理每一页
            for i in range(len(reader.pages)):
                page = reader.pages[i]
                if i in pages:
                    page.rotate(rotation_angle)
                writer.add_page(page)
            
            # 生成输出文件路径
            output_dir = os.path.dirname(pdf_path)
            output_path = os.path.join(output_dir, "rotated.pdf")
            
            # 保存旋转后的PDF
            with open(output_path, "wb") as output_file:
                writer.write(output_file)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"PDF旋转失败: {str(e)}")
    
    def extract_images(self, pdf_path, output_dir, image_type='all', min_size=100):
        """提取PDF中的图片
        :param pdf_path: PDF文件路径
        :param output_dir: 输出目录
        :param image_type: 图片类型 ('jpeg', 'png', 'all')
        :param min_size: 最小图片尺寸（像素）
        :return: 提取的图片路径列表
        """
        try:
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            # 打开PDF文件
            pdf_document = fitz.open(pdf_path)
            image_paths = []
            
            # 获取支持的图片类型
            supported_types = self.supported_image_types.get(image_type.lower(), self.supported_image_types['all'])
            
            # 遍历每一页
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                
                # 获取页面上的图片
                image_list = page.get_images()
                
                # 处理每个图片
                for img_index, img in enumerate(image_list):
                    xref = img[0]  # 图片引用号
                    base_image = pdf_document.extract_image(xref)
                    
                    if base_image:
                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"].lower()
                        
                        # 检查图片类型
                        if image_ext not in supported_types:
                            continue
                        
                        # 检查图片尺寸
                        try:
                            image = Image.open(io.BytesIO(image_bytes))
                            if min(image.size) < min_size:
                                continue
                        except Exception:
                            continue
                        
                        # 生成输出文件路径
                        image_path = os.path.join(
                            output_dir, 
                            f"page_{page_num + 1}_img_{img_index + 1}.{image_ext}"
                        )
                        
                        # 保存图片
                        with open(image_path, "wb") as image_file:
                            image_file.write(image_bytes)
                        image_paths.append(image_path)
            
            return image_paths
            
        except Exception as e:
            raise Exception(f"提取图片失败: {str(e)}")
        finally:
            if 'pdf_document' in locals():
                pdf_document.close()

    def add_watermark(self, pdf_path, watermark_text, output_dir, font_size=40, opacity=0.3, angle=45, color=(128,128,128)):
        """添加文字水印到PDF
        :param pdf_path: PDF文件路径
        :param watermark_text: 水印文字
        :param output_dir: 输出目录
        :param font_size: 字体大小
        :param opacity: 不透明度 (0-1)
        :param angle: 旋转角度
        :param color: RGB颜色元组
        :return: 输出文件路径
        """
        try:
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            # 创建水印PDF
            watermark_path = os.path.join(output_dir, f"watermark_{uuid.uuid4()}.pdf")
            
            # 获取PDF页面大小
            with open(pdf_path, 'rb') as file:
                pdf = PdfReader(file)
                if len(pdf.pages) > 0:
                    page = pdf.pages[0]
                    page_width = float(page.mediabox.width)
                    page_height = float(page.mediabox.height)
                else:
                    page_width, page_height = letter
            
            # 创建水印
            c = canvas.Canvas(watermark_path, pagesize=(page_width, page_height))
            c.setFillColorRGB(color[0]/255, color[1]/255, color[2]/255, opacity)
            
            # 使用 Windows 自带的中文字体
            font_path = "C:/Windows/Fonts/simhei.ttf"  # 黑体
            pdfmetrics.registerFont(TTFont('SimHei', font_path))
            c.setFont("SimHei", font_size)
            
            # 计算水印位置和重复次数
            text_width = c.stringWidth(watermark_text, "SimHei", font_size)
            text_height = font_size
            
            # 在页面上重复绘制水印
            x_count = int(page_width / (text_width * 2)) + 2
            y_count = int(page_height / (text_height * 2)) + 2
            
            for i in range(x_count):
                for j in range(y_count):
                    x = i * text_width * 2
                    y = j * text_height * 2
                    
                    # 保存当前状态
                    c.saveState()
                    # 移动到位置
                    c.translate(x, y)
                    # 旋转
                    c.rotate(angle)
                    # 绘制文字
                    c.drawString(0, 0, watermark_text)
                    # 恢复状态
                    c.restoreState()
            
            c.save()
            
            # 合并水印和原PDF
            output_path = os.path.join(output_dir, "watermarked.pdf")
            
            reader = PdfReader(pdf_path)
            watermark_reader = PdfReader(watermark_path)
            writer = PdfWriter()
            
            # 将水印添加到每一页
            for page in reader.pages:
                page.merge_page(watermark_reader.pages[0])
                writer.add_page(page)
            
            # 保存结果
            with open(output_path, "wb") as output_file:
                writer.write(output_file)
            
            # 删除临时水印文件
            os.remove(watermark_path)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"添加水印失败: {str(e)}")

    def add_image_watermark(self, pdf_path, image_path, output_dir, scale=0.3, opacity=0.3):
        """添加图片水印到PDF
        :param pdf_path: PDF文件路径
        :param image_path: 水印图片路径
        :param output_dir: 输出目录
        :param scale: 图片缩放比例 (0-1)
        :param opacity: 不透明度 (0-1)
        :return: 输出文件路径
        """
        try:
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            # 创建水印PDF
            watermark_path = os.path.join(output_dir, f"watermark_{uuid.uuid4()}.pdf")
            
            # 获取PDF页面大小
            with open(pdf_path, 'rb') as file:
                pdf = PdfReader(file)
                if len(pdf.pages) > 0:
                    page = pdf.pages[0]
                    page_width = float(page.mediabox.width)
                    page_height = float(page.mediabox.height)
                else:
                    page_width, page_height = letter
            
            # 创建水印
            c = canvas.Canvas(watermark_path, pagesize=(page_width, page_height))
            
            # 处理图片
            img = Image.open(image_path)
            img_width, img_height = img.size
            
            # 计算缩放后的尺寸
            scaled_width = img_width * scale
            scaled_height = img_height * scale
            
            # 计算水印位置和重复次数
            x_count = int(page_width / (scaled_width * 1.5)) + 1
            y_count = int(page_height / (scaled_height * 1.5)) + 1
            
            # 在页面上重复绘制水印
            for i in range(x_count):
                for j in range(y_count):
                    x = i * scaled_width * 1.5
                    y = j * scaled_height * 1.5
                    c.drawImage(
                        image_path, x, y,
                        width=scaled_width,
                        height=scaled_height,
                        mask='auto',
                        alpha=opacity
                    )
            
            c.save()
            
            # 合并水印和原PDF
            output_path = os.path.join(output_dir, "watermarked.pdf")
            
            reader = PdfReader(pdf_path)
            watermark_reader = PdfReader(watermark_path)
            writer = PdfWriter()
            
            # 将水印添加到每一页
            for page in reader.pages:
                page.merge_page(watermark_reader.pages[0])
                writer.add_page(page)
            
            # 保存结果
            with open(output_path, "wb") as output_file:
                writer.write(output_file)
            
            # 删除临时水印文件
            os.remove(watermark_path)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"添加图片水印失败: {str(e)}")
