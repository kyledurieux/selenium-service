from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import json
from pathlib import Path


scheduler = BackgroundScheduler(timezone="America/Denver")
SCHEDULE_DAYS = "mon-fri"
SCHEDULE_HOUR = 7
SCHEDULE_MINUTE = 0
SCHEDULER_ENABLED = True
RUN_CALLBACK = None
USER_RUN_CALLBACK = None

SETTINGS_PATH = Path("/app/runtime/scheduler_settings.json")
USER_SCHEDULES_PATH = Path("/app/runtime/user_schedules.json")


def load_scheduler_settings():
    global SCHEDULER_ENABLED, SCHEDULE_DAYS, SCHEDULE_HOUR, SCHEDULE_MINUTE

    if not SETTINGS_PATH.exists():
        return

    try:
        data = json.loads(SETTINGS_PATH.read_text())

        SCHEDULER_ENABLED = bool(data.get("enabled", SCHEDULER_ENABLED))
        SCHEDULE_DAYS = data.get("schedule_days", SCHEDULE_DAYS)
        SCHEDULE_HOUR = int(data.get("schedule_hour", SCHEDULE_HOUR))
        SCHEDULE_MINUTE = int(data.get("schedule_minute", SCHEDULE_MINUTE))
        if SCHEDULE_HOUR < 0 or SCHEDULE_HOUR > 23:
            print("=== Invalid schedule hour, resetting to 7 ===")
            SCHEDULE_HOUR = 7

        if SCHEDULE_MINUTE < 0 or SCHEDULE_MINUTE > 59:
            print("=== Invalid schedule minute, resetting to 0 ===")
            SCHEDULE_MINUTE = 0

    except Exception as e:
        print(f"=== Failed to load scheduler settings: {e} ===")

def save_scheduler_settings():
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_PATH.write_text(json.dumps({
        "enabled": SCHEDULER_ENABLED,
        "schedule_days": SCHEDULE_DAYS,
        "schedule_hour": SCHEDULE_HOUR,
        "schedule_minute": SCHEDULE_MINUTE
    }, indent=2))


def start_scheduler(run_callback=None, user_run_callback=None):
    global RUN_CALLBACK, USER_RUN_CALLBACK
    RUN_CALLBACK = run_callback
    USER_RUN_CALLBACK = user_run_callback

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
    
    schedules = load_user_schedules()

    for username, config in schedules.items():
        register_user_schedule_job(username, config)
    
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
        if not job and RUN_CALLBACK:
            scheduler.add_job(
                RUN_CALLBACK,
                CronTrigger(
                    day_of_week=SCHEDULE_DAYS,
                    hour=SCHEDULE_HOUR,
                    minute=SCHEDULE_MINUTE,
                ),
                id="weekday_morning_run",
                replace_existing=True,
            )

            job = scheduler.get_job("weekday_morning_run")

        if job:
            job.resume()

        return {"enabled": True, "message": "Scheduler enabled"}

    if job:
        job.pause()

    return {"enabled": False, "message": "Scheduler disabled"}

def update_scheduler_schedule(days: str, hour: int, minute: int):
    global SCHEDULE_DAYS, SCHEDULE_HOUR, SCHEDULE_MINUTE

    SCHEDULE_DAYS = days
    SCHEDULE_HOUR = hour
    SCHEDULE_MINUTE = minute

    save_scheduler_settings()

    job = scheduler.get_job("weekday_morning_run")

    if job:
        job.reschedule(
            trigger=CronTrigger(
                day_of_week=SCHEDULE_DAYS,
                hour=SCHEDULE_HOUR,
                minute=SCHEDULE_MINUTE,
            )
        )

    return {
        "message": "Scheduler schedule updated",
        "schedule_days": SCHEDULE_DAYS,
        "schedule_hour": SCHEDULE_HOUR,
        "schedule_minute": SCHEDULE_MINUTE,
    }

def load_user_schedules():
    if not USER_SCHEDULES_PATH.exists():
        return {}

    try:
        return json.loads(USER_SCHEDULES_PATH.read_text())
    except Exception as e:
        print(f"=== Failed to load user schedules: {e} ===")
        return {}


def save_user_schedules(data: dict):
    USER_SCHEDULES_PATH.parent.mkdir(parents=True, exist_ok=True)
    USER_SCHEDULES_PATH.write_text(json.dumps(data, indent=2))

def register_user_schedule_job(username: str, config: dict):
    if not USER_RUN_CALLBACK:
        return

    job_id = f"user_schedule_{username}"

    existing = scheduler.get_job(job_id)
    if existing:
        existing.remove()

    if not config.get("enabled", False):
        return

    scheduler.add_job(
        USER_RUN_CALLBACK,
        CronTrigger(
            day_of_week=config.get("days", "mon-fri"),
            hour=int(config.get("hour", 7)),
            minute=int(config.get("minute", 0)),
        ),
        args=[username],
        id=job_id,
        replace_existing=True,
    )

def get_user_schedule(username: str):
    schedules = load_user_schedules()

    return schedules.get(username, {
        "enabled": False,
        "days": "mon-fri",
        "hour": 7,
        "minute": 0
    })


def update_user_schedule(username: str, enabled: bool, days: str, hour: int, minute: int):
    schedules = load_user_schedules()

    schedules[username] = {
        "enabled": enabled,
        "days": days,
        "hour": hour,
        "minute": minute
    }

    save_user_schedules(schedules)
    register_user_schedule_job(username, schedules[username])

    return {
        "username": username,
        "schedule": schedules[username]
    }