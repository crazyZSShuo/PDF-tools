import os
import shutil
from datetime import datetime, timedelta

class FileManager:
    def __init__(self, base_dir="temp", max_age_hours=24):
        self.base_dir = base_dir
        self.max_age_hours = max_age_hours
        
        # 确保基础目录存在
        os.makedirs(self.base_dir, exist_ok=True)
    
    def create_session_directory(self, session_id):
        """为会话创建目录"""
        session_dir = os.path.join(self.base_dir, session_id)
        os.makedirs(session_dir, exist_ok=True)
        return session_dir
    
    def cleanup_old_files(self):
        """清理过期文件"""
        cutoff_time = datetime.now() - timedelta(hours=self.max_age_hours)
        
        for item in os.listdir(self.base_dir):
            item_path = os.path.join(self.base_dir, item)
            if os.path.getctime(item_path) < cutoff_time.timestamp():
                try:
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                except Exception as e:
                    print(f"清理文件失败 {item_path}: {str(e)}")
    
    def save_uploaded_file(self, uploaded_file, session_dir):
        """保存上传的文件"""
        file_path = os.path.join(session_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    
    def get_file_size(self, file_path):
        """获取文件大小（MB）"""
        return os.path.getsize(file_path) / (1024 * 1024)
    
    def is_file_allowed(self, file_path, max_size_mb=100):
        """检查文件是否允许（大小限制）"""
        return self.get_file_size(file_path) <= max_size_mb
