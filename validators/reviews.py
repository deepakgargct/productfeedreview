def validate_reviews(p):
    errors=[]; warnings=[]; rows=[]
    prc = p.get('product_review_count')
    if prc is not None:
        try:
            if int(prc) < 0:
                warnings.append('product_review_count must be non-negative')
        except:
            warnings.append('product_review_count should be integer')
    rows.append({'Field':'product_review_count','Value':prc})
    prr = p.get('product_review_rating')
    if prr is not None:
        try:
            v=float(prr)
            if v < 0 or v > 5:
                warnings.append('product_review_rating should be between 0 and 5')
        except:
            warnings.append('product_review_rating should be numeric')
    rows.append({'Field':'product_review_rating','Value':prr})
    # q_and_a and raw_review_data lightly added
    rows.append({'Field':'q_and_a','Value':p.get('q_and_a')})
    rows.append({'Field':'raw_review_data','Value':p.get('raw_review_data')})
    return errors,warnings,rows
