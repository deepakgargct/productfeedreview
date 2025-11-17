def validate_returns(p):
    errors=[]; warnings=[]; rows=[]
    rp = p.get('return_policy')
    if rp and not isinstance(rp, str):
        warnings.append('return_policy should be a URL string')
    rows.append({'Field':'return_policy','Value':rp})
    rwin = p.get('return_window')
    if rwin:
        try:
            if int(rwin) <= 0:
                errors.append('return_window must be a positive integer')
        except:
            errors.append('return_window must be an integer representing days')
    rows.append({'Field':'return_window','Value':rwin})
    return errors,warnings,rows
