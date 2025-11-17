from urllib.parse import urlparse
from datetime import datetime, timezone

def is_url(s):
    if not s:
        return False
    try:
        p=urlparse(str(s))
        return p.scheme in ('http','https') and bool(p.netloc)
    except:
        return False

def is_iso8601_date(s):
    if not s:
        return False
    try:
        datetime.fromisoformat(str(s))
        return True
    except:
        try:
            datetime.strptime(str(s), '%Y-%m-%d')
            return True
        except:
            return False

def parse_iso_date(s):
    try:
        return datetime.fromisoformat(s)
    except:
        try:
            return datetime.strptime(s, '%Y-%m-%d')
        except:
            return None
