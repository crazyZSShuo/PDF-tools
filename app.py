import streamlit as st
import os
import uuid
from datetime import datetime
import time
import shutil
from modules.pdf_converter import PDFConverter
from modules.pdf_processor import PDFProcessor
from utils.file_handler import FileManager
from utils.session_manager import SessionManager

# 页面配置
st.set_page_config(
    page_title="PDF工具集",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化会话管理器
session_manager = SessionManager()
session_manager.initialize_session()

# 初始化文件管理器
file_manager = FileManager(base_dir="temp")

def get_output_filename(original_filename, prefix):
    """生成输出文件名，保留原始文件名"""
    # 获取文件名（不含扩展名）和扩展名
    name, ext = os.path.splitext(original_filename)
    # 根据不同处理类型设置新的扩展名
    new_ext = '.docx' if prefix == 'converted' else '.pdf'
    # 返回新的文件名
    return f"{name}_{prefix}{new_ext}"

def save_uploaded_file(uploaded_file, work_dir):
    """保存上传的文件并返回保存路径"""
    if not os.path.exists(work_dir):
        os.makedirs(work_dir)
    file_path = os.path.join(work_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def process_download(output_path, original_filename, prefix):
    """处理文件下载"""
    try:
        if os.path.exists(output_path):
            with open(output_path, "rb") as file:
                output_filename = get_output_filename(original_filename, prefix)
                file_bytes = file.read()
                return file_bytes, output_filename
        return None, None
    except Exception as e:
        st.error(f"文件处理失败: {str(e)}")
        return None, None

def main():
    st.title("PDF工具集")
    
    # 侧边栏 - 功能选择
    st.sidebar.title("功能选择")
    option = st.sidebar.selectbox(
        "选择功能",
        ["PDF转Word", "PDF处理工具", "PDF合并", "提取图片", "添加水印"]
    )
    
    # 根据选择显示不同功能
    if option == "PDF转Word":
        pdf_to_word_page()
    elif option == "PDF合并":
        merge_pdfs_page()
    elif option == "提取图片":
        extract_images_page()
    elif option == "添加水印":
        add_watermark_page()
    else:
        pdf_tools_page()

def pdf_to_word_page():
    st.header("PDF转Word")
    
    uploaded_file = st.file_uploader("上传PDF文件", type=["pdf"])
    
    if uploaded_file:
        try:
            # 保存上传的文件
            pdf_path = save_uploaded_file(uploaded_file, st.session_state.work_dir)
            
            if st.button("转换为Word"):
                with st.spinner("正在转换..."):
                    converter = PDFConverter()
                    docx_path = converter.pdf_to_word(pdf_path)
                    
                    # 显示下载按钮
                    file_bytes, output_filename = process_download(docx_path, uploaded_file.name, "converted")
                    if file_bytes:
                        st.download_button(
                            label="下载Word文档",
                            data=file_bytes,
                            file_name=output_filename,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
        except Exception as e:
            st.error(f"转换失败: {str(e)}")

def pdf_tools_page():
    st.header("PDF处理工具")
    
    uploaded_file = st.file_uploader("上传PDF文件", type=["pdf"])
    
    if uploaded_file:
        # 保存上传的文件
        pdf_path = save_uploaded_file(uploaded_file, st.session_state.work_dir)
        
        # PDF处理选项
        tool_option = st.selectbox(
            "选择处理工具",
            ["加密PDF", "解密PDF", "压缩PDF", "PDF拆分", "PDF旋转"]
        )
        
        processor = PDFProcessor()
        
        if tool_option == "加密PDF":
            password = st.text_input("设置密码", type="password")
            if st.button("加密") and password:
                with st.spinner("正在加密..."):
                    try:
                        output_path = processor.encrypt_pdf(pdf_path, password)
                        file_bytes, output_filename = process_download(output_path, uploaded_file.name, "encrypted")
                        if file_bytes:
                            st.download_button(
                                label="下载加密PDF",
                                data=file_bytes,
                                file_name=output_filename,
                                mime="application/pdf"
                            )
                    except Exception as e:
                        st.error(f"加密失败: {str(e)}")
                        
        elif tool_option == "解密PDF":
            password = st.text_input("输入密码", type="password")
            if st.button("解密") and password:
                with st.spinner("正在解密..."):
                    try:
                        output_path = processor.decrypt_pdf(pdf_path, password)
                        file_bytes, output_filename = process_download(output_path, uploaded_file.name, "decrypted")
                        if file_bytes:
                            st.download_button(
                                label="下载解密PDF",
                                data=file_bytes,
                                file_name=output_filename,
                                mime="application/pdf"
                            )
                    except Exception as e:
                        st.error("密码错误或PDF解密失败")
                        
        elif tool_option == "压缩PDF":
            if st.button("压缩"):
                with st.spinner("正在压缩..."):
                    try:
                        output_path = processor.compress_pdf(pdf_path)
                        file_bytes, output_filename = process_download(output_path, uploaded_file.name, "compressed")
                        if file_bytes:
                            st.download_button(
                                label="下载压缩PDF",
                                data=file_bytes,
                                file_name=output_filename,
                                mime="application/pdf"
                            )
                    except Exception as e:
                        st.error(f"压缩失败: {str(e)}")
                        
        elif tool_option == "PDF拆分":
            total_pages = processor.get_page_count(pdf_path)
            st.write(f"总页数: {total_pages}")
            
            start_page = st.number_input("起始页", min_value=1, max_value=total_pages, value=1)
            end_page = st.number_input("结束页", min_value=start_page, max_value=total_pages, value=total_pages)
            
            if st.button("拆分"):
                with st.spinner("正在拆分..."):
                    try:
                        output_path = processor.split_pdf(pdf_path, start_page, end_page)
                        file_bytes, output_filename = process_download(output_path, uploaded_file.name, f"split_{start_page}-{end_page}")
                        if file_bytes:
                            st.download_button(
                                label="下载拆分PDF",
                                data=file_bytes,
                                file_name=output_filename,
                                mime="application/pdf"
                            )
                    except Exception as e:
                        st.error(f"拆分失败: {str(e)}")
                        
        elif tool_option == "PDF旋转":
            # 获取总页数
            total_pages = processor.get_page_count(pdf_path)
            st.write(f"总页数: {total_pages}")
            
            # 旋转选项
            rotation_angle = st.selectbox("选择旋转角度", [90, 180, 270])
            
            # 页面选择
            page_option = st.radio("选择要旋转的页面", ["所有页面", "指定页面"])
            pages = 'all'
            
            if page_option == "指定页面":
                page_input = st.text_input("输入页码（例如：1,3,5-7）")
                if page_input:
                    try:
                        pages = []
                        for part in page_input.split(','):
                            if '-' in part:
                                start, end = map(int, part.split('-'))
                                pages.extend(range(start, end + 1))
                            else:
                                pages.append(int(part))
                    except:
                        st.error("页码格式无效")
                        return
            
            if st.button("旋转"):
                with st.spinner("正在旋转..."):
                    try:
                        output_path = processor.rotate_pdf(pdf_path, rotation_angle, pages)
                        # 生成旋转文件名后缀
                        rotate_suffix = f"rotated_{rotation_angle}deg"
                        if pages != 'all':
                            rotate_suffix += f"_pages_{min(pages)}-{max(pages)}"
                        
                        file_bytes, output_filename = process_download(output_path, uploaded_file.name, rotate_suffix)
                        if file_bytes:
                            st.download_button(
                                label="下载旋转后的PDF",
                                data=file_bytes,
                                file_name=output_filename,
                                mime="application/pdf"
                            )
                    except Exception as e:
                        st.error(f"旋转失败: {str(e)}")

def merge_pdfs_page():
    st.header("PDF合并")
    
    # 使用session_state来存储上传的文件
    if 'uploaded_pdfs' not in st.session_state:
        st.session_state.uploaded_pdfs = []
    
    # 文件上传组件
    uploaded_file = st.file_uploader("上传PDF文件（可多次上传）", type=["pdf"], key="pdf_merger")
    
    if uploaded_file:
        # 检查文件是否已经上传
        if uploaded_file.name not in [f.name for f in st.session_state.uploaded_pdfs]:
            # 保存上传的文件
            pdf_path = save_uploaded_file(uploaded_file, st.session_state.work_dir)
            # 将文件信息添加到列表
            st.session_state.uploaded_pdfs.append(uploaded_file)
            st.experimental_rerun()
    
    # 显示已上传的文件
    if st.session_state.uploaded_pdfs:
        st.write("已上传的文件：")
        for i, pdf in enumerate(st.session_state.uploaded_pdfs):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"{i+1}. {pdf.name}")
            with col2:
                if st.button("删除", key=f"del_{i}"):
                    st.session_state.uploaded_pdfs.pop(i)
                    st.experimental_rerun()
        
        # 文件排序
        if len(st.session_state.uploaded_pdfs) > 1:
            st.write("拖动调整合并顺序：")
            order = st.text_input("输入文件序号（例如：1,3,2）", value=",".join(str(i+1) for i in range(len(st.session_state.uploaded_pdfs))))
            
            try:
                # 解析顺序
                new_order = [int(x.strip())-1 for x in order.split(",")]
                if sorted(new_order) != list(range(len(st.session_state.uploaded_pdfs))):
                    st.error("序号无效")
                    return
            except:
                st.error("序号格式无效")
                return
            
            # 合并按钮
            if st.button("合并PDF"):
                with st.spinner("正在合并..."):
                    try:
                        processor = PDFProcessor()
                        # 按指定顺序获取文件路径
                        pdf_paths = [os.path.join(st.session_state.work_dir, st.session_state.uploaded_pdfs[i].name) for i in new_order]
                        output_path = processor.merge_pdfs(pdf_paths, st.session_state.work_dir)
                        
                        # 生成合并后的文件名（使用所有文件名的前缀）
                        merged_names = "_".join(os.path.splitext(st.session_state.uploaded_pdfs[i].name)[0] for i in new_order)
                        if len(merged_names) > 100:  # 如果名字太长，只使用第一个文件名
                            merged_names = os.path.splitext(st.session_state.uploaded_pdfs[new_order[0]].name)[0]
                        
                        file_bytes, output_filename = process_download(output_path, f"{merged_names}.pdf", "merged")
                        if file_bytes:
                            st.download_button(
                                label="下载合并后的PDF",
                                data=file_bytes,
                                file_name=output_filename,
                                mime="application/pdf"
                            )
                    except Exception as e:
                        st.error(f"合并失败: {str(e)}")
        
        # 清空按钮
        if st.button("清空所有"):
            st.session_state.uploaded_pdfs = []
            st.experimental_rerun()
    else:
        st.info("请上传需要合并的PDF文件")

def extract_images_page():
    st.header("提取PDF中的图片")
    
    uploaded_file = st.file_uploader("上传PDF文件", type=["pdf"])
    
    if uploaded_file:
        # 保存上传的文件
        pdf_path = save_uploaded_file(uploaded_file, st.session_state.work_dir)
        
        # 提取选项
        col1, col2 = st.columns(2)
        with col1:
            image_type = st.selectbox("图片类型", ["all", "jpeg", "png"])
        with col2:
            min_size = st.number_input("最小图片尺寸（像素）", min_value=50, value=100, step=50)
        
        if st.button("提取图片"):
            with st.spinner("正在提取图片..."):
                try:
                    processor = PDFProcessor()
                    image_paths = processor.extract_images(
                        pdf_path, 
                        st.session_state.work_dir,
                        image_type=image_type,  
                        min_size=min_size
                    )
                    
                    if image_paths:
                        st.success(f"成功提取 {len(image_paths)} 张图片")
                        
                        # 创建zip文件
                        import zipfile
                        zip_path = os.path.join(st.session_state.work_dir, "images.zip")
                        with zipfile.ZipFile(zip_path, 'w') as zipf:
                            for img_path in image_paths:
                                zipf.write(img_path, os.path.basename(img_path))
                        
                        # 提供zip下载
                        with open(zip_path, "rb") as f:
                            st.download_button(
                                label="下载所有图片(ZIP)",
                                data=f,
                                file_name=f"{os.path.splitext(uploaded_file.name)[0]}_images.zip",
                                mime="application/zip"
                            )
                        
                        # 预览图片
                        st.write("图片预览：")
                        cols = st.columns(3)
                        for i, img_path in enumerate(image_paths):
                            with cols[i % 3]:
                                st.image(img_path, caption=f"图片 {i+1}")
                                with open(img_path, "rb") as img_file:
                                    st.download_button(
                                        label=f"下载图片 {i+1}",
                                        data=img_file,
                                        file_name=os.path.basename(img_path),
                                        mime=f"image/{os.path.splitext(img_path)[1][1:]}"
                                    )
                    else:
                        st.warning("未找到符合条件的图片")
                        
                except Exception as e:
                    st.error(f"提取图片失败: {str(e)}")

def add_watermark_page():
    st.header("添加PDF水印")
    
    uploaded_file = st.file_uploader("上传PDF文件", type=["pdf"], key="watermark_pdf")
    
    if uploaded_file:
        # 保存上传的文件
        pdf_path = save_uploaded_file(uploaded_file, st.session_state.work_dir)
        
        # 水印类型选择
        watermark_type = st.radio("水印类型", ["文字水印", "图片水印"])
        
        try:
            processor = PDFProcessor()
            
            if watermark_type == "文字水印":
                # 文字水印选项
                col1, col2 = st.columns(2)
                with col1:
                    watermark_text = st.text_input("水印文字", "机密文件")
                    font_size = st.number_input("字体大小", min_value=10, value=40, step=5)
                with col2:
                    opacity = st.slider("不透明度", 0.1, 1.0, 0.3, 0.1)
                    angle = st.number_input("旋转角度", min_value=0, value=45, step=15)
                
                # 颜色选择
                color = st.color_picker("水印颜色", "#808080")
                # 将颜色转换为RGB元组
                color = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                
                if st.button("添加水印"):
                    with st.spinner("正在添加水印..."):
                        try:
                            output_path = processor.add_watermark(
                                pdf_path,
                                watermark_text,
                                st.session_state.work_dir,
                                font_size=font_size,
                                opacity=opacity,
                                angle=angle,
                                color=color
                            )
                            
                            file_bytes, output_filename = process_download(
                                output_path,
                                uploaded_file.name,
                                f"watermark_text"
                            )
                            if file_bytes:
                                st.download_button(
                                    label="下载添加水印的PDF",
                                    data=file_bytes,
                                    file_name=output_filename,
                                    mime="application/pdf"
                                )
                        except Exception as e:
                            st.error(f"添加水印失败: {str(e)}")
            
            else:  # 图片水印
                uploaded_image = st.file_uploader("上传水印图片", type=["png", "jpg", "jpeg"], key="watermark_image")
                
                if uploaded_image:
                    # 保存水印图片
                    image_path = save_uploaded_file(uploaded_image, st.session_state.work_dir)
                    
                    # 显示水印图片预览
                    st.image(image_path, caption="水印图片预览", width=200)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        scale = st.slider("图片大小", 0.1, 1.0, 0.3, 0.1)
                    with col2:
                        opacity = st.slider("不透明度", 0.1, 1.0, 0.3, 0.1)
                    
                    if st.button("添加水印"):
                        with st.spinner("正在添加水印..."):
                            try:
                                output_path = processor.add_image_watermark(
                                    pdf_path,
                                    image_path,
                                    st.session_state.work_dir,
                                    scale=scale,
                                    opacity=opacity
                                )
                                
                                file_bytes, output_filename = process_download(
                                    output_path,
                                    uploaded_file.name,
                                    f"watermark_image"
                                )
                                if file_bytes:
                                    st.download_button(
                                        label="下载添加水印的PDF",
                                        data=file_bytes,
                                        file_name=output_filename,
                                        mime="application/pdf"
                                    )
                            except Exception as e:
                                st.error(f"添加水印失败: {str(e)}")
                
        except Exception as e:
            st.error(f"处理失败: {str(e)}")

if __name__ == "__main__":
    main()
