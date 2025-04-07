import subprocess
import json
import time
import os
import re
import requests
from datetime import datetime

# Configuration file path
CONFIG_FILE = "telegram_config.json"
# Artifacts directory
ARTIFACTS_DIR = "artifacts"

def ensure_artifacts_dir():
    """Ensure the artifacts directory exists"""
    if not os.path.exists(ARTIFACTS_DIR):
        os.makedirs(ARTIFACTS_DIR)
        print(f"Created artifacts directory: {ARTIFACTS_DIR}")

def load_telegram_config():
    """Load Telegram bot token and chat ID from config file"""
    try:
        with open(CONFIG_FILE, 'r') as file:
            config = json.load(file)
            return config.get('bot_token'), config.get('chat_id')
    except FileNotFoundError:
        print(f"Error: Config file '{CONFIG_FILE}' not found.")
        return None, None
    except json.JSONDecodeError:
        print(f"Error: Config file '{CONFIG_FILE}' is not valid JSON.")
        return None, None
    except Exception as e:
        print(f"Error reading config: {e}")
        return None, None

def send_telegram_message(bot_token, chat_id, message):
    """Send message to Telegram chat"""
    if not bot_token or not chat_id:
        print("ERROR: Missing bot token or chat ID")
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print(f"Message sent successfully to Telegram at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            return True
        else:
            print(f"Failed to send message. Status code: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error sending Telegram message: {e}")
        return False

def check_log_for_appointments(log_file):
    """Check the log file for appointment availability messages"""
    try:
        with open(log_file, 'r') as file:
            log_content = file.read()
            
            # Check for availability messages
            if "Appointments might be available for service 1151" in log_content:
                return 1151, True
            elif "Appointments might be available for service 1258" in log_content:
                return 1258, True
            else:
                # Check both services are fully booked
                service1151_checked = "No appointments available for service 1151" in log_content
                service1258_checked = "No appointments available for service 1258" in log_content
                
                if service1151_checked and service1258_checked:
                    return None, False
                else:
                    # Script may have failed before checking all services
                    return None, None
    except FileNotFoundError:
        print(f"Log file {log_file} not found.")
        return None, None
    except Exception as e:
        print(f"Error reading log file: {e}")
        return None, None

def run_appointment_check():
    """Run the login.py script and capture output to a log file"""
    ensure_artifacts_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(ARTIFACTS_DIR, f"appointment_check_{timestamp}.log")
    
    print(f"Starting appointment check at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Log will be saved to {log_file}")
    
    try:
        # Run the login.py script and redirect output to log file
        with open(log_file, 'w') as f:
            process = subprocess.Popen(['python3', 'login.py'], 
                                      stdout=f, 
                                      stderr=subprocess.STDOUT)
            process.wait()
        
        print(f"Appointment check completed with exit code {process.returncode}")
        return log_file
    except Exception as e:
        print(f"Error running appointment check: {e}")
        return None

def update_daily_status(available=False):
    """Update the daily status file to track if appointments were available today"""
    status_file = os.path.join(ARTIFACTS_DIR, "daily_status.json")
    today = datetime.now().strftime("%Y-%m-%d")
    
    try:
        # Read existing data if file exists
        if os.path.exists(status_file):
            with open(status_file, 'r') as f:
                status_data = json.load(f)
        else:
            status_data = {"last_available_date": None, "checks_today": 0, "date": today}
        
        # Update the date if it's a new day
        if status_data.get("date") != today:
            status_data = {"last_available_date": status_data.get("last_available_date"), "checks_today": 0, "date": today}
        
        # Increment the checks counter
        status_data["checks_today"] = status_data.get("checks_today", 0) + 1
        
        # Update the last available date if appointments are available
        if available:
            status_data["last_available_date"] = today
        
        # Save updated data
        with open(status_file, 'w') as f:
            json.dump(status_data, f)
            
        return status_data
    except Exception as e:
        print(f"Error updating daily status: {e}")
        return None

def is_summary_time():
    """Check if it's time to send the daily summary (around 17:00)"""
    now = datetime.now()
    return now.hour == 17 and 0 <= now.minute < 10  # Between 17:00 and 17:10

def send_daily_summary(bot_token, chat_id):
    """Send a daily summary message if no appointments were available today"""
    status_file = os.path.join(ARTIFACTS_DIR, "daily_status.json")
    
    try:
        if not os.path.exists(status_file):
            return False
            
        with open(status_file, 'r') as f:
            status_data = json.load(f)
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Only send summary if it's for today and we haven't found appointments today
        if status_data.get("date") == today and status_data.get("last_available_date") != today:
            checks_today = status_data.get("checks_today", 0)
            last_available = status_data.get("last_available_date", "never")
            
            message = f"📊 <b>DAILY SUMMARY</b>\n\n"
            message += f"Date: {today}\n"
            message += f"Checks performed today: {checks_today}\n"
            message += f"Result: No appointments were available today\n"
            
            if last_available and last_available != "never":
                message += f"Last time appointments were available: {last_available}"
            else:
                message += "No appointments have been available since monitoring began."
            
            # Send the summary message
            send_telegram_message(bot_token, chat_id, message)
            return True
    
    except Exception as e:
        print(f"Error sending daily summary: {e}")
    
    return False

def main():
    """Main monitoring function"""
    # Ensure artifacts directory exists
    ensure_artifacts_dir()
    
    # Load Telegram configuration
    bot_token, chat_id = load_telegram_config()
    if not bot_token or not chat_id:
        print("ERROR: Telegram configuration missing or invalid. Please check telegram_config.json")
        print("Example format: {\"bot_token\": \"YOUR_BOT_TOKEN\", \"chat_id\": \"YOUR_CHAT_ID\"}")
        return
    
    print("Telegram configuration loaded successfully")
    
    # Check if it's time for the daily summary
    if is_summary_time():
        print("It's summary time. Checking if we need to send a daily summary...")
        summary_sent = send_daily_summary(bot_token, chat_id)
        if summary_sent:
            print("Daily summary sent successfully")
    
    # Get HTML files before running check (to compare after)
    existing_html_files = set([f for f in os.listdir(ARTIFACTS_DIR) if f.startswith("booking_page_") and f.endswith(".html")])
    
    # Run appointment check
    log_file = run_appointment_check()
    if not log_file:
        message = "⚠️ Error running appointment check script! Please check the system."
        send_telegram_message(bot_token, chat_id, message)
        return
    
    # New HTML files after check
    new_html_files = set([f for f in os.listdir(ARTIFACTS_DIR) if f.startswith("booking_page_") and f.endswith(".html")])
    new_files = new_html_files - existing_html_files
    
    # Check results
    service_code, is_available = check_log_for_appointments(log_file)
    
    if is_available is True:
        # Appointments available! Update daily status and send notification
        update_daily_status(available=True)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"🎉 <b>APPOINTMENT AVAILABLE!</b> 🎉\n\nService code: {service_code}\nDetected at: {timestamp}\n\n⚡ Book immediately at https://prenotami.esteri.it/Services/Booking/{service_code}"
        
        # Add HTML file info if available
        html_file = f"booking_page_{service_code}.html"
        if html_file in new_files:
            message += f"\n\nHTML file saved: {os.path.join(ARTIFACTS_DIR, html_file)}"
        
        # Send notification
        send_telegram_message(bot_token, chat_id, message)
        
    elif is_available is False:
        # No appointments available - update daily status but DON'T send notification
        update_daily_status(available=False)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"No appointments available at {timestamp}. Both services checked and fully booked.")
        
    else:
        # Script may have failed to check all services - this is an error condition, so send notification
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"⚠️ Script may not have completed successfully at {timestamp}. Please check log file: {log_file}"
        send_telegram_message(bot_token, chat_id, message)

if __name__ == "__main__":
    main()