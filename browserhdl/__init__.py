"""BrowserHDL - Headless Browser Module"""
__version__ = "1.0.0"

from .core import IBrowserAdapter, BrowserEvent, ProxyConfig, PageStatistics
from .adapters import PlaywrightAdapter, SeleniumAdapter
from .profiles import ProfileManager, ProfileMetadata
from .cli import BrowserCLI

__all__ = [
    "IBrowserAdapter",
    "BrowserEvent",
    "ProxyConfig",
    "PageStatistics",
    "PlaywrightAdapter",
    "SeleniumAdapter",
    "ProfileManager",
    "ProfileMetadata",
    "BrowserCLI",
]
