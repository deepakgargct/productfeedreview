def validate_performance(p):
    errors=[]; warnings=[]; rows=[]
    pop = p.get('popularity_score')
    if pop is not None:
        try:
            v = float(pop)
        except:
            warnings.append('popularity_score should be numeric')
    rows.append({'Field':'popularity_score','Value':pop})
    rr = p.get('return_rate')
    if rr is not None:
        try:
            v=float(str(rr).strip('%')) if isinstance(rr,str) else float(rr)
            if v < 0 or v > 100:
                warnings.append('return_rate should be 0-100%')
        except:
            warnings.append('return_rate should be numeric or percent string')
    rows.append({'Field':'return_rate','Value':rr})
    return errors,warnings,rows
