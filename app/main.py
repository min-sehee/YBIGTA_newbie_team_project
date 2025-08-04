from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import os

from app.user.user_router import user
from app.review.review_router import review
from app.config import PORT

# 기본 FastAPI 앱 생성(커스텀 JSON 응답 클래스 사용하지 않음)
app = FastAPI()

# DB 테이블 자동 생성
from database.mysql_connection import engine
from app.user.user_repository import Base
Base.metadata.create_all(bind=engine)

static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/")
async def root():
    index_file = os.path.join(static_path, "index.html")
    return FileResponse(index_file)

app.include_router(user)
app.include_router(review)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
