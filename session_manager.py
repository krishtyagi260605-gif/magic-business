import os
import shutil
import time
import uuid
from config import OUTPUT_DIR

class SessionManager:
    @staticmethod
    def create_session() -> str:
        """Create a new session ID and its corresponding output folder."""
        session_id = str(uuid.uuid4())
        session_dir = os.path.join(OUTPUT_DIR, session_id)
        os.makedirs(session_dir, exist_ok=True)
        return session_id

    @staticmethod
    def get_session_dir(session_id: str) -> str:
        """Get path to session output folder, ensuring it exists."""
        session_dir = os.path.join(OUTPUT_DIR, session_id)
        os.makedirs(session_dir, exist_ok=True)
        return session_dir

    @staticmethod
    def list_files(session_id: str) -> list[str]:
        """List all files generated in the session directory."""
        session_dir = SessionManager.get_session_dir(session_id)
        if not os.path.exists(session_dir):
            return []
        return [f for f in os.listdir(session_dir) if os.path.isfile(os.path.join(session_dir, f))]

    @staticmethod
    def clean_old_sessions(max_age_hours: int = 24):
        """Clean up session directories older than max_age_hours."""
        if not os.path.exists(OUTPUT_DIR):
            return
            
        now = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for folder_name in os.listdir(OUTPUT_DIR):
            folder_path = os.path.join(OUTPUT_DIR, folder_name)
            if not os.path.isdir(folder_path):
                continue
                
            try:
                # Check modification time of the folder
                mtime = os.path.getmtime(folder_path)
                if (now - mtime) > max_age_seconds:
                    print(f"Cleaning up expired session directory: {folder_path}")
                    shutil.rmtree(folder_path)
            except Exception as e:
                print(f"Error cleaning session directory {folder_path}: {e}")
