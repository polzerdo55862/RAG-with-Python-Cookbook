# Playwright Browser Configuration Examples

# Default browser (Chromium)
default_params = {"command": "npx", "args": ["@playwright/mcp@latest"]}

# Microsoft Edge
edge_params = {
    "command": "npx",
    "args": ["@playwright/mcp@latest", "--browser", "msedge"],
}

# Firefox
firefox_params = {
    "command": "npx",
    "args": ["@playwright/mcp@latest", "--browser", "firefox"],
}

# Chrome (if installed)
chrome_params = {
    "command": "npx",
    "args": ["@playwright/mcp@latest", "--browser", "chrome"],
}

# Headless mode (no GUI)
headless_params = {"command": "npx", "args": ["@playwright/mcp@latest", "--headless"]}

# Edge with custom options
edge_custom_params = {
    "command": "npx",
    "args": [
        "@playwright/mcp@latest",
        "--browser",
        "msedge",
        "--viewport-width",
        "1920",
        "--viewport-height",
        "1080",
    ],
}
