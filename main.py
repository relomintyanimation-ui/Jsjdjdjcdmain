from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from telethon import TelegramClient

# Aapke diye gaye Telegram API details
API_ID = 33592413
API_HASH = "bf4718cb6674f73fdcdfe94bf8baece7"
BOT_TOKEN = "8404457169:AAELzsfm4ZiDXTG3zyS2n_5TL05uWHPAiMA"

app = FastAPI()
client = TelegramClient('bot_session', API_ID, API_HASH)

@app.on_event("startup")
async def startup_event():
    # Bot token ke sath Telegram se connect karna
    await client.start(bot_token=BOT_TOKEN)

@app.get("/{link:path}")
async def download_file(link: str):
    try:
        # Agar URL me https:// laga hai toh use clean karna
        clean_link = link.replace("https://", "").replace("http://", "")
        
        # Link se channel name aur message ID nikalna (e.g., t.me/channelname/123)
        parts = clean_link.split('/')
        msg_id = int(parts[-1])
        channel = parts[-2]
        
        # Telegram se message fetch karna
        message = await client.get_messages(channel, ids=msg_id)
        if not message or not message.media:
            raise HTTPException(status_code=404, detail="File nahi mili, ya channel private hai/link galat hai.")

        # File ko stream karne ka function (1MB chunks me)
        async def stream_file():
            async for chunk in client.iter_download(message.media, chunk_size=1024*1024):
                yield chunk

        # Original file ka naam nikalna (agar available ho)
        file_name = "downloaded_file"
        if hasattr(message, 'file') and message.file and message.file.name:
            file_name = message.file.name

        # Browser ko download shuru karne ka signal dena
        return StreamingResponse(
            stream_file(), 
            media_type="application/octet-stream",
            headers={"Content-Disposition": f'attachment; filename="{file_name}"'}
        )
    except Exception as e:
        return {"error": f"Kuch galat ho gaya: {str(e)}"}
