from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = BackgroundScheduler(timezone="America/Denver")
SCHEDULE_DAYS = "mon-fri"
SCHEDULE_HOUR = 7
SCHEDULE_MINUTE = 0

def start_scheduler(run_callback=None):
    if scheduler.running:
        return

    print("=== Scheduler started ===")

    # Weekdays at 7:00 AM Mountain Time
    if run_callback:
        scheduler.add_job(
            run_callback,
            CronTrigger(
                day_of_week=SCHEDULE_DAYS,
                hour=SCHEDULE_HOUR,
                minute=SCHEDULE_MINUTE,
            ),
            
            id="weekday_morning_run",
            replace_existing=True,
        )

        print("=== Weekday 7AM CNH schedule registered ===")

    scheduler.start()