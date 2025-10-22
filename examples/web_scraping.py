#!/usr/bin/env python3
"""
Example: Web Scraping with BrowserHDL
This script demonstrates how to use BrowserHDL for web scraping
"""

from browserhdl import PlaywrightAdapter, BrowserEvent

def main():
    # Create browser instance
    browser = PlaywrightAdapter(engine="chromium", headless=True)
    
    # Register event handlers
    browser.on(BrowserEvent.ON_LOAD, lambda: print("✓ Page loaded"))
    browser.on(BrowserEvent.ON_ERROR, lambda err: print(f"✗ Error: {err}"))
    
    try:
        # Start browser
        browser.start()
        
        # Navigate to Hacker News
        print("\n🌐 Navigating to Hacker News...")
        browser.navigate("https://news.ycombinator.com")
        
        # Wait for stories to load
        browser.wait_for_selector(".titleline")
        
        # Get all story titles
        script = """
        () => {
            const stories = [];
            document.querySelectorAll('.titleline').forEach((el, idx) => {
                if (idx < 10) {
                    stories.push({
                        title: el.textContent.trim(),
                        url: el.querySelector('a')?.href || ''
                    });
                }
            });
            return stories;
        }
        """
        
        stories = browser.execute_script(script)
        
        # Display results
        print("\n📰 Top 10 Stories:")
        print("=" * 80)
        for i, story in enumerate(stories, 1):
            print(f"{i}. {story['title']}")
            print(f"   {story['url']}\n")
        
        # Get page statistics
        stats = browser.get_statistics()
        print("\n📊 Page Statistics:")
        print(f"Load Time: {stats.load_time:.2f}s")
        print(f"Page Size: {stats.size_bytes / 1024:.2f} KB")
        print(f"Total Links: {stats.num_links}")
        
        # Take screenshot
        browser.screenshot("hackernews.png")
        print("\n📸 Screenshot saved as hackernews.png")
        
    finally:
        # Always stop the browser
        browser.stop()
    
    print("\n✓ Example completed successfully!")

if __name__ == "__main__":
    main()
