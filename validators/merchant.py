from utils.rules import is_url
def validate_merchant(p):
    errors=[]; warnings=[]; rows=[]
    seller = p.get('seller_name')
    if not seller:
        warnings.append('seller_name recommended')
    rows.append({'Field':'seller_name','Value':seller})
    seller_url = p.get('seller_url')
    if seller_url and not is_url(seller_url):
        warnings.append('seller_url should be a valid URL')
    rows.append({'Field':'seller_url','Value':seller_url})
    # seller privacy/tos required if enable_checkout true will be handled in flags
    return errors,warnings,rows
