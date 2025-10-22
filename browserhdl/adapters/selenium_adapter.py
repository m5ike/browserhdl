"""
Selenium Adapter - Supports Chrome, Firefox, Edge, and Safari
"""
import time
from typing import Dict, Any, Optional, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from ..core.browser_interface import IBrowserAdapter, BrowserEvent, ProxyConfig, PageStatistics


class SeleniumAdapter(IBrowserAdapter):
    """
    Selenium WebDriver adapter supporting multiple browsers
    """
    
    def __init__(self, browser: str = "chrome", headless: bool = True,
                 proxy: Optional[ProxyConfig] = None, **kwargs):
        """
        Initialize Selenium adapter
        
        Args:
            browser: Browser type - 'chrome', 'firefox', 'edge', or 'safari'
            headless: Run in headless mode
            proxy: Proxy configuration
        """
        super().__init__(headless, proxy)
        self.browser_type = browser.lower()
        if self.browser_type not in ['chrome', 'firefox', 'edge', 'safari']:
            raise ValueError(f"Unsupported browser: {browser}")
        
        self.driver = None
        self._start_time = 0
        
    def start(self) -> None:
        """Start Selenium WebDriver"""
        try:
            if self.browser_type == "chrome":
                options = webdriver.ChromeOptions()
                if self.headless:
                    options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                
                if self.proxy and self.proxy.enabled:
                    options.add_argument(f'--proxy-server={self.proxy.host}:{self.proxy.port}')
                
                self.driver = webdriver.Chrome(options=options)
                
            elif self.browser_type == "firefox":
                options = webdriver.FirefoxOptions()
                if self.headless:
                    options.add_argument('--headless')
                
                if self.proxy and self.proxy.enabled:
                    options.set_preference('network.proxy.type', 1)
                    options.set_preference('network.proxy.http', self.proxy.host)
                    options.set_preference('network.proxy.http_port', self.proxy.port)
                    options.set_preference('network.proxy.ssl', self.proxy.host)
                    options.set_preference('network.proxy.ssl_port', self.proxy.port)
                
                self.driver = webdriver.Firefox(options=options)
                
            elif self.browser_type == "edge":
                options = webdriver.EdgeOptions()
                if self.headless:
                    options.add_argument('--headless')
                
                if self.proxy and self.proxy.enabled:
                    options.add_argument(f'--proxy-server={self.proxy.host}:{self.proxy.port}')
                
                self.driver = webdriver.Edge(options=options)
                
            elif self.browser_type == "safari":
                # Safari doesn't support headless mode well
                self.driver = webdriver.Safari()
            
            self.trigger_event(BrowserEvent.ON_START)
            print(f"✓ Selenium {self.browser_type} started")
            
        except Exception as e:
            raise RuntimeError(f"Failed to start Selenium: {e}")
    
    def stop(self) -> None:
        """Stop Selenium WebDriver"""
        try:
            if self.driver:
                self.driver.quit()
            
            self.trigger_event(BrowserEvent.ON_STOP)
            print("✓ Selenium stopped")
        except Exception as e:
            print(f"Error stopping Selenium: {e}")
    
    def navigate(self, url: str) -> None:
        """Navigate to URL"""
        if not self.driver:
            raise RuntimeError("Browser not started")
        
        self._start_time = time.time()
        self.driver.get(url)
        self.trigger_event(BrowserEvent.ON_NAVIGATE, url)
        
        # Collect statistics
        self._last_statistics = self.get_statistics()
    
    def get_html(self) -> str:
        """Get current page HTML"""
        if not self.driver:
            raise RuntimeError("Browser not started")
        return self.driver.page_source
    
    def execute_script(self, script: str) -> Any:
        """Execute JavaScript"""
        if not self.driver:
            raise RuntimeError("Browser not started")
        return self.driver.execute_script(script)
    
    def find_element(self, selector: str) -> Optional[Any]:
        """Find element by CSS selector"""
        if not self.driver:
            raise RuntimeError("Browser not started")
        try:
            return self.driver.find_element(By.CSS_SELECTOR, selector)
        except NoSuchElementException:
            return None
    
    def find_elements(self, selector: str) -> List[Any]:
        """Find all elements by CSS selector"""
        if not self.driver:
            raise RuntimeError("Browser not started")
        return self.driver.find_elements(By.CSS_SELECTOR, selector)
    
    def click(self, selector: str) -> None:
        """Click element"""
        element = self.find_element(selector)
        if element:
            element.click()
        else:
            raise NoSuchElementException(f"Element not found: {selector}")
    
    def fill(self, selector: str, value: str) -> None:
        """Fill input field"""
        element = self.find_element(selector)
        if element:
            element.clear()
            element.send_keys(value)
        else:
            raise NoSuchElementException(f"Element not found: {selector}")
    
    def screenshot(self, path: str) -> None:
        """Take screenshot"""
        if not self.driver:
            raise RuntimeError("Browser not started")
        self.driver.save_screenshot(path)
    
    def get_cookies(self) -> List[Dict[str, Any]]:
        """Get all cookies"""
        if not self.driver:
            raise RuntimeError("Browser not started")
        return self.driver.get_cookies()
    
    def set_cookie(self, name: str, value: str, **kwargs) -> None:
        """Set a cookie"""
        if not self.driver:
            raise RuntimeError("Browser not started")
        
        cookie = {
            "name": name,
            "value": value
        }
        cookie.update(kwargs)
        self.driver.add_cookie(cookie)
    
    def delete_cookie(self, name: str) -> None:
        """Delete a cookie"""
        if not self.driver:
            raise RuntimeError("Browser not started")
        self.driver.delete_cookie(name)
    
    def get_local_storage(self) -> Dict[str, str]:
        """Get localStorage contents"""
        if not self.driver:
            raise RuntimeError("Browser not started")
        
        script = """
        let items = {};
        for (let i = 0; i < localStorage.length; i++) {
            let key = localStorage.key(i);
            items[key] = localStorage.getItem(key);
        }
        return items;
        """
        return self.execute_script(script)
    
    def set_local_storage(self, key: str, value: str) -> None:
        """Set localStorage item"""
        if not self.driver:
            raise RuntimeError("Browser not started")
        
        script = f"localStorage.setItem('{key}', '{value}')"
        self.execute_script(script)
    
    def wait_for_selector(self, selector: str, timeout: int = 30000) -> None:
        """Wait for element to appear"""
        if not self.driver:
            raise RuntimeError("Browser not started")
        
        try:
            WebDriverWait(self.driver, timeout / 1000).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
        except TimeoutException:
            raise TimeoutException(f"Element not found within {timeout}ms: {selector}")
    
    def get_statistics(self) -> PageStatistics:
        """Get page statistics"""
        if not self.driver:
            raise RuntimeError("Browser not started")
        
        # Collect various metrics
        html = self.get_html()
        load_time = time.time() - self._start_time if self._start_time else 0
        
        # Count elements using JavaScript
        stats_script = """
        return {
            numTags: document.querySelectorAll('*').length,
            numForms: document.forms.length,
            numLinks: document.links.length,
            numButtons: document.querySelectorAll('button').length,
            numInputs: document.querySelectorAll('input').length,
            numImages: document.images.length,
            title: document.title
        }
        """
        
        try:
            stats = self.execute_script(stats_script)
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
            url=self.driver.current_url,
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
            status_code=200,  # Selenium doesn't expose this directly
            content_type='text/html'
        )
