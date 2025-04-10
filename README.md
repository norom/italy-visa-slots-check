# Prenotami Appointment Checker

An automated tool to check for available appointments on the Italian consular services website (prenotami.esteri.it) with scheduled monitoring and notifications.

## Description

This system automates the process of logging into the Prenotami website and checking for available appointment slots. It uses Selenium with anti-bot detection measures to navigate through the website and includes a scheduler to periodically check for appointments. When an appointment becomes available, the system sends notifications via Telegram.

## Features

- Automated login to prenotami.esteri.it
- Anti-bot detection measures using selenium-stealth
- Human-like behavior simulation with random delays
- Multiple login attempt strategies
- Cookie persistence for future sessions
- Screenshot capture at critical steps
- Detailed logging of the process
- Scheduled appointment checking (approximately hourly with randomization)
- Telegram notifications when appointments become available
- Daily status summaries
- Artifact archiving for debugging and verification

## Components

The system consists of several Python scripts:

1. **login.py** - Handles the core website interaction and appointment checking logic
2. **appointment_monitor.py** - Runs the login script and sends notifications when appointments are found
3. **scheduler.py** - Provides automated scheduling of appointment checks

## Requirements

- Python 3.6+
- Chrome browser
- Internet connection
- Telegram bot (for notifications)

## Dependencies

The scripts require the following Python packages:

```
selenium
webdriver-manager
selenium-stealth
requests
schedule
beautifulsoup4
```

Install dependencies with pip:

```bash
pip install selenium webdriver-manager selenium-stealth requests schedule beautifulsoup4
```

## Configuration

### 1. Credentials Setup

Create a `credentials.json` file in the same directory with your Prenotami login details:

```json
{
  "email": "your-prenotami-email@example.com",
  "password": "your-prenotami-password"
}
```

### 2. Telegram Notifications Setup

Create a `telegram_config.json` file for notification capabilities:

```json
{
  "bot_token": "YOUR_TELEGRAM_BOT_TOKEN",
  "chat_id": "YOUR_TELEGRAM_CHAT_ID"
}
```

## Usage

### Manual Check

Run a single check for available appointments:

```bash
python appointment_monitor.py
```

### Scheduled Monitoring

Start the automated scheduler to check for appointments approximately hourly:

```bash
python scheduler.py
```

The scheduler will:
- Run checks approximately every hour (with ±10 minutes of randomization)
- Log all activity to the artifacts directory
- Send notifications through Telegram when appointments become available
- Provide daily summaries when no appointments are found

## Output Files

The scripts generate several files in the `artifacts` directory:

- `scheduler.log`: Log of all scheduler activities
- `appointment_check_YYYYMMDD_HHMMSS.log`: Logs from individual checks
- `form_filled_attempt_N.png`: Screenshot after filling the login form
- `after_login_attempt_N.png`: Screenshot after attempting to log in
- `error_attempt_N.png`: Screenshot if an error occurs
- `prenotami_cookies_attempt_N.json`: Saved cookies after successful login
- `services_page_attempt_N.png`: Screenshot of the services page
- `booking_page_1151.png/html`: Screenshot/HTML of the booking page for service 1151
- `booking_page_1258.png/html`: Screenshot/HTML of the booking page for service 1258
- `daily_status.json`: Tracking of check results and history

## Functionality

The system works by:

1. **Scheduler (scheduler.py)**:
   - Runs appointment checks approximately every hour with randomized timing
   - Logs all activity for troubleshooting

2. **Monitor (appointment_monitor.py)**:
   - Executes the login script to check appointment availability
   - Processes the results and determines if appointments are available
   - Sends Telegram notifications when appointments are found
   - Provides daily summaries
   - Maintains tracking of check history

3. **Login Script (login.py)**:
   - Reads credentials from a JSON file
   - Configures Chrome with anti-bot detection measures
   - Navigates to the Prenotami website
   - Simulates human-like typing and interaction behavior
   - Checks multiple booking service pages for appointment availability
   - Saves screenshots and HTML content for verification

## Services Monitored

The system checks for appointments for two specific services:
- Service ID 1151
- Service ID 1258

## Troubleshooting

- If you see "ERROR: Telegram configuration missing or invalid," check your telegram_config.json file.
- If you see "Error: Credentials file 'credentials.json' not found", create the credentials file as described in the Configuration section.
- Check the generated logs, screenshots, and HTML files in the artifacts directory for debugging.
- If the scheduler stops unexpectedly, check the scheduler.log file for errors.

## Legal Notice

This tool is meant for personal use only. Please respect the website's terms of service and avoid excessive requests that might overload their servers.

## License

This project is provided as-is with no warranties or guarantees.