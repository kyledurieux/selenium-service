from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging

scheduler = BackgroundScheduler(timezone="America/Denver")

logger = logging.getLogger(__name__)


def test_scheduled_job():
    logger.warning(f"SCHEDULER TEST RUN: {datetime.now()}")


def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(
            test_scheduled_job,
            CronTrigger(second="0"),
            id="test_job",
            replace_existing=True,
        )

        scheduler.start()
        logger.warning("Scheduler started")