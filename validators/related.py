def validate_related(p):
    errors=[]; warnings=[]; rows=[]
    rel = p.get('related_product_id')
    if rel and isinstance(rel,str) and ',' in rel:
        # ok comma-separated
        pass
    rows.append({'Field':'related_product_id','Value':rel})
    rt = p.get('relationship_type')
    if rt and rt not in ('part_of_set','required_part','often_bought_with','substitute','different_brand','accessory'):
        warnings.append('relationship_type value unexpected')
    rows.append({'Field':'relationship_type','Value':rt})
    return errors,warnings,rows
