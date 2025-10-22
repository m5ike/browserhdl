"""
Browser Interface - Abstract base class for all headless browser implementations
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable
from enum import Enum
from dataclasses import dataclass
import json


class BrowserEvent(Enum):
    """Browser events that can be triggered"""
    ON_LOAD = "onload"
    ON_START = "onstart"
    ON_STOP = "onstop"
    ON_NAVIGATE = "onnavigate"
    ON_UNLOAD = "onunload"
    ON_ERROR = "onerror"
    ON_CONSOLE = "onconsole"
    ON_DIALOG = "ondialog"
    ON_DOWNLOAD = "ondownload"
    ON_REQUEST = "onrequest"
    ON_RESPONSE = "onresponse"


@dataclass
class ProxyConfig:
    """Proxy configuration for browser"""
    enabled: bool = False
    host: str = ""
    port: int = 0
    username: Optional[str] = None
    password: Optional[str] = None
    cache_enabled: bool = False
    filters: List[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "password": self.password,
            "cache_enabled": self.cache_enabled,
            "filters": self.filters or []
        }


@dataclass
class PageStatistics:
    """Statistics about loaded page"""
    url: str
    load_time: float
    size_bytes: int
    num_tags: int
    num_forms: int
    num_links: int
    num_buttons: int
    num_inputs: int
    num_images: int
    cookies_size: int
    page_title: str
    status_code: int
    content_type: str
    
    def __str__(self) -> str:
        return f"""
Page Statistics:
═══════════════════════════════════════
URL: {self.url}
Title: {self.page_title}
Status: {self.status_code}
Content-Type: {self.content_type}
Load Time: {self.load_time:.2f}s
Size: {self.size_bytes / 1024:.2f} KB
Tags: {self.num_tags}
Forms: {self.num_forms}
Links: {self.num_links}
Buttons: {self.num_buttons}
Inputs: {self.num_inputs}
Images: {self.num_images}
Cookies Size: {self.cookies_size} bytes
═══════════════════════════════════════
"""


class IBrowserAdapter(ABC):
    """
    Interface that all headless browser adapters must implement.
    Provides a unified API for different headless browser engines.
    """
    
    def __init__(self, headless: bool = True, proxy: Optional[ProxyConfig] = None):
        """
        Initialize browser adapter
        
        Args:
            headless: Run browser in headless mode
            proxy: Proxy configuration
        """
        self.headless = headless
        self.proxy = proxy
        self.event_handlers: Dict[BrowserEvent, List[Callable]] = {}
        self._last_statistics: Optional[PageStatistics] = None
        
    @abstractmethod
    def start(self) -> None:
        """Start the browser instance"""
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """Stop the browser instance"""
        pass
    
    @abstractmethod
    def navigate(self, url: str) -> None:
        """Navigate to URL"""
        pass
    
    @abstractmethod
    def get_html(self) -> str:
        """Get current page HTML"""
        pass
    
    @abstractmethod
    def execute_script(self, script: str) -> Any:
        """Execute JavaScript in page context"""
        pass
    
    @abstractmethod
    def find_element(self, selector: str) -> Optional[Any]:
        """Find element by CSS selector"""
        pass
    
    @abstractmethod
    def find_elements(self, selector: str) -> List[Any]:
        """Find all elements by CSS selector"""
        pass
    
    @abstractmethod
    def click(self, selector: str) -> None:
        """Click element by selector"""
        pass
    
    @abstractmethod
    def fill(self, selector: str, value: str) -> None:
        """Fill input field"""
        pass
    
    @abstractmethod
    def screenshot(self, path: str) -> None:
        """Take screenshot"""
        pass
    
    @abstractmethod
    def get_cookies(self) -> List[Dict[str, Any]]:
        """Get all cookies"""
        pass
    
    @abstractmethod
    def set_cookie(self, name: str, value: str, **kwargs) -> None:
        """Set a cookie"""
        pass
    
    @abstractmethod
    def delete_cookie(self, name: str) -> None:
        """Delete a cookie"""
        pass
    
    @abstractmethod
    def get_local_storage(self) -> Dict[str, str]:
        """Get localStorage contents"""
        pass
    
    @abstractmethod
    def set_local_storage(self, key: str, value: str) -> None:
        """Set localStorage item"""
        pass
    
    @abstractmethod
    def wait_for_selector(self, selector: str, timeout: int = 30000) -> None:
        """Wait for element to appear"""
        pass
    
    @abstractmethod
    def get_statistics(self) -> PageStatistics:
        """Get page statistics"""
        pass
    
    def on(self, event: BrowserEvent, handler: Callable) -> None:
        """Register event handler"""
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.event_handlers[event].append(handler)
    
    def trigger_event(self, event: BrowserEvent, *args, **kwargs) -> None:
        """Trigger event handlers"""
        if event in self.event_handlers:
            for handler in self.event_handlers[event]:
                try:
                    handler(*args, **kwargs)
                except Exception as e:
                    print(f"Error in event handler for {event.value}: {e}")
    
    def load_profile(self, profile_data: Dict[str, Any]) -> None:
        """
        Load user profile (cookies, localStorage, etc.)
        
        Args:
            profile_data: Dictionary containing profile data
        """
        # Set cookies
        if "cookies" in profile_data:
            for cookie in profile_data["cookies"]:
                try:
                    self.set_cookie(**cookie)
                except Exception as e:
                    print(f"Failed to set cookie: {e}")
        
        # Set localStorage
        if "localStorage" in profile_data:
            for key, value in profile_data["localStorage"].items():
                try:
                    self.set_local_storage(key, value)
                except Exception as e:
                    print(f"Failed to set localStorage: {e}")
    
    def get_last_statistics(self) -> Optional[PageStatistics]:
        """Get last collected statistics"""
        return self._last_statistics
