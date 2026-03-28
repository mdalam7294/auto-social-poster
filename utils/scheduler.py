import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

scheduler = BackgroundScheduler()
scheduler.start()

def schedule_upload(upload_func, video_path, metadata, user):
    # Define peak times for US/UK/Canada (example: 8 PM EST, 7 PM GMT)
    est = pytz.timezone('US/Eastern')
    now = datetime.now(est)
    target_times = [
        est.localize(now.replace(hour=20, minute=0, second=0)),  # 8 PM EST today
        est.localize(now.replace(hour=21, minute=0, second=0)),  # 9 PM EST
    ]
    # Find next future time
    next_time = None
    for t in target_times:
        if t > now:
            next_time = t
            break
    if next_time:
        scheduler.add_job(
            func=upload_func,
            args=[user, video_path, metadata],
            trigger='date',
            run_date=next_time
        )
        return f"Video scheduled for {next_time.strftime('%Y-%m-%d %H:%M %Z')}"
    else:
        # Upload immediately
        return upload_func(user, video_path, metadata)
