import re
from utils.rules import is_iso8601_date
def validate_geo(p):
    errors=[]; warnings=[]; rows=[]
    gp = p.get('geo_price')
    if gp:
        # very light parse - ensure currency present somewhere
        if not any(c.isalpha() for c in str(gp)):
            warnings.append('geo_price expected to include currency code or region note')
    rows.append({'Field':'geo_price','Value':gp})
    ga = p.get('geo_availability')
    if ga:
        # should contain region codes; light check
        if not isinstance(ga,str):
            warnings.append('geo_availability should be string like "US:in_stock"')
    rows.append({'Field':'geo_availability','Value':ga})
    return errors,warnings,rows
