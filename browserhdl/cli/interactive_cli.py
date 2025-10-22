"""
Interactive CLI - Command Line Interface for headless browser control
Features multi-line script input, statistics display, and interactive control
"""
import sys
import os
import re
import time
from typing import Optional, Dict, Any, List
from pathlib import Path

from ..core.browser_interface import IBrowserAdapter, BrowserEvent
from ..adapters.playwright_adapter import PlaywrightAdapter
from ..adapters.selenium_adapter import SeleniumAdapter
from ..profiles.profile_manager import ProfileManager


class BrowserCLI:
    """
    Interactive CLI for browser control
    """
    
    ADAPTERS = {
        "playwright-chromium": (PlaywrightAdapter, {"engine": "chromium"}),
        "playwright-firefox": (PlaywrightAdapter, {"engine": "firefox"}),
        "playwright-webkit": (PlaywrightAdapter, {"engine": "webkit"}),
        "selenium-chrome": (SeleniumAdapter, {"browser": "chrome"}),
        "selenium-firefox": (SeleniumAdapter, {"browser": "firefox"}),
        "selenium-edge": (SeleniumAdapter, {"browser": "edge"}),
        "selenium-safari": (SeleniumAdapter, {"browser": "safari"}),
    }
    
    def __init__(self, adapter_name: str = "playwright-chromium", initial_url: Optional[str] = None):
        """Initialize CLI"""
        self.browser: Optional[IBrowserAdapter] = None
        self.profile_manager = ProfileManager()
        self.current_profile = None
        self.script_buffer: List[str] = []
        self.running = True
        self.adapter_name = adapter_name
        self.initial_url = initial_url
        
        # Register event handlers
        self.setup_event_handlers()
    
    def setup_event_handlers(self) -> None:
        """Setup default event handlers"""
        pass  # Can be extended
    
    def start_browser(self) -> None:
        """Start the browser"""
        if self.adapter_name not in self.ADAPTERS:
            print(f"❌ Unknown adapter: {self.adapter_name}")
            print(f"Available adapters: {', '.join(self.ADAPTERS.keys())}")
            sys.exit(1)
        
        adapter_class, options = self.ADAPTERS[self.adapter_name]
        self.browser = adapter_class(**options)
        
        # Register events
        self.browser.on(BrowserEvent.ON_LOAD, lambda: print("📄 Page loaded"))
        self.browser.on(BrowserEvent.ON_ERROR, lambda err: print(f"❌ Error: {err}"))
        self.browser.on(BrowserEvent.ON_CONSOLE, lambda msg: print(f"🖥️  Console: {msg}"))
        
        self.browser.start()
        
        # Navigate to initial URL if provided
        if self.initial_url:
            print(f"🌐 Navigating to {self.initial_url}...")
            self.browser.navigate(self.initial_url)
            self.show_statistics()
    
    def show_help(self) -> None:
        """Show help message"""
        help_text = """
╔══════════════════════════════════════════════════════════════╗
║            BrowserHDL - Interactive CLI Help                 ║
╠══════════════════════════════════════════════════════════════╣
║ Navigation & Content:                                         ║
║   navigate(url)          - Navigate to URL                   ║
║   html()                 - Get page HTML                     ║
║   refresh()              - Refresh current page              ║
║   back()                 - Go back                           ║
║   forward()              - Go forward                        ║
║                                                              ║
║ Element Interaction:                                         ║
║   find(selector)         - Find element by CSS selector      ║
║   click(selector)        - Click element                     ║
║   fill(selector, value)  - Fill input field                  ║
║   wait(selector)         - Wait for element                  ║
║                                                              ║
║ JavaScript Execution:                                        ║
║   execute(script)        - Execute JavaScript                ║
║                                                              ║
║ Cookies & Storage:                                           ║
║   get_cookies()          - Get all cookies                   ║
║   set_cookie(name, val)  - Set cookie                        ║
║   get_storage()          - Get localStorage                  ║
║   set_storage(key, val)  - Set localStorage item             ║
║                                                              ║
║ Profiles:                                                    ║
║   load_profile(name)     - Load user profile                 ║
║   save_profile(name)     - Save current profile              ║
║   list_profiles()        - List all profiles                 ║
║                                                              ║
║ Utility:                                                     ║
║   screenshot(path)       - Take screenshot                   ║
║   sleep(seconds)         - Sleep for N seconds               ║
║   stats                  - Show page statistics              ║
║   help                   - Show this help                    ║
║   exit/quit              - Exit CLI                          ║
║                                                              ║
║ Multi-line Scripts:                                          ║
║   Start with """ (triple quotes)                            ║
║   End with """                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
        print(help_text)
    
    def show_statistics(self) -> None:
        """Show page statistics"""
        if not self.browser:
            print("❌ Browser not started")
            return
        
        stats = self.browser.get_last_statistics()
        if stats:
            print(stats)
        else:
            print("⚠️  No statistics available yet")
    
    def run(self) -> None:
        """Run the interactive CLI"""
        self.start_browser()
        
        print("\n" + "="*60)
        print("🌐 BrowserHDL Interactive CLI")
        print("="*60)
        print(f"Using adapter: {self.adapter_name}")
        print("Type 'help' for available commands, 'exit' to quit")
        print("="*60 + "\n")
        
        while self.running:
            try:
                # Get input
                line = input("browserhdl> ").strip()
                
                if not line:
                    continue
                
                # Check for multi-line script start
                if line.startswith('"""'):
                    self.handle_multiline_script()
                    continue
                
                # Handle single commands
                self.execute_command(line)
                
            except KeyboardInterrupt:
                print("\n👋 Interrupted. Type 'exit' to quit.")
            except EOFError:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        
        # Cleanup
        if self.browser:
            self.browser.stop()
    
    def handle_multiline_script(self) -> None:
        """Handle multi-line script input"""
        print("Entering multi-line mode. End with \"\"\"")
        self.script_buffer = []
        
        while True:
            line = input("... ")
            if line.strip() == '"""':
                break
            self.script_buffer.append(line)
        
        # Execute the script
        script = "\n".join(self.script_buffer)
        self.execute_script(script)
        self.script_buffer = []
    
    def execute_command(self, command: str) -> None:
        """Execute a single command"""
        command = command.strip()
        
        # Built-in commands
        if command in ['help', '?']:
            self.show_help()
        elif command in ['exit', 'quit']:
            self.running = False
        elif command == 'stats':
            self.show_statistics()
        else:
            # Try to execute as Python
            self.execute_script(command)
    
    def execute_script(self, script: str) -> None:
        """Execute Python script with browser context"""
        if not self.browser:
            print("❌ Browser not started")
            return
        
        # Create execution context
        context = {
            'browser': self.browser,
            'navigate': self.browser.navigate,
            'html': self.browser.get_html,
            'execute': self.browser.execute_script,
            'find': self.browser.find_element,
            'find_all': self.browser.find_elements,
            'click': self.browser.click,
            'fill': self.browser.fill,
            'wait': self.browser.wait_for_selector,
            'screenshot': self.browser.screenshot,
            'get_cookies': self.browser.get_cookies,
            'set_cookie': self.browser.set_cookie,
            'get_storage': self.browser.get_local_storage,
            'set_storage': self.browser.set_local_storage,
            'load_profile': self._load_profile_cmd,
            'save_profile': self._save_profile_cmd,
            'list_profiles': self._list_profiles_cmd,
            'sleep': time.sleep,
            'print': print,
        }
        
        try:
            exec(script, context)
        except Exception as e:
            print(f"❌ Script error: {e}")
            import traceback
            traceback.print_exc()
    
    def _load_profile_cmd(self, name: str) -> None:
        """Load profile command"""
        try:
            profile_data = self.profile_manager.load_profile(name)
            if self.browser:
                self.browser.load_profile(profile_data)
            self.current_profile = name
            print(f"✓ Profile '{name}' loaded")
        except Exception as e:
            print(f"❌ Failed to load profile: {e}")
    
    def _save_profile_cmd(self, name: str) -> None:
        """Save profile command"""
        if not self.browser:
            print("❌ Browser not started")
            return
        
        try:
            profile_data = {
                "cookies": self.browser.get_cookies(),
                "localStorage": self.browser.get_local_storage(),
                "settings": {}
            }
            self.profile_manager.save_profile(name, profile_data)
            print(f"✓ Profile '{name}' saved")
        except Exception as e:
            print(f"❌ Failed to save profile: {e}")
    
    def _list_profiles_cmd(self) -> None:
        """List profiles command"""
        profiles = self.profile_manager.list_profiles()
        if not profiles:
            print("No profiles found")
            return
        
        print("\n📁 Available Profiles:")
        print("="*60)
        for profile in profiles:
            print(f"  • {profile.name} ({profile.source})")
            print(f"    Created: {profile.created_at}")
            print(f"    Modified: {profile.modified_at}")
            if profile.endpoint:
                print(f"    Endpoint: {profile.endpoint}")
            print()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='BrowserHDL Interactive CLI')
    parser.add_argument('adapter', nargs='?', default='playwright-chromium',
                      help='Browser adapter to use')
    parser.add_argument('url', nargs='?', help='Initial URL to navigate to')
    parser.add_argument('--list-adapters', action='store_true',
                      help='List available adapters')
    
    args = parser.parse_args()
    
    if args.list_adapters:
        print("Available adapters:")
        for name in BrowserCLI.ADAPTERS.keys():
            print(f"  • {name}")
        return
    
    cli = BrowserCLI(adapter_name=args.adapter, initial_url=args.url)
    cli.run()


if __name__ == '__main__':
    main()
