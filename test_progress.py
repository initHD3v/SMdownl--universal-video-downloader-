import yt_dlp

def progress_hook(d):
    print(d['status'])
    if d['status'] == 'downloading':
        print(f"Downloaded: {d.get('downloaded_bytes')}, Total: {d.get('total_bytes')} / {d.get('total_bytes_estimate')}")
        print(f"Percent: {d.get('_percent_str')}")

ydl_opts = {
    'progress_hooks': [progress_hook],
    'quiet': True,
    'format': 'worst' # Smallest format
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download(['https://youtube.com/shorts/e-8X-jkLQe0'])
