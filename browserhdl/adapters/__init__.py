"""Browser adapters module"""
from .playwright_adapter import PlaywrightAdapter
from .selenium_adapter import SeleniumAdapter

__all__ = ['PlaywrightAdapter', 'SeleniumAdapter']
