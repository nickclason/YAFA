import datetime

def get_start_epoch(days: int) -> int:
    """Return the Unix timestamp for N days ago."""
    return int((datetime.datetime.now() - datetime.timedelta(days=days)).timestamp())
