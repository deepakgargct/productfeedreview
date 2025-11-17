from .flags import validate_flags
from .basic import validate_basic
from .item_info import validate_item_info
from .media import validate_media
from .pricing import validate_pricing
from .availability import validate_availability
from .variants import validate_variants
from .fulfillment import validate_fulfillment
from .merchant import validate_merchant
from .returns import validate_returns
from .performance import validate_performance
from .compliance import validate_compliance
from .reviews import validate_reviews
from .related import validate_related
from .geo import validate_geo

def run_all_validations(p):
    errors=[]; warnings=[]; infos=[]; fields=[]
    for fn in [validate_flags, validate_basic, validate_item_info, validate_media,
               validate_pricing, validate_availability, validate_variants,
               validate_fulfillment, validate_merchant, validate_returns,
               validate_performance, validate_compliance, validate_reviews,
               validate_related, validate_geo]:
        e,w,f = fn(p)
        errors+=e; warnings+=w; fields+=f
    return {'errors':errors,'warnings':warnings,'infos':infos,'fields':fields}
