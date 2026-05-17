import os
from apscheduler.schedulers.background import BackgroundScheduler
from app.searcher import run_search
from app.notifier import notify
from app.storage import save_result


def scheduled_job() -> None:
    print("Running scheduled search...")
    result = run_search()
    save_result(result)
    notify(result)
    print(f"Done. Best price: R$ {result.best_price:.0f}")


def start_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler()
    time = os.getenv("HORARIO_VERIFICACAO", "09:00")
    hour, minute = time.split(":")
    scheduler.add_job(
        scheduled_job,
        trigger="cron",
        hour=int(hour),
        minute=int(minute),
    )
    scheduler.start()
    return scheduler