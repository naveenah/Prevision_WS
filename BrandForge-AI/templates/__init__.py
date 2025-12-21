"""BrandForge AI - Templates Package"""

from .prompts import *
from .launch_plan_template import *

__all__ = [
    'FOUNDATION_PROMPT',
    'POSITIONING_PROMPT',
    'COMPETITOR_ANALYSIS_PROMPT',
    'BRAND_IDENTITY_PROMPT',
    'get_launch_plan_template',
    'get_available_brand_types'
]
