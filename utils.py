import re

def parse_video_url(url):
    """
    Detects platform and converts video URL into an embed link or direct link.
    Returns a dict: {'embed_url': ..., 'type': 'iframe' or 'video', 'thumbnail': ...}
    """
    url = url.strip()
    
    # YouTube URL Parser
    youtube_regex = (
        r'(?:https?://)?(?:www\.)?(?:youtube\.com/(?:[^/\n\s]+/\S+/|(?:v|e(?:mbed)?|watch)\?[^#\n\s]*&?v=|(?:embed|v)/)|youtu\.be/)([a-zA-Z0-9_-]{11})'
    )
    match = re.search(youtube_regex, url)
    if match:
        video_id = match.group(1)
        return {
            'embed_url': f'https://www.youtube.com/embed/{video_id}',
            'type': 'iframe',
            'thumbnail': f'https://img.youtube.com/vi/{video_id}/hqdefault.jpg'
        }

    # Dailymotion URL Parser
    dailymotion_regex = r'(?:https?://)?(?:www\.)?(?:dailymotion\.com/video/|dai\.ly/)([a-zA-Z0-9]+)'
    match = re.search(dailymotion_regex, url)
    if match:
        video_id = match.group(1)
        return {
            'embed_url': f'https://www.dailymotion.com/embed/video/{video_id}',
            'type': 'iframe',
            'thumbnail': f'https://www.dailymotion.com/thumbnail/video/{video_id}'
        }

    # Vimeo URL Parser
    vimeo_regex = r'(?:https?://)?(?:www\.)?vimeo\.com/(?:channels/(?:\w+/)?|groups/(?:[^/:]+)/videos/|album/(?:\d+)/video/|video/|)(\d+)'
    match = re.search(vimeo_regex, url)
    if match:
        video_id = match.group(1)
        return {
            'embed_url': f'https://player.vimeo.com/video/{video_id}',
            'type': 'iframe',
            'thumbnail': 'https://via.placeholder.com/480x360.png?text=Vimeo+Video'
        }

    # Direct MP4 or Generic Embed
    if url.endswith('.mp4') or 'embed' in url:
        return {
            'embed_url': url,
            'type': 'iframe' if 'embed' in url else 'video',
            'thumbnail': 'https://via.placeholder.com/480x360.png?text=Video+Thumbnail'
        }

    # Fallback default
    return {
        'embed_url': url,
        'type': 'iframe',
        'thumbnail': 'https://via.placeholder.com/480x360.png?text=Video'
    }