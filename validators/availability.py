from utils.rules import is_iso8601_date
def validate_availability(p):
    errors=[]; warnings=[]; rows=[]
    availability = p.get('availability')
    if not availability:
        errors.append('Missing required field: availability')
    else:
        if availability not in ('in_stock','out_of_stock','preorder'):
            errors.append("availability must be one of in_stock, out_of_stock, preorder")
    rows.append({'Field':'availability','Value':availability})
    if availability == 'preorder':
        ad = p.get('availability_date')
        if not ad:
            errors.append('availability_date required for preorder')
        else:
            if not is_iso8601_date(str(ad)):
                errors.append('availability_date must be ISO 8601')
    inv = p.get('inventory_quantity')
    if inv is None or not str(inv).isdigit():
        errors.append('inventory_quantity must be a non-negative integer')
    rows.append({'Field':'inventory_quantity','Value':inv})
    exp = p.get('expiration_date')
    if exp and not is_iso8601_date(str(exp)):
        warnings.append('expiration_date should be ISO 8601')
    rows.append({'Field':'expiration_date','Value':exp})
    return errors,warnings,rows
