import os
from pdf2docx import Converter
import time

class PDFConverter:
    def pdf_to_word(self, pdf_path):
        """将PDF转换为Word文档"""
        try:
            # 生成输出文件路径
            output_dir = os.path.dirname(pdf_path)
            output_path = os.path.join(output_dir, f"converted_{int(time.time())}.docx")
            
            # 转换PDF到Word
            cv = Converter(pdf_path)
            cv.convert(output_path)
            cv.close()
            
            return output_path
            
        except Exception as e:
            raise Exception(f"PDF转Word失败: {str(e)}")
