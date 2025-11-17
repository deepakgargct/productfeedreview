import json
import xml.etree.ElementTree as ET
from typing import List, Dict, Any

def extract_products_from_json(obj):
    if isinstance(obj, list) and all(isinstance(i, dict) for i in obj):
        return obj
    if isinstance(obj, dict):
        for key in ('products','items','feed','entries','data'):
            if key in obj and isinstance(obj[key], list):
                return obj[key]
    # BFS search for first list-of-dicts
    queue=[obj]
    seen=set()
    while queue:
        cur=queue.pop(0)
        if id(cur) in seen:
            continue
        seen.add(id(cur))
        if isinstance(cur, list):
            if cur and all(isinstance(i, dict) for i in cur):
                return cur
            for it in cur:
                queue.append(it)
        elif isinstance(cur, dict):
            for v in cur.values():
                queue.append(v)
    if isinstance(obj, dict):
        return [obj]
    return []

def load_feed(uploaded) -> List[Dict[str,Any]]:
    raw = uploaded.getvalue().decode('utf-8')
    name = uploaded.name.lower()
    if name.endswith('.json'):
        parsed = json.loads(raw)
        return extract_products_from_json(parsed)
    elif name.endswith('.xml'):
        root = ET.fromstring(raw)
        candidates = root.findall('.//item') or root.findall('.//product') or root.findall('.//entry') or list(root)
        out=[]
        for el in candidates:
            obj={}
            for c in el:
                tag = c.tag.split('}')[-1]
                # if nested, convert children to dict
                if list(c):
                    inner={}
                    for cc in c:
                        inner[cc.tag.split('}')[-1]] = cc.text or ''
                    obj[tag]=inner
                else:
                    obj[tag]=c.text or ''
            out.append(obj)
        return out
    else:
        raise ValueError('Unsupported file type')
