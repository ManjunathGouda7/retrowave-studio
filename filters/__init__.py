"""Auto-import all filter modules so they register themselves into FILTER_REGISTRY."""
from . import vintage_80s
from . import vintage_90s
from . import retro_general
from . import glitch
from . import artistic
from . import cyberpunk
from . import horror
from . import dreamy
from .base import FILTER_REGISTRY, get_filters_by_category