"""Auto-import all filter modules so they register themselves."""
from . import vintage_80s
from . import vintage_90s
from . import retro_general
from . import glitch
from . import artistic
from .base import FILTER_REGISTRY, get_filters_by_category