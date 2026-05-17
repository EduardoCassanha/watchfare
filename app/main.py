from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv
from app.scheduler import start_scheduler
from app.searcher import run_search
from app.storage import load_history, save_result

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = start_scheduler()
    yield
    scheduler.shutdown()


app = FastAPI(title="Watchfare", lifespan=lifespan)


@app.get("/status")
def status():
    return {"status": "ok", "message": "Watchfare is running"}


@app.get("/check")
def check():
    result = run_search()
    save_result(result)
    return result


@app.get("/history")
def history():
    return load_history()