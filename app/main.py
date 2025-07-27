import os
import re
import uuid
import nest_asyncio
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from app.services.converter import download_and_convert
from app.utils.file_utils import cleanup_downloads

# ==============================
# 初期設定
# ==============================
load_dotenv()
nest_asyncio.apply()

app = FastAPI()

# LINE API
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

# ngrok の URL（環境変数に設定しておく）
NGROK_URL = os.getenv("NGROK_URL")  # 例: https://xxxxx.ngrok-free.app

# ダウンロードフォルダ
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "..", "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ==============================
# YouTube URL バリデーション
# ==============================
YOUTUBE_URL_PATTERN = re.compile(
    r"^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+$"
)

def is_valid_youtube_url(url: str) -> bool:
    return bool(YOUTUBE_URL_PATTERN.match(url))


# ==============================
# LINE Webhook
# ==============================
@app.post("/callback")
async def callback(request: Request):
    signature = request.headers.get("X-Line-Signature", "")
    body = await request.body()

    try:
        handler.handle(body.decode("utf-8"), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    return "OK"


# ==============================
# LINE メッセージハンドラ
# ==============================
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text.strip()

    # URL バリデーション
    if not is_valid_youtube_url(user_message):
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="対応していないURLです。YouTubeのURLを送ってください。")
        )
        return

    # 変換中メッセージを先に送る
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="変換中です。少々お待ちください…")
    )

    # 非同期で変換処理
    import asyncio
    asyncio.create_task(process_youtube(event, user_message))


# ==============================
# 変換処理
# ==============================
async def process_youtube(event, url: str):
    try:
        cleanup_downloads(DOWNLOAD_DIR, max_files=30)
        mp3_path, filename = await download_and_convert(url, DOWNLOAD_DIR)

        public_url = f"{NGROK_URL}/download/{os.path.basename(mp3_path)}"

        line_bot_api.push_message(
            event.source.user_id,
            TextSendMessage(
                text=f"変換が完了しました！\nこちらからダウンロードできます👇\n{public_url}"
            )
        )
    except Exception as e:
        line_bot_api.push_message(
            event.source.user_id,
            TextSendMessage(text=f"変換に失敗しました。再度お試しください。\n({str(e)})")
        )


# ==============================
# ダウンロード用エンドポイント
# ==============================
@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="ファイルが見つかりません")
    return FileResponse(file_path, filename=filename, media_type="audio/mpeg")
