import yt_dlp
import uuid
import os
import asyncio
import subprocess

async def download_and_convert(url: str, download_dir: str):
    unique_id = str(uuid.uuid4())
    video_path = os.path.join(download_dir, f"{unique_id}.mp4")
    mp3_path = os.path.join(download_dir, f"{unique_id}.mp3")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': video_path,
        'quiet': True,
        'noplaylist': True,
    }

        # ダウンロード
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).download([url]))
        print(f"ダウンロード後: {video_path} exists? {os.path.exists(video_path)}")  # 追加
    except Exception as e:
        print(f"yt_dlp error: {e}")
        raise ValueError("動画のダウンロードに失敗しました")

    # ...existing code...
    # ffmpegでmp3変換
    try:
        result = subprocess.run(
            ['ffmpeg', '-y', '-i', video_path, '-vn', '-acodec', 'libmp3lame', mp3_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if result.returncode != 0:
            print("ffmpeg stderr:", result.stderr.decode())  # 追加
            raise Exception(result.stderr.decode())
    except Exception:
        if os.path.exists(video_path):
            os.remove(video_path)
        raise ValueError("音声変換に失敗しました")
# ...existing code...

    # mp4削除
    if os.path.exists(video_path):
        os.remove(video_path)

    if not os.path.exists(mp3_path):
        raise ValueError("MP3ファイルが生成されませんでした")

    return mp3_path, f"{unique_id}.mp3"
