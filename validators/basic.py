from utils.rules import is_url, is_iso8601_date
import re

def validate_basic(p):
    errors=[]; warnings=[]; rows=[]
    # id
    idv = p.get('id')
    if idv in (None,''):
        errors.append('Missing required field: id')
    else:
        if len(str(idv))>100:
            warnings.append('id exceeds 100 chars')
    rows.append({'Field':'id','Value':idv})
    # gtin
    gtin = p.get('gtin')
    if not gtin:
        warnings.append('gtin recommended')
    else:
        if not re.match(r'^[0-9]{8,14}$', str(gtin)):
            warnings.append('gtin should be 8-14 digits')
    rows.append({'Field':'gtin','Value':gtin})
    # mpn
    mpn = p.get('mpn')
    if not gtin and not mpn:
        errors.append("Either 'gtin' or 'mpn' must be present")
    if mpn and len(str(mpn))>70:
        warnings.append('mpn exceeds 70 chars')
    rows.append({'Field':'mpn','Value':mpn})
    # title
    title = p.get('title')
    if not title:
        errors.append('Missing required field: title')
    elif len(str(title))>150:
        warnings.append('title exceeds 150 chars')
    rows.append({'Field':'title','Value':title})
    # description
    desc = p.get('description')
    if not desc:
        errors.append('Missing required field: description')
    elif len(str(desc))>5000:
        errors.append('description exceeds 5000 chars')
    rows.append({'Field':'description','Value':desc})
    # link
    link = p.get('link')
    if not link:
        errors.append('Missing required field: link')
    else:
        if not is_url(link):
            errors.append('link must be valid http(s) URL')
    rows.append({'Field':'link','Value':link})
    return errors,warnings,rows
