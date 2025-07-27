import os
from glob import glob

def cleanup_downloads(download_dir: str, max_files: int = 30):
    files = sorted(
        glob(os.path.join(download_dir, "*.mp3")),
        key=os.path.getctime
    )
    if len(files) > max_files:
        for f in files[:len(files) - max_files]:
            try:
                os.remove(f)
            except Exception:
                pass
