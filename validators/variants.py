def validate_variants(p):
    errors=[]; warnings=[]; rows=[]
    item_group = p.get('item_group_id')
    # detect variant fields
    variant_fields = any(p.get(f) for f in ('color','size','offer_id'))
    if variant_fields and not item_group:
        errors.append('item_group_id required when variants exist')
    rows.append({'Field':'item_group_id','Value':item_group})
    # sizes/colors recommendations
    if p.get('color') and len(str(p.get('color'))) > 40:
        warnings.append('color exceeds 40 chars')
    rows.append({'Field':'color','Value':p.get('color')})
    if p.get('size') and len(str(p.get('size'))) > 20:
        warnings.append('size exceeds 20 chars')
    rows.append({'Field':'size','Value':p.get('size')})
    return errors,warnings,rows
