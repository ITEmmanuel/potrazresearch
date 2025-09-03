import time
import os
import glob
import uuid
import shutil
import csv
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ---------------- CONFIG ----------------
EMAIL = os.getenv('ACADEMI_EMAIL', 'emmanuelfood76@gmail.com')
PASSWORD = os.getenv('ACADEMI_PASSWORD', 'kosa#1234')
FILE_PATH = "NetworkMonitoringandManagementSystem.docx"  # your file to upload
DOWNLOAD_DIR = os.path.abspath("downloads")  # folder where PDF will be saved
CSV_OUTPUT = os.path.abspath("results.csv")  # store extracted results
# -----------------------------------------

# Ensure downloads folder exists
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Configure Chrome to auto-download files
options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": DOWNLOAD_DIR,
    "download.prompt_for_download": False,
    "plugins.always_open_pdf_externally": True
}
options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def wait_for_download(path, timeout=180):
    """Wait until all .crdownload files are gone (download finished)."""
    end_time = time.time() + timeout
    while time.time() < end_time:
        if not glob.glob(os.path.join(path, "*.crdownload")):
            return True
        time.sleep(1)
    raise TimeoutError("Download did not complete in time.")

def generate_unique_name(original_name):
    """Generate a unique name using timestamp + short uuid"""
    base, ext = os.path.splitext(original_name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"{base}_{timestamp}_{unique_id}{ext}"

try:
    # Step 1: Open login page
    driver.get("https://academi.cx/login/")

    # Step 2: Enter login credentials
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "email")))
    driver.find_element(By.NAME, "email").send_keys(EMAIL)
    driver.find_element(By.NAME, "password").send_keys(PASSWORD + Keys.RETURN)

    # Step 3: Wait until dashboard loads
    WebDriverWait(driver, 20).until(EC.url_contains("/dashboard"))

    # Step 4: Upload document with unique name
    unique_file_name = generate_unique_name(os.path.basename(FILE_PATH))
    unique_file_path = os.path.join(os.path.dirname(FILE_PATH), unique_file_name)
    shutil.copy(FILE_PATH, unique_file_path)  # copy original with new unique name

    upload_input = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
    )
    upload_input.send_keys(os.path.abspath(unique_file_path))

    try:
        submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_btn.click()
    except:
        pass

    # Step 5: Loop through all uploaded documents and extract results
    print("⏳ Collecting results for all uploaded documents...")
    results_data = []

    documents = WebDriverWait(driver, 30).until(
        EC.presence_of_all_elements_located((By.XPATH, "//button[contains(., 'View Results')] | //a[contains(., 'View Results')]"))
    )

    for i in range(len(documents)):
        try:
            print(f"📄 Processing document {i+1}...")

            # Re-find buttons (DOM refresh issue)
            documents = driver.find_elements(By.XPATH, "//button[contains(., 'View Results')] | //a[contains(., 'View Results')]")
            documents[i].click()

            # Wait for modal
            modal = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'modal-content') or contains(., 'Results')]"))
            )

            # Extract details
            doc_name = driver.find_element(By.XPATH, "//b[contains(text(), 'Document Name:')]/parent::p").text
            word_count = driver.find_element(By.XPATH, "//b[contains(text(), 'Word Count:')]/parent::p").text
            ai_percentage = driver.find_element(By.XPATH, "//b[contains(text(), 'AI Percentage:')]/parent::p").text
            similarity_percentage = driver.find_element(By.XPATH, "//b[contains(text(), 'Similarity Percentage:')]/parent::p").text

            # Click "Download similarity report"
            similarity_download_btn = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Download similarity report')] | //a[contains(., 'Download similarity report')]"))
            )
            similarity_download_btn.click()

            # Wait for download
            wait_for_download(DOWNLOAD_DIR, timeout=180)

            # Rename file
            list_of_files = glob.glob(os.path.join(DOWNLOAD_DIR, "*.pdf"))
            latest_file = max(list_of_files, key=os.path.getctime)
            final_pdf_name = os.path.splitext(unique_file_name)[0] + "_similarity.pdf"
            final_pdf_path = os.path.join(DOWNLOAD_DIR, final_pdf_name)
            os.rename(latest_file, final_pdf_path)

            print(f"✅ Got results for {doc_name} → Similarity={similarity_percentage}, AI={ai_percentage}")

            results_data.append({
                "Unique Document": unique_file_name,
                "Word Count": word_count,
                "AI %": ai_percentage,
                "Similarity %": similarity_percentage,
                "Report File": final_pdf_path
            })

            # Close modal
            close_btn = driver.find_element(By.XPATH, "//button[contains(., '×')] | //span[contains(@class, 'close')]")
            close_btn.click()
            WebDriverWait(driver, 10).until(EC.invisibility_of_element(modal))

        except Exception as e:
            print(f"⚠️ Could not process document {i+1}: {e}")

    # Save results into CSV
    with open(CSV_OUTPUT, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Unique Document", "Word Count", "AI %", "Similarity %", "Report File"])
        writer.writeheader()
        writer.writerows(results_data)

    print(f"\n📊 Results saved in {CSV_OUTPUT}")

    # Step 9: Log out
    try:
        logout_link = driver.find_element(By.XPATH, "//a[contains(text(),'Sign Out') or contains(text(),'Log out')]")
        logout_link.click()
        print("👋 Logged out successfully!")
    except:
        print("⚠️ Could not find logout link.")

finally:
    time.sleep(5)
    driver.quit()
