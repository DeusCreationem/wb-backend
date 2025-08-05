from fastapi import FastAPI, Depends
from pydantic import BaseModel
import telebot
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import Base, SessionLocal, engine          # <- импортируем Base отсюда
import models                                            # <- регистрируем модели

# ⚠️  Твой токен и chat-id (если группа — будет отрицательное число)
TOKEN   = "8438618735:AAFF50eYJVCkSsedaYvJY77KItLo9YnbTO4"
CHAT_ID = 1132706729

bot = telebot.TeleBot(TOKEN)

# Создаём таблицы (если ещё нет)
Base.metadata.create_all(bind=engine)

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://gilded-gumdrop-f1c23e.netlify.app"],
    allow_methods=["POST"],
    allow_headers=["*"],
)


class ApplicationForm(BaseModel):
    name: str
    phone: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/submit")
def submit_form(form: ApplicationForm, db: Session = Depends(get_db)):
    # 1) пишем в БД
    application = models.Application(name=form.name, phone=form.phone)
    db.add(application)
    db.commit()
    db.refresh(application)

    # 2) шлём уведомление в Telegram
    msg = f"📥 Новая заявка!\n\nИмя: {form.name}\nТелефон: {form.phone}"
    bot.send_message(CHAT_ID, msg)

    return {"status": "success", "id": application.id}
