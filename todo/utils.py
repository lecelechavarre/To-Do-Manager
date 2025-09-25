def format_duration(seconds: int) -> str:
    # Returns H:MM:SS or M:SS if less than hour
    seconds = int(seconds)
    if seconds < 0:
        seconds = 0
    hrs = seconds // 3600
    mins = (seconds % 3600) // 60
    secs = seconds % 60
    if hrs > 0:
        return f"{hrs:d}:{mins:02d}:{secs:02d}"
    else:
        return f"{mins:d}:{secs:02d}"
