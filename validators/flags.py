def validate_flags(p):
    errors=[]; warnings=[]; rows=[]
    es = p.get('enable_search')
    ec = p.get('enable_checkout')
    if es is None:
        warnings.append('enable_search recommended but not present; must be lower-case string true/false')
    if ec is None:
        warnings.append('enable_checkout recommended but not present; must be lower-case string true/false')
    if ec and (not es):
        errors.append('enable_checkout cannot be true when enable_search is not true')
    rows.append({'Field':'enable_search','Value':es})
    rows.append({'Field':'enable_checkout','Value':ec})
    return errors,warnings,rows
