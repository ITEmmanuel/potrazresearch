#!/usr/bin/env python3
"""
Document Processing Module - Integrates main.py logic with Flask app
"""

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

# Import Flask components for database access
from .models import db, Document
from . import create_app

class DocumentProcessor:
    """Handles document processing via academi.cx using Selenium"""

    def __init__(self, email=None, password=None):
        """Initialize the document processor"""
        self.email = email or os.getenv('ACADEMI_EMAIL')
        self.password = password or os.getenv('ACADEMI_PASSWORD')
        
        if not self.email or not self.password:
            raise ValueError("ACADEMI_EMAIL and ACADEMI_PASSWORD environment variables must be set")
        self.download_dir = os.path.abspath("downloads")
        self.driver = None

        # Ensure download directory exists
        os.makedirs(self.download_dir, exist_ok=True)

    def setup_driver(self):
        """Setup Chrome WebDriver with download preferences"""
        options = webdriver.ChromeOptions()

        # Configure Chrome for headless operation in production
        if os.getenv('FLASK_ENV') == 'production':
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')

        # Download preferences
        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "plugins.always_open_pdf_externally": True,
            "download.directory_upgrade": True
        }
        options.add_experimental_option("prefs", prefs)

        # Additional options for stability
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        # Execute script to remove webdriver property
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        return self.driver

    def login(self):
        """Login to academi.cx"""
        if not self.driver:
            self.setup_driver()

        try:
            print("🔐 Logging into academi.cx...")
            self.driver.get("https://academi.cx/login/")

            # Wait for email field and enter credentials
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )

            email_field = self.driver.find_element(By.NAME, "email")
            password_field = self.driver.find_element(By.NAME, "password")

            email_field.clear()
            email_field.send_keys(self.email)
            password_field.clear()
            password_field.send_keys(self.password + Keys.RETURN)

            # Wait for dashboard to load
            WebDriverWait(self.driver, 30).until(
                EC.url_contains("/dashboard")
            )

            print("✅ Successfully logged in!")
            return True

        except Exception as e:
            print(f"❌ Login failed: {str(e)}")
            return False

    def wait_for_download(self, timeout=180):
        """Wait until download completes"""
        end_time = time.time() + timeout
        while time.time() < end_time:
            if not glob.glob(os.path.join(self.download_dir, "*.crdownload")):
                return True
            time.sleep(1)
        raise TimeoutError("Download did not complete in time.")

    def generate_unique_name(self, original_name):
        """Generate unique filename"""
        base, ext = os.path.splitext(original_name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"{base}_{timestamp}_{unique_id}{ext}"

    def upload_document(self, file_path):
        """Upload a document to academi.cx"""
        try:
            print(f"📤 Uploading document: {os.path.basename(file_path)}")

            # Generate unique name to avoid conflicts
            unique_name = self.generate_unique_name(os.path.basename(file_path))
            unique_path = os.path.join(os.path.dirname(file_path), unique_name)

            # Copy file with unique name
            shutil.copy(file_path, unique_path)

            # Find and interact with file input
            upload_input = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
            )

            upload_input.send_keys(os.path.abspath(unique_path))

            # Try to submit (some sites auto-submit, others need manual submit)
            try:
                submit_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
                submit_btn.click()
            except:
                print("ℹ️  Upload appears to be automatic or submit button not found")

            print("✅ Document uploaded successfully!")
            return unique_name

        except Exception as e:
            print(f"❌ Upload failed: {str(e)}")
            return None
        finally:
            # Clean up temporary file
            if os.path.exists(unique_path):
                os.remove(unique_path)

    def extract_results(self, document_name):
        """Extract plagiarism results from the current page"""
        try:
            print("📊 Extracting results...")

            # Find all "View Results" buttons/links
            results_buttons = WebDriverWait(self.driver, 30).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//button[contains(., 'View Results')] | //a[contains(., 'View Results')]")
                )
            )

            if not results_buttons:
                print("⚠️  No results found yet. Document may still be processing.")
                return None

            # Click the first (most recent) result
            results_buttons[0].click()

            # Wait for modal/results page
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[contains(@class, 'modal-content') or contains(., 'Results')]")
                )
            )

            # Extract document details
            try:
                doc_name_element = self.driver.find_element(
                    By.XPATH, "//b[contains(text(), 'Document Name:')]/parent::p"
                )
                doc_name = doc_name_element.text.replace('Document Name:', '').strip()
            except:
                doc_name = document_name

            try:
                word_count_element = self.driver.find_element(
                    By.XPATH, "//b[contains(text(), 'Word Count:')]/parent::p"
                )
                word_count = word_count_element.text.replace('Word Count:', '').strip()
            except:
                word_count = "N/A"

            try:
                ai_percentage_element = self.driver.find_element(
                    By.XPATH, "//b[contains(text(), 'AI Percentage:')]/parent::p"
                )
                ai_percentage = ai_percentage_element.text.replace('AI Percentage:', '').strip()
            except:
                ai_percentage = "0%"

            try:
                similarity_percentage_element = self.driver.find_element(
                    By.XPATH, "//b[contains(text(), 'Similarity Percentage:')]/parent::p"
                )
                similarity_percentage = similarity_percentage_element.text.replace('Similarity Percentage:', '').strip()
            except:
                similarity_percentage = "0%"

            results = {
                'document_name': doc_name,
                'word_count': word_count,
                'ai_percentage': ai_percentage,
                'similarity_percentage': similarity_percentage,
                'processed_at': datetime.utcnow()
            }

            print(f"✅ Results extracted: Similarity={similarity_percentage}, AI={ai_percentage}")

            # Try to download similarity report
            try:
                download_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(., 'Download similarity report')] | //a[contains(., 'Download similarity report')]")
                    )
                )
                download_btn.click()

                # Wait for download
                self.wait_for_download(timeout=60)

                # Find the downloaded PDF and rename it
                pdf_files = glob.glob(os.path.join(self.download_dir, "*.pdf"))
                if pdf_files:
                    latest_pdf = max(pdf_files, key=os.path.getctime)
                    report_name = os.path.splitext(document_name)[0] + "_similarity_report.pdf"
                    report_path = os.path.join(self.download_dir, report_name)
                    os.rename(latest_pdf, report_path)
                    results['report_path'] = report_path
                    print(f"✅ Report downloaded: {report_name}")

            except Exception as e:
                print(f"⚠️  Could not download report: {str(e)}")

            # Close modal
            try:
                close_btn = self.driver.find_element(
                    By.XPATH, "//button[contains(., '×')] | //span[contains(@class, 'close')]"
                )
                close_btn.click()
                WebDriverWait(self.driver, 5).until(
                    EC.invisibility_of_element_located(
                        (By.XPATH, "//div[contains(@class, 'modal-content')]")
                    )
                )
            except:
                pass

            return results

        except Exception as e:
            print(f"❌ Error extracting results: {str(e)}")
            return None

    def process_document(self, document_id):
        """Process a single document by ID"""
        app = create_app()

        with app.app_context():
            try:
                # Get document from database
                document = Document.query.get(document_id)
                if not document:
                    print(f"❌ Document {document_id} not found")
                    return False

                print(f"🚀 Starting processing for document: {document.original_filename}")

                # Update status to processing
                document.status = 'processing'
                db.session.commit()

                # Setup browser and login
                if not self.driver:
                    if not self.login():
                        document.status = 'failed'
                        db.session.commit()
                        return False

                # Upload the document
                uploaded_name = self.upload_document(document.path)
                if not uploaded_name:
                    document.status = 'failed'
                    db.session.commit()
                    return False

                # Wait for processing (this might take time)
                print("⏳ Waiting for document processing...")
                time.sleep(30)  # Initial wait

                # Try to extract results (retry a few times)
                max_retries = 10
                for attempt in range(max_retries):
                    print(f"🔄 Attempt {attempt + 1}/{max_retries} to extract results...")
                    results = self.extract_results(uploaded_name)

                    if results:
                        # Update document with results
                        document.status = 'completed'
                        document.processed_at = results['processed_at']

                        # Store similarity score (extract number from percentage)
                        try:
                            similarity_str = results['similarity_percentage'].replace('%', '')
                            document.similarity_score = float(similarity_str)
                        except:
                            document.similarity_score = 0.0

                        # Store report path if available
                        if 'report_path' in results:
                            # Store relative path for web access
                            document.report_path = os.path.basename(results['report_path'])

                        db.session.commit()
                        print(f"✅ Document processing completed successfully!")
                        return True

                    # Wait before retry
                    time.sleep(15)

                # If we get here, processing failed
                print("❌ Document processing timed out")
                document.status = 'failed'
                db.session.commit()
                return False

            except Exception as e:
                print(f"❌ Error processing document: {str(e)}")
                try:
                    document.status = 'failed'
                    db.session.commit()
                except:
                    pass
                return False

    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            try:
                # Try to logout
                try:
                    logout_link = self.driver.find_element(
                        By.XPATH, "//a[contains(text(),'Sign Out') or contains(text(),'Log out')]"
                    )
                    logout_link.click()
                    print("👋 Logged out successfully!")
                except:
                    print("⚠️  Could not find logout link.")

                time.sleep(2)
                self.driver.quit()
                self.driver = None
                print("🧹 Browser cleanup completed")

            except Exception as e:
                print(f"⚠️  Error during cleanup: {str(e)}")

def process_document_background(document_id):
    """Background function to process a document - can be called from Flask routes"""
    processor = DocumentProcessor()

    try:
        success = processor.process_document(document_id)
        return success
    finally:
        processor.cleanup()

# For standalone testing
if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        print("Usage: python document_processor.py <document_id>")
        sys.exit(1)

    document_id = int(sys.argv[1])
    success = process_document_background(document_id)

    if success:
        print(f"✅ Document {document_id} processed successfully!")
        sys.exit(0)
    else:
        print(f"❌ Document {document_id} processing failed!")
        sys.exit(1)

