from utils.rules import is_url
def validate_media(p):
    errors=[]; warnings=[]; rows=[]
    img = p.get('image_link')
    if not img:
        errors.append('Missing required field: image_link')
    else:
        if not is_url(img):
            errors.append('image_link must be a valid URL')
    rows.append({'Field':'image_link','Value':img})
    add = p.get('additional_image_link')
    if add:
        # accept comma-separated
        if isinstance(add,str) and ',' in add:
            arr=[s.strip() for s in add.split(',') if s.strip()]
        elif isinstance(add,list):
            arr=add
        else:
            arr=[add]
        for u in arr:
            if not is_url(u):
                warnings.append('additional_image_link contains invalid URL')
                break
    rows.append({'Field':'additional_image_link','Value':add})
    video = p.get('video_link')
    if video and not is_url(video):
        warnings.append('video_link not valid URL')
    rows.append({'Field':'video_link','Value':video})
    model3 = p.get('model_3d_link')
    if model3 and not is_url(model3):
        warnings.append('model_3d_link not valid URL')
    rows.append({'Field':'model_3d_link','Value':model3})
    return errors,warnings,rows
