from selenium import webdriver
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import requests
import config

# === Telegram Notification ===
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": config.TELEGRAM_CHAT_ID,
        "text": message
    }
    requests.post(url, data=payload)

# === Start Selenium Driver ===
# Set ChromeDriver service with your path
service = Service(executable_path=config.CHROME_DRIVER_PATH)

# Optional: set options if needed
options = Options()
# options.add_argument("--headless")  # uncomment this to run without opening a window

# Initialize the driver
driver = webdriver.Chrome(service=service, options=options)

driver.get(config.LOGIN_URL)
time.sleep(3)  # Wait for page to load

# === Login Logic ===
wait = WebDriverWait(driver, 10)
buttons = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "top-pad-10")))

for button in buttons:
    if button.text.strip() == "Giriş yapmak için tıklayınız":
        wait.until(EC.element_to_be_clickable((By.XPATH, f"//*[text()='Giriş yapmak için tıklayınız']"))).click()
        break

username_field = driver.find_element(By.ID,  "username")
password_field = driver.find_element(By.ID, "password")

username_field.send_keys(config.USERNAME)
password_field.send_keys(config.PASSWORD)

MAX_RETRIES = 3
for attempt in range(MAX_RETRIES):
    try:
        wait = WebDriverWait(driver, 10)
        
        # Wait until it's present and visible
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".btn.btn-success.w-100")))
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn.btn-success.w-100")))

        # Then refetch and click
        login_button = driver.find_element(By.CSS_SELECTOR, ".btn.btn-success.w-100")
        login_button.click()
        print("Login button clicked.")
        break

    except StaleElementReferenceException:
        print(f"Login button went stale. Retrying... ({attempt + 1}/{MAX_RETRIES})")
        if attempt == MAX_RETRIES - 1:
            raise

    except TimeoutException:
        print("Login button did not appear in time.")
        break

    

time.sleep(3)  # Wait for login to process
current_url = driver.current_url + 'not-gor'
driver.get(current_url)
time.sleep(3)  # Wait for login to process


# === Check for grades logic ===
courses = driver.find_elements(By.CSS_SELECTOR, "div[data-ng-repeat='tnotlarNote in birim.tnotlarNotes']")

for course in courses:
    try:
        # Only try if it contains at least one .row
        rows = course.find_elements(By.CLASS_NAME, "row")
        if not rows:
            print("⏭️ Skipping a non-course block (no .row found)")
            continue

        row = rows[0]  # the actual course data row

        # Extract course name
        course_name = row.find_element(By.CSS_SELECTOR, ".col-xs-3 p").text.strip()

        # Extract grade values
        grade_row = row.find_element(By.CSS_SELECTOR, ".col-xs-6 .row")
        grade_cells = grade_row.find_elements(By.CLASS_NAME, "ng-scope")
        grades = [cell.text.strip() for cell in grade_cells]

        print(f"{course_name} => {grades}")

    except Exception as e:
        print(f"❌ Error parsing a row: {e}")



# This is just a first version — refine it later

# === Cleanup ===



