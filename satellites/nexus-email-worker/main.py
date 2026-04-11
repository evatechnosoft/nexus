import os
import asyncio
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

import worker

# .env yükle
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
log = logging.getLogger("nexus-email-worker")

async def run_email_check():
    log.info("Starting email check cycle...")
    try:
        await worker.check_and_process_emails()
    except Exception as e:
        log.error(f"Worker Error: {e}")

async def main():
    log.info("Nexus Email Worker (Satellite) Initializing...")
    
    interval = int(os.getenv("WATCH_INTERVAL_MIN", 5))
    scheduler = AsyncIOScheduler()
    
    scheduler.add_job(
        run_email_check,
        "interval",
        minutes=interval,
        id="email_worker_job",
        next_run_time=datetime.now()
    )
    
    scheduler.start()
    log.info(f"Worker started. Running every {interval} minutes.")
    
    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
