from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import json
from pathlib import Path


scheduler = BackgroundScheduler(timezone="America/Denver")
SCHEDULE_DAYS = "mon-fri"
SCHEDULE_HOUR = 7
SCHEDULE_MINUTE = 0
SCHEDULER_ENABLED = True

SETTINGS_PATH = Path("/app/runtime/scheduler_settings.json")


def load_scheduler_settings():
    global SCHEDULER_ENABLED

    if SETTINGS_PATH.exists():
        try:
            data = json.loads(SETTINGS_PATH.read_text())
            SCHEDULER_ENABLED = bool(data.get("enabled", SCHEDULER_ENABLED))
        except Exception as e:
            print(f"=== Failed to load scheduler settings: {e} ===")


def save_scheduler_settings():
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_PATH.write_text(json.dumps({
        "enabled": SCHEDULER_ENABLED
    }, indent=2))

def start_scheduler(run_callback=None):
    load_scheduler_settings()

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
        "schedule_days": SCHEDULE_DAYS,
        "schedule_hour": SCHEDULE_HOUR,
        "schedule_minute": SCHEDULE_MINUTE,
        "jobs": jobs,
    }

def set_scheduler_enabled(enabled: bool):
    global SCHEDULER_ENABLED

    SCHEDULER_ENABLED = enabled
    save_scheduler_settings()

    job = scheduler.get_job("weekday_morning_run")

    if enabled:
        if job:
            job.resume()
        return {"enabled": True, "message": "Scheduler enabled"}

    if job:
        job.pause()

    return {"enabled": False, "message": "Scheduler disabled"}

