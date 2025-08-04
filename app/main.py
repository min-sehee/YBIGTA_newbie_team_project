from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import os

from app.user.user_router import user
from app.review.review_router import review
from app.config import PORT

app = FastAPI()
static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

# 루트 URL에서 index.html 반환 코드 추가
@app.get("/")
async def root():
    index_file = os.path.join(static_path, "index.html")
    return FileResponse(index_file)

app.include_router(user)
app.include_router(review)

if __name__=="__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
