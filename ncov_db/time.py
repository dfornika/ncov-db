import datetime

def now():
    now = datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat()
    return now
