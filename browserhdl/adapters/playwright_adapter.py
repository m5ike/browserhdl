"""
Playwright Adapter - Supports Chromium, Firefox, and WebKit
"""
import time
from typing import Dict, Any, Optional, List
from playwright.sync_api import sync_playwright, Browser, Page, Playwright

from ..core.browser_interface import IBrowserAdapter, BrowserEvent, ProxyConfig, PageStatistics


class PlaywrightAdapter(IBrowserAdapter):
    """
    Playwright adapter supporting multiple browser engines
    """
    
    def __init__(self, engine: str = "chromium", headless: bool = True, 
                 proxy: Optional[ProxyConfig] = None, **kwargs):
        """
        Initialize Playwright adapter
        
        Args:
            engine: Browser engine - 'chromium', 'firefox', or 'webkit'
            headless: Run in headless mode
            proxy: Proxy configuration
        """
        super().__init__(headless, proxy)
        self.engine = engine.lower()
        if self.engine not in ['chromium', 'firefox', 'webkit']:
            raise ValueError(f"Unsupported engine: {engine}")
        
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.context = None
        self._start_time = 0
        
    def start(self) -> None:
        """Start Playwright browser"""
        try:
            self.playwright = sync_playwright().start()
            
            # Browser launch options
            launch_options = {
                "headless": self.headless
            }
            
            # Add proxy if configured
            if self.proxy and self.proxy.enabled:
                launch_options["proxy"] = {
                    "server": f"{self.proxy.host}:{self.proxy.port}"
                }
                if self.proxy.username and self.proxy.password:
                    launch_options["proxy"]["username"] = self.proxy.username
                    launch_options["proxy"]["password"] = self.proxy.password
            
            # Launch browser based on engine
            if self.engine == "chromium":
                self.browser = self.playwright.chromium.launch(**launch_options)
            elif self.engine == "firefox":
                self.browser = self.playwright.firefox.launch(**launch_options)
            elif self.engine == "webkit":
                self.browser = self.playwright.webkit.launch(**launch_options)
            
            # Create context and page
            self.context = self.browser.new_context()
            self.page = self.context.new_page()
            
            # Register event listeners
            self.page.on("load", lambda: self.trigger_event(BrowserEvent.ON_LOAD))
            self.page.on("console", lambda msg: self.trigger_event(
                BrowserEvent.ON_CONSOLE, msg.text))
            self.page.on("pageerror", lambda err: self.trigger_event(
                BrowserEvent.ON_ERROR, str(err)))
            
            self.trigger_event(BrowserEvent.ON_START)
            print(f"✓ Playwright {self.engine} started")
            
        except Exception as e:
            raise RuntimeError(f"Failed to start Playwright: {e}")
    
    def stop(self) -> None:
        """Stop Playwright browser"""
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            
            self.trigger_event(BrowserEvent.ON_STOP)
            print("✓ Playwright stopped")
        except Exception as e:
            print(f"Error stopping Playwright: {e}")
    
    def navigate(self, url: str) -> None:
        """Navigate to URL"""
        if not self.page:
            raise RuntimeError("Browser not started")
        
        self._start_time = time.time()
        self.page.goto(url, wait_until="networkidle", timeout=60000)
        self.trigger_event(BrowserEvent.ON_NAVIGATE, url)
        
        # Collect statistics
        self._last_statistics = self.get_statistics()
    
    def get_html(self) -> str:
        """Get current page HTML"""
        if not self.page:
            raise RuntimeError("Browser not started")
        return self.page.content()
    
    def execute_script(self, script: str) -> Any:
        """Execute JavaScript"""
        if not self.page:
            raise RuntimeError("Browser not started")
        return self.page.evaluate(script)
    
    def find_element(self, selector: str) -> Optional[Any]:
        """Find element by CSS selector"""
        if not self.page:
            raise RuntimeError("Browser not started")
        try:
            return self.page.query_selector(selector)
        except:
            return None
    
    def find_elements(self, selector: str) -> List[Any]:
        """Find all elements by CSS selector"""
        if not self.page:
            raise RuntimeError("Browser not started")
        return self.page.query_selector_all(selector)
    
    def click(self, selector: str) -> None:
        """Click element"""
        if not self.page:
            raise RuntimeError("Browser not started")
        self.page.click(selector)
    
    def fill(self, selector: str, value: str) -> None:
        """Fill input field"""
        if not self.page:
            raise RuntimeError("Browser not started")
        self.page.fill(selector, value)
    
    def screenshot(self, path: str) -> None:
        """Take screenshot"""
        if not self.page:
            raise RuntimeError("Browser not started")
        self.page.screenshot(path=path, full_page=True)
    
    def get_cookies(self) -> List[Dict[str, Any]]:
        """Get all cookies"""
        if not self.context:
            raise RuntimeError("Browser not started")
        return self.context.cookies()
    
    def set_cookie(self, name: str, value: str, **kwargs) -> None:
        """Set a cookie"""
        if not self.context:
            raise RuntimeError("Browser not started")
        
        cookie = {
            "name": name,
            "value": value,
            "url": self.page.url if self.page else "https://example.com"
        }
        cookie.update(kwargs)
        self.context.add_cookies([cookie])
    
    def delete_cookie(self, name: str) -> None:
        """Delete a cookie"""
        if not self.context:
            raise RuntimeError("Browser not started")
        self.context.clear_cookies()
    
    def get_local_storage(self) -> Dict[str, str]:
        """Get localStorage contents"""
        if not self.page:
            raise RuntimeError("Browser not started")
        
        script = """
        () => {
            let items = {};
            for (let i = 0; i < localStorage.length; i++) {
                let key = localStorage.key(i);
                items[key] = localStorage.getItem(key);
            }
            return items;
        }
        """
        return self.page.evaluate(script)
    
    def set_local_storage(self, key: str, value: str) -> None:
        """Set localStorage item"""
        if not self.page:
            raise RuntimeError("Browser not started")
        
        script = f"localStorage.setItem('{key}', '{value}')"
        self.page.evaluate(script)
    
    def wait_for_selector(self, selector: str, timeout: int = 30000) -> None:
        """Wait for element to appear"""
        if not self.page:
            raise RuntimeError("Browser not started")
        self.page.wait_for_selector(selector, timeout=timeout)
    
    def get_statistics(self) -> PageStatistics:
        """Get page statistics"""
        if not self.page:
            raise RuntimeError("Browser not started")
        
        # Collect various metrics
        html = self.get_html()
        load_time = time.time() - self._start_time if self._start_time else 0
        
        # Count elements
        stats_script = """
        () => {
            return {
                numTags: document.querySelectorAll('*').length,
                numForms: document.forms.length,
                numLinks: document.links.length,
                numButtons: document.querySelectorAll('button').length,
                numInputs: document.querySelectorAll('input').length,
                numImages: document.images.length,
                title: document.title
            }
        }
        """
        
        try:
            stats = self.page.evaluate(stats_script)
        except:
            stats = {
                'numTags': 0,
                'numForms': 0,
                'numLinks': 0,
                'numButtons': 0,
                'numInputs': 0,
                'numImages': 0,
                'title': ''
            }
        
        # Get cookies size
        cookies = self.get_cookies()
        cookies_size = sum(len(str(c)) for c in cookies)
        
        return PageStatistics(
            url=self.page.url,
            load_time=load_time,
            size_bytes=len(html.encode('utf-8')),
            num_tags=stats.get('numTags', 0),
            num_forms=stats.get('numForms', 0),
            num_links=stats.get('numLinks', 0),
            num_buttons=stats.get('numButtons', 0),
            num_inputs=stats.get('numInputs', 0),
            num_images=stats.get('numImages', 0),
            cookies_size=cookies_size,
            page_title=stats.get('title', ''),
            status_code=200,  # Playwright doesn't expose this easily
            content_type='text/html'
        )
