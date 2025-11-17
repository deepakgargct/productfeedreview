from utils.rules import is_url
import re
def validate_item_info(p):
    errors=[]; warnings=[]; rows=[]
    # condition
    condition = p.get('condition')
    if condition and condition not in ('new','refurbished','used'):
        warnings.append('condition should be new/refurbished/used')
    rows.append({'Field':'condition','Value':condition})
    # product_category
    cat = p.get('product_category') or p.get('category') or p.get('google_product_category')
    if not cat:
        warnings.append('product_category recommended')
    rows.append({'Field':'product_category','Value':cat})
    # brand
    brand = p.get('brand')
    if not brand:
        warnings.append('brand recommended')
    elif len(str(brand))>70:
        warnings.append('brand exceeds 70 chars')
    rows.append({'Field':'brand','Value':brand})
    # material
    mat = p.get('material')
    if not mat:
        warnings.append('material recommended')
    rows.append({'Field':'material','Value':mat})
    # dimensions / weight
    weight = p.get('weight') or p.get('shipping_weight')
    if not weight:
        warnings.append('weight recommended')
    rows.append({'Field':'weight','Value':weight})
    # age_group
    age = p.get('age_group')
    if age and age not in ('newborn','infant','toddler','kids','adult'):
        warnings.append('age_group should be one of newborn, infant, toddler, kids, adult')
    rows.append({'Field':'age_group','Value':age})
    return errors,warnings,rows
