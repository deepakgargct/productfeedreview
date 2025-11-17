from utils.rules import is_url
def validate_compliance(p):
    errors=[]; warnings=[]; rows=[]
    warning_text = p.get('warning')
    warning_url = p.get('warning_url')
    if warning_url and not is_url(warning_url):
        warnings.append('warning_url should be a valid URL')
    rows.append({'Field':'warning','Value':warning_text})
    rows.append({'Field':'warning_url','Value':warning_url})
    age = p.get('age_restriction')
    if age:
        try:
            if int(age) <= 0:
                warnings.append('age_restriction should be positive integer')
        except:
            warnings.append('age_restriction should be integer')
    rows.append({'Field':'age_restriction','Value':age})
    return errors,warnings,rows
