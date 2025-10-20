import logging
from typing import Callable, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler

def create_scheduler() -> AsyncIOScheduler:
    logging.getLogger("apscheduler").setLevel(logging.INFO)
    scheduler = AsyncIOScheduler()
    return scheduler


def add_memory_check_job(scheduler: AsyncIOScheduler, func: Callable, app, timeout_minutes: Optional[int] = 1) -> None:
    scheduler.add_job(func, "interval", minutes=timeout_minutes, args=[app])

async def start_scheduler(scheduler: AsyncIOScheduler) -> None:
    try:
        scheduler.start()
        logging.info("Scheduler started")
    except Exception as e:
        logging.error(f"Failed to start scheduler: {e}")

def stop_scheduler(scheduler: AsyncIOScheduler) -> None:
    try:
        if scheduler.running:
            scheduler.shutdown(wait=False)
            logging.info("Scheduler stopped")
    except Exception as e:
        logging.error(f"Error stopping scheduler: {e}")
