from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
import time
import json
import random
from tempfile import mkdtemp
import os

# Function to add random delays between actions
def human_delay():
    time.sleep(random.uniform(1.0, 3.0))

# Function to navigate to a URL with timeout handling
def navigate_with_timeout(driver, url, timeout=30):
    """Navigate to a URL with timeout handling and retry mechanism"""
    print(f"Navigating to {url} with {timeout} second timeout...")
    
    # Set page load timeout
    driver.set_page_load_timeout(timeout)
    
    try:
        driver.get(url)
        return True
    except Exception as e:
        print(f"Timeout or error accessing {url}: {e}")
        # Try to cancel navigation by executing JavaScript
        try:
            driver.execute_script("window.stop();")
        except:
            pass
        return False

# Function to attempt logout and re-login
def logout_and_retry(driver):
    """Attempt to logout and then re-login"""
    print("Attempting to logout...")
    
    try:
        # Cancel any ongoing requests
        driver.execute_script("window.stop();")
        
        # Navigate to logout page with timeout
        logout_success = navigate_with_timeout(driver, "https://prenotami.esteri.it/Account/LogOff", 15)
        
        if logout_success:
            print("Logout successful")
            human_delay()
            return True
        else:
            print("Logout timed out, will try a fresh session")
            # If logout times out, we'll just refresh the driver in the main loop
            return False
            
    except Exception as e:
        print(f"Error during logout: {e}")
        return False

# Function to read credentials from file
def read_credentials(file_path="credentials.json"):
    try:
        with open(file_path, 'r') as file:
            credentials = json.load(file)
            return credentials.get('email'), credentials.get('password')
    except FileNotFoundError:
        print(f"Error: Credentials file '{file_path}' not found.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error: Credentials file '{file_path}' is not valid JSON.")
        exit(1)
    except Exception as e:
        print(f"Error reading credentials: {e}")
        exit(1)

# Read login credentials from external file
EMAIL, PASSWORD = read_credentials()

if not EMAIL or not PASSWORD:
    print("Error: Email or password missing in credentials file.")
    exit(1)

# Configure Chrome options
chrome_options = Options()

# Anti-bot detection measures
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.6943.53 Safari/537.36")

# Other options
temp_dir = mkdtemp()
chrome_options.add_argument(f"--user-data-dir={temp_dir}")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")

# Initialize the driver with the correct ChromeDriver version
print("Installing ChromeDriver...")
driver_path = ChromeDriverManager().install()
print(f"Using ChromeDriver from: {driver_path}")
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Apply stealth settings
stealth(driver,
      languages=["en-US", "en"],
      vendor="Google Inc.",
      platform="Win32",
      webgl_vendor="Intel Inc.",
      renderer="Intel Iris OpenGL Engine",
      fix_hairline=True,
)

print("Selenium-stealth applied")

try:
    max_retries = 3
    current_retry = 0
    
    while current_retry < max_retries:
        # Open the website directly to the English version
        print(f"Attempt {current_retry + 1}/{max_retries}")
        
        if current_retry > 0:
            print("Refreshing session after timeout...")
            try:
                # Close and reopen browser for a fresh session
                driver.quit()
                driver = webdriver.Chrome(service=service, options=chrome_options)
                
                # Reapply stealth settings
                stealth(driver,
                      languages=["en-US", "en"],
                      vendor="Google Inc.",
                      platform="Win32",
                      webgl_vendor="Intel Inc.",
                      renderer="Intel Iris OpenGL Engine",
                      fix_hairline=True,
                )
                print("Selenium-stealth reapplied for new session")
            except Exception as e:
                print(f"Error refreshing browser session: {e}")
                break
        
        print("Opening the website directly in English...")
        site_loaded = navigate_with_timeout(driver, "https://prenotami.esteri.it/?lang=en-GB", 30)
        
        if not site_loaded:
            print("Initial site load timed out, retrying...")
            current_retry += 1
            continue
            
        human_delay()
        
        print("Accessing login page...")
        
        # Login process
        try:
            print("Looking for email field...")
            try:
                email_field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@id='Email' or @name='Email']"))
                )
            except Exception as e:
                print(f"Error finding email field: {e}")
                driver.save_screenshot(f"login_error_attempt_{current_retry}.png")
                current_retry += 1
                continue
                
            print("Found email field, filling form...")
            email_field.clear()
            human_delay()
            # Type email character by character like a human
            for char in EMAIL:
                email_field.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            human_delay()
            
            print("Looking for password field...")
            password_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@id='Password' or @name='Password']"))
            )
            password_field.clear()
            human_delay()
            # Type password character by character
            for char in PASSWORD:
                password_field.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
                
            human_delay()
            
            driver.save_screenshot(f"form_filled_attempt_{current_retry}.png")
            print("Form filled, saved screenshot")
            
            # Click on the Forward button
            print("Attempting to click login button...")
            try:
                # Find by JavaScript rather than Selenium
                driver.execute_script("""
                    let buttons = document.querySelectorAll('button');
                    for (let btn of buttons) {
                        if (btn.textContent.includes('FORWARD') || btn.type === 'submit') {
                            btn.click();
                            return;
                        }
                    }
                """)
                print("Clicked button using JavaScript")
            except Exception as e:
                print(f"JavaScript click failed: {e}")
                # Fall back to Selenium
                try:
                    forward_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'FORWARD')]"))
                    )
                    forward_button.click()
                    print("Clicked FORWARD button by text")
                except Exception as e:
                    print(f"First attempt failed: {e}")
                    try:
                        forward_button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
                        )
                        forward_button.click()
                        print("Clicked submit button by type")
                    except Exception as e:
                        print(f"Second attempt failed: {e}")
                        try:
                            forward_button = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-primary"))
                            )
                            forward_button.click()
                            print("Clicked button by class")
                        except Exception as e:
                            print(f"All click attempts failed: {e}")
                            current_retry += 1
                            continue
            
            human_delay()
            
            # Check if we're logged in
            driver.save_screenshot(f"after_login_attempt_{current_retry}.png")
            print("Login attempt completed, saved screenshot")
            
            # Get all cookies
            cookies = driver.get_cookies()
            with open(f"prenotami_cookies_attempt_{current_retry}.json", "w") as f:
                json.dump(cookies, f)
            
            print("Cookies saved to prenotami_cookies.json")
            
            # First navigate to the Services page
            print("Navigating to the main Services page...")
            services_loaded = navigate_with_timeout(driver, "https://prenotami.esteri.it/Services", 30)
            
            if not services_loaded:
                print("Services page timed out, logging out and retrying...")
                logout_success = logout_and_retry(driver)
                current_retry += 1
                continue
                
            human_delay()
            driver.save_screenshot(f"services_page_attempt_{current_retry}.png")
            print("Services page accessed, saved screenshot")
            
            # Then navigate to the first booking page
            print("Navigating to the first booking service page (1151)...")
            booking_loaded = navigate_with_timeout(driver, "https://prenotami.esteri.it/Services/Booking/1151", 30)
            
            if not booking_loaded:
                print("Booking page 1151 timed out, logging out and retrying...")
                logout_success = logout_and_retry(driver)
                current_retry += 1
                continue
                
            human_delay()
            
            # Check for the "fully booked" message
            page_source = driver.page_source
            if "Sorry, all appointments for this service are currently booked" in page_source:
                print("RESULT: No appointments available for service 1151 - all slots are booked.")
                
                # Try the second booking page with delay
                print("Trying alternative booking service page (1258)...")
                human_delay()  # Additional delay before trying next service
                
                booking2_loaded = navigate_with_timeout(driver, "https://prenotami.esteri.it/Services/Booking/1258", 30)
                
                if not booking2_loaded:
                    print("Booking page 1258 timed out, logging out and retrying...")
                    logout_success = logout_and_retry(driver)
                    current_retry += 1
                    continue
                    
                human_delay()
                
                # Check the second service for availability
                page_source = driver.page_source
                if "Sorry, all appointments for this service are currently booked" in page_source:
                    print("RESULT: No appointments available for service 1258 either - all slots are booked.")
                else:
                    print("RESULT: Appointments might be available for service 1258!")
                    
                    # Save for inspection
                    driver.save_screenshot("booking_page_1258.png")
                    with open("booking_page_1258.html", "w", encoding="utf-8") as f:
                        f.write(page_source)
            else:
                print("RESULT: Appointments might be available for service 1151!")
                
                # Save for inspection
                driver.save_screenshot("booking_page_1151.png")
                with open("booking_page_1151.html", "w", encoding="utf-8") as f:
                    f.write(page_source)
                    
            # Success! Break out of retry loop
            break
                
        except Exception as e:
            print(f"Error during process attempt {current_retry}: {e}")
            driver.save_screenshot(f"error_attempt_{current_retry}.png")
            current_retry += 1
        
except Exception as e:
    print(f"An error occurred: {e}")
    
finally:
    # Close the browser
    driver.quit()
    
    # Cleanup
    try:
        import shutil
        shutil.rmtree(temp_dir)
    except:
        pass