from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = BackgroundScheduler(timezone="America/Denver")
SCHEDULE_DAYS = "mon-fri"
SCHEDULE_HOUR = 7
SCHEDULE_MINUTE = 0
SCHEDULER_ENABLED = True

def start_scheduler(run_callback=None):
    if scheduler.running:
        return

    print("=== Scheduler started ===")

    # Weekdays at 7:00 AM Mountain Time
    if run_callback and SCHEDULER_ENABLED:
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
    
def get_scheduler_status():
    jobs = []

    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "next_run_time": str(job.next_run_time),
            "trigger": str(job.trigger),
        })

    return {
        "running": scheduler.running,
        "enabled": SCHEDULER_ENABLED,
        "timezone": str(scheduler.timezone),
        "jobs": jobs,
    }
