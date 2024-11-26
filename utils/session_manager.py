import streamlit as st
import uuid
import os
from datetime import datetime

class SessionManager:
    def initialize_session(self):
        """初始化会话状态"""
        if 'session_id' not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
            
        if 'work_dir' not in st.session_state:
            work_dir = os.path.join("temp", st.session_state.session_id)
            os.makedirs(work_dir, exist_ok=True)
            st.session_state.work_dir = work_dir
            
        if 'created_at' not in st.session_state:
            st.session_state.created_at = datetime.now()
    
    def get_session_id(self):
        """获取会话ID"""
        return st.session_state.session_id
    
    def get_work_dir(self):
        """获取工作目录"""
        return st.session_state.work_dir
    
    def clear_session(self):
        """清理会话数据"""
        if 'work_dir' in st.session_state:
            work_dir = st.session_state.work_dir
            if os.path.exists(work_dir):
                try:
                    for item in os.listdir(work_dir):
                        item_path = os.path.join(work_dir, item)
                        if os.path.isfile(item_path):
                            os.remove(item_path)
                except Exception as e:
                    print(f"清理会话文件失败: {str(e)}")
    
    def is_session_expired(self, max_age_hours=24):
        """检查会话是否过期"""
        if 'created_at' in st.session_state:
            age = datetime.now() - st.session_state.created_at
            return age.total_seconds() > (max_age_hours * 3600)
        return True
