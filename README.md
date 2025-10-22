# BrowserHDL - Headless Browser Module

A powerful, flexible headless browser module supporting multiple browser engines with an intuitive CLI interface.

## Features

- **Multi-Adapter Support**: Playwright (Chromium, Firefox, WebKit) and Selenium (Chrome, Firefox, Edge, Safari)
- **Profile Management**: Internal and external user profiles with cookies, localStorage, and settings
- **Interactive CLI**: Command-line interface with multi-line script support
- **Event System**: Comprehensive event handling (onload, onerror, onconsole, etc.)
- **LocalLib Support**: Register and use local library resources
- **Statistics**: Detailed page load statistics and metrics
- **Export/Import**: Profile export in JSON, XML, and ZIP formats
- **Docker Support**: Fully containerized deployment option

## Installation

### Quick Install

```bash
./scripts/install.sh install
```

### Manual Install

```bash
pip install -r requirements.txt
python -m playwright install chromium firefox webkit
pip install -e .
```

## Usage

### Command Line

```bash
# Start with default adapter (Playwright Chromium)
browserhdl

# Specify adapter
browserhdl playwright-firefox

# Navigate to URL on start
browserhdl selenium-chrome https://example.com

# List available adapters
browserhdl --list-adapters
```

### Using Scripts

```bash
# Run with default settings
./scripts/run.sh

# Run with specific adapter and URL
./scripts/run.sh playwright-webkit https://example.com
```

### Docker

```bash
# Build Docker image
./scripts/docker.sh build

# Run in Docker
./scripts/docker.sh run

# Stop container
./scripts/docker.sh stop
```

## Interactive CLI

Once in the interactive CLI, you can use the following commands:

### Navigation

```python
navigate("https://example.com")
html()                    # Get page HTML
```

### Element Interaction

```python
find("button.submit")     # Find element
click("button.submit")    # Click element
fill("input#email", "user@example.com")  # Fill input
wait("div.content")       # Wait for element
```

### JavaScript Execution

```python
execute("return document.title")
execute("console.log('Hello')")
```

### Cookies & Storage

```python
get_cookies()             # Get all cookies
set_cookie("name", "value")
get_storage()             # Get localStorage
set_storage("key", "value")
```

### Profiles

```python
save_profile("myprofile")    # Save current profile
load_profile("myprofile")    # Load profile
list_profiles()              # List all profiles
```

### Utility Commands

```python
screenshot("page.png")    # Take screenshot
sleep(2)                  # Wait 2 seconds
stats                     # Show page statistics
help                      # Show help
exit                      # Exit CLI
```

### Multi-line Scripts

Start with `"""` and end with `"""`:

```python
"""
navigate("https://example.com")
wait("input#username")
fill("input#username", "user")
fill("input#password", "pass")
click("button[type='submit']")
sleep(2)
print("Login complete!")
"""
```

## Available Adapters

- `playwright-chromium` - Playwright with Chromium engine (default)
- `playwright-firefox` - Playwright with Firefox engine
- `playwright-webkit` - Playwright with WebKit engine
- `selenium-chrome` - Selenium with Chrome browser
- `selenium-firefox` - Selenium with Firefox browser
- `selenium-edge` - Selenium with Edge browser
- `selenium-safari` - Selenium with Safari browser

## Examples

### Example 1: Web Scraping

```python
navigate("https://news.ycombinator.com")
wait(".storylink")
links = find_all(".storylink")
for link in links[:10]:
    print(link.text)
```

### Example 2: Form Automation

```python
navigate("https://example.com/login")
fill("input[name='username']", "myuser")
fill("input[name='password']", "mypass")
click("button[type='submit']")
sleep(2)
screenshot("logged_in.png")
save_profile("example_profile")
```

### Example 3: Profile Management

```python
# Save profile with cookies and storage
navigate("https://example.com")
# ... perform login ...
save_profile("example_user")

# Later, load the profile
load_profile("example_user")
navigate("https://example.com/dashboard")
# Already logged in!
```

## Profile Management

### Internal Profiles

Profiles are stored locally in the `profiles/` directory with SQLite tracking for integrity verification.

```python
# Create and save a profile
save_profile("myprofile")

# Load a profile
load_profile("myprofile")

# Export profile
profile_manager.export_profile("myprofile", format="json")
profile_manager.export_profile("myprofile", format="xml")
profile_manager.export_profile("myprofile", format="zip")
```

### External Profiles

Register external profiles from HTTP endpoints:

```python
profile_manager.register_external_profile(
    name="remote_profile",
    endpoint="https://api.example.com/profiles/user123",
    username="admin",
    password="secret"
)

# Load external profile
load_profile("remote_profile")
```

### LocalLib Resources

Register local library resources:

```python
profile_manager.register_locallib("mylib", "/path/to/library")
path = profile_manager.get_locallib("mylib")
```

## Configuration

Create a `config.json` file in the project root:

```json
{
  "default_adapter": "playwright-chromium",
  "headless": true,
  "profiles_dir": "profiles",
  "timeout": 30000
}
```

## Architecture

```
browserhdl/
├── core/               # Core interfaces and base classes
│   └── browser_interface.py
├── adapters/           # Browser adapters
│   ├── playwright_adapter.py
│   └── selenium_adapter.py
├── profiles/           # Profile management
│   └── profile_manager.py
├── cli/                # CLI interface
│   └── interactive_cli.py
├── proxy/              # Proxy support (future)
└── utils/              # Utility functions
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black browserhdl/
flake8 browserhdl/
```

### Type Checking

```bash
mypy browserhdl/
```

## Requirements

- Python 3.8+
- Playwright 1.40.0+
- Selenium 4.15.0+
- requests 2.31.0+

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues, questions, or contributions, please visit:
https://github.com/m5ike/browserhdl

## Author

m5ike

## Changelog

### Version 1.0.0 (2025)
- Initial release
- Multi-adapter support (Playwright & Selenium)
- Interactive CLI with multi-line script support
- Profile management (internal & external)
- Event system
- Docker support
- Export/Import functionality
- LocalLib support
- Comprehensive documentation
