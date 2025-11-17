from utils.rules import is_iso8601_date
def validate_fulfillment(p):
    errors=[]; warnings=[]; rows=[]
    shipping = p.get('shipping')
    if shipping:
        entries = shipping if isinstance(shipping, list) else [s.strip() for s in str(shipping).split(',') if s.strip()]
        for s in entries:
            parts = s.split(':')
            if len(parts) < 4:
                warnings.append(f"shipping entry '{s}' expected 'country:region:service_class:price'")
    rows.append({'Field':'shipping','Value':shipping})
    de = p.get('delivery_estimate')
    if de and not is_iso8601_date(str(de)):
        warnings.append('delivery_estimate should be ISO 8601 date')
    rows.append({'Field':'delivery_estimate','Value':de})
    return errors,warnings,rows
