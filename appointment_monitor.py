import subprocess
import json
import time
import os
import re
import requests
from datetime import datetime

# Configuration file path
CONFIG_FILE = "telegram_config.json"

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
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"appointment_check_{timestamp}.log"
    
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

def main():
    """Main monitoring function"""
    # Load Telegram configuration
    bot_token, chat_id = load_telegram_config()
    if not bot_token or not chat_id:
        print("ERROR: Telegram configuration missing or invalid. Please check telegram_config.json")
        print("Example format: {\"bot_token\": \"YOUR_BOT_TOKEN\", \"chat_id\": \"YOUR_CHAT_ID\"}")
        return
    
    print("Telegram configuration loaded successfully")
    
    # Get HTML files before running check (to compare after)
    existing_html_files = set([f for f in os.listdir() if f.startswith("booking_page_") and f.endswith(".html")])
    
    # Run appointment check
    log_file = run_appointment_check()
    if not log_file:
        message = "⚠️ Error running appointment check script! Please check the system."
        send_telegram_message(bot_token, chat_id, message)
        return
    
    # New HTML files after check
    new_html_files = set([f for f in os.listdir() if f.startswith("booking_page_") and f.endswith(".html")])
    new_files = new_html_files - existing_html_files
    
    # Check results
    service_code, is_available = check_log_for_appointments(log_file)
    
    if is_available is True:
        # Appointments available!
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"🎉 <b>APPOINTMENT AVAILABLE!</b> 🎉\n\nService code: {service_code}\nDetected at: {timestamp}\n\n⚡ Book immediately at https://prenotami.esteri.it/Services/Booking/{service_code}"
        
        # Add HTML file info if available
        html_file = f"booking_page_{service_code}.html"
        if html_file in new_files:
            message += f"\n\nHTML file saved: {html_file}"
        
        # Send notification
        send_telegram_message(bot_token, chat_id, message)
        
    elif is_available is False:
        # No appointments available
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"😞 No appointments available at {timestamp}. Both services checked and fully booked."
        send_telegram_message(bot_token, chat_id, message)
        
    else:
        # Script may have failed to check all services
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"⚠️ Script may not have completed successfully at {timestamp}. Please check log file: {log_file}"
        send_telegram_message(bot_token, chat_id, message)

if __name__ == "__main__":
    main()