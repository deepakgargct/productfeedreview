import re
from utils.rules import is_iso8601_date
def parse_price(value):
    if value is None:
        return None,None
    s=str(value).strip()
    m = re.match(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*([A-Z]{3})?\s*$", s)
    if m:
        return float(m.group(1)), m.group(2)
    # try json-like
    try:
        import json
        parsed = json.loads(s)
        if isinstance(parsed, dict) and 'value' in parsed:
            return float(parsed['value']), parsed.get('currency')
    except:
        pass
    parts = s.split()
    if not parts:
        return None,None
    try:
        return float(parts[0]), (parts[1] if len(parts)>1 else None)
    except:
        return None,None

def validate_pricing(p):
    errors=[]; warnings=[]; rows=[]
    price = p.get('price')
    pv, pc = parse_price(price)
    if pv is None:
        errors.append('Missing or invalid required field: price')
    else:
        if pv < 0:
            errors.append('price must be non-negative')
        if not pc:
            errors.append('price must include ISO 4217 currency code per spec')
    rows.append({'Field':'price','Value':price})
    sale = p.get('sale_price')
    if sale:
        sv, sc = parse_price(sale)
        if sv is None:
            errors.append('sale_price present but not parseable')
        else:
            if pv is not None and sv > pv:
                errors.append('sale_price must be <= price')
    rows.append({'Field':'sale_price','Value':sale})
    sale_eff = p.get('sale_price_effective_date')
    if sale and sale_eff:
        parts = re.split(r"\s*/\s*", str(sale_eff))
        if len(parts)!=2:
            errors.append('sale_price_effective_date must be range start/end')
        else:
            if not is_iso8601_date(parts[0]) or not is_iso8601_date(parts[1]):
                errors.append('sale_price_effective_date dates must be ISO 8601')
    rows.append({'Field':'sale_price_effective_date','Value':sale_eff})
    # unit_pricing_measure / base_measure light check
    upm = p.get('unit_pricing_measure')
    if upm and not isinstance(upm, str):
        warnings.append('unit_pricing_measure should be string like "16 oz / 1 oz"')
    rows.append({'Field':'unit_pricing_measure','Value':upm})
    return errors,warnings,rows
