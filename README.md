# Prenotami Appointment Checker

An automated tool to check for available appointments on the Italian consular services website (prenotami.esteri.it).

## Description

This script automates the process of logging into the Prenotami website and checking for available appointment slots. It uses Selenium with anti-bot detection measures to navigate through the website, and falls back to direct HTTP requests if Selenium is detected.

## Features

- Automated login to prenotami.esteri.it
- Anti-bot detection measures using selenium-stealth
- Human-like behavior simulation with random delays
- Multiple login attempt strategies
- Fallback to direct HTTP requests if automation is detected
- Cookie persistence for future sessions
- Screenshot capture at critical steps
- Detailed logging of the process

## Requirements

- Python 3.6+
- Chrome browser
- Internet connection

## Dependencies

The script requires the following Python packages:

```
selenium
webdriver-manager
selenium-stealth
requests
beautifulsoup4
```

Install dependencies with pip:

```bash
pip install selenium webdriver-manager selenium-stealth requests beautifulsoup4
```

## Configuration

Create a `credentials.json` file in the same directory as the script with the following format:

```json
{
  "email": "your-prenotami-email@example.com",
  "password": "your-prenotami-password"
}
```

## Usage

1. Ensure you have Chrome installed on your system
2. Create the credentials.json file with your login details
3. Run the script:

```bash
python login.py
```

## Output

The script generates several files during execution:

- `form_filled.png`: Screenshot after filling the login form
- `after_login.png`: Screenshot after attempting to log in
- `error.png`: Screenshot if an error occurs
- `prenotami_cookies.json`: Saved cookies after successful login with Selenium
- `prenotami_cookies_requests.json`: Saved cookies after successful login with requests
- `booking_page.html`: HTML content of the booking page
- `booking_page.png`: Screenshot of the booking page
- `unavailable_page.html`: HTML content if "Unavailable" is detected
- `login_response.html`: HTML content of the login response when using requests

## Functionality

The script works by:

1. Reading credentials from a JSON file
2. Configuring Chrome with anti-bot detection measures
3. Navigating to the Prenotami website
4. Filling in the login form with human-like typing behavior
5. Attempting to click the login button using multiple methods
6. Checking if login was successful
7. If detected as a bot, falling back to direct HTTP requests
8. Checking the specific booking service page for appointment availability
9. Saving the results and relevant screenshots/HTML

## Troubleshooting

- If you see "Error: Credentials file 'credentials.json' not found", create the credentials file as described in the Configuration section.
- If the script fails with "Website returned 'Unavailable'", it may mean the website has detected automation. The script will try alternative methods.
- Check the generated screenshots and HTML files for further debugging.

## Legal Notice

This tool is meant for personal use only. Please respect the website's terms of service and avoid excessive requests that might overload their servers.

## License

This project is provided as-is with no warranties or guarantees.