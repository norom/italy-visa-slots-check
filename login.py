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
    # Open the website directly to the English version
    print("Opening the website directly in English...")
    driver.get("https://prenotami.esteri.it/?lang=en-GB")
    human_delay()
    
    print("Accessing login page...")
    
    # Login process
    try:
        print("Looking for email field...")
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='Email' or @name='Email']"))
        )
        
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
        
        driver.save_screenshot("form_filled.png")
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
        
        human_delay()
        
        # Check if we're logged in
        driver.save_screenshot("after_login.png")
        print("Login attempt completed, saved screenshot")
        
        # Get all cookies
        cookies = driver.get_cookies()
        with open("prenotami_cookies.json", "w") as f:
            json.dump(cookies, f)
        
        print("Cookies saved to prenotami_cookies.json")
        
        # First navigate to the Services page
        print("Navigating to the main Services page...")
        driver.get("https://prenotami.esteri.it/Services")
        human_delay()
        driver.save_screenshot("services_page.png")
        print("Services page accessed, saved screenshot")
        
        # Then navigate to the specific booking page
        print("Navigating to the specific booking service page...")
        driver.get("https://prenotami.esteri.it/Services/Booking/1151")
        human_delay()
        
        # Check for the "fully booked" message
        page_source = driver.page_source
        if "Sorry, all appointments for this service are currently booked" in page_source:
            print("RESULT: No appointments available - all slots are booked.")
        else:
            print("RESULT: Appointments might be available!")
            
            # Save for inspection
            driver.save_screenshot("booking_page.png")
            with open("booking_page.html", "w", encoding="utf-8") as f:
                f.write(page_source)
                
    except Exception as e:
        print(f"Error during process: {e}")
        driver.save_screenshot("error.png")
        
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