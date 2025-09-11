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
        unique_path = None
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

            # Wait for upload to complete on academi.cx
            print("⏳ Waiting 50 seconds for document to fully upload to academi.cx...")
            time.sleep(50)
            
            print("✅ Document uploaded successfully!")
            return unique_name

        except Exception as e:
            print(f"❌ Upload failed: {str(e)}")
            return None
        finally:
            # Clean up temporary file with retry mechanism
            if unique_path and os.path.exists(unique_path):
                max_retries = 5
                for attempt in range(max_retries):
                    try:
                        os.remove(unique_path)
                        print(f"🧹 Cleaned up temporary file: {unique_name}")
                        break
                    except PermissionError:
                        if attempt < max_retries - 1:
                            print(f"⏳ File locked, retrying cleanup in {attempt + 1} seconds...")
                            time.sleep(attempt + 1)
                        else:
                            print(f"⚠️  Could not delete temporary file: {unique_path}")
                    except Exception as cleanup_error:
                        print(f"⚠️  Error during cleanup: {str(cleanup_error)}")
                        break

    def extract_results(self, document_name):
        """Extract plagiarism results by downloading PDF report only"""
        try:
            print("📊 Looking for results...")

            # Find all "View Results" buttons/links
            results_buttons = WebDriverWait(self.driver, 30).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//button[contains(., 'View Results')] | //a[contains(., 'View Results')]")
                )
            )

            if not results_buttons:
                print("⚠️  No results found yet. Document may still be processing.")
                return None

            print(f"📋 Found {len(results_buttons)} result(s), clicking the first one...")
            
            # Click the first (most recent) result
            results_buttons[0].click()

            # Wait for modal to open
            print("⏳ Waiting for results modal to open...")
            modal = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[contains(@class, 'modal') or contains(., 'Results')]")
                )
            )
            
            # Wait a moment for modal content to load
            time.sleep(2)

            # Look for and click the download similarity report button
            print("🔍 Looking for download similarity report button...")
            try:
                download_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(., 'Download similarity report')] | //a[contains(., 'Download similarity report')]")
                    )
                )
                
                print("📥 Clicking download similarity report button...")
                download_btn.click()

                # Wait for download to complete
                print("⏳ Waiting for PDF download to complete...")
                self.wait_for_download(timeout=60)

                # Find the downloaded PDF and rename it
                pdf_files = glob.glob(os.path.join(self.download_dir, "*.pdf"))
                if pdf_files:
                    latest_pdf = max(pdf_files, key=os.path.getctime)
                    report_name = os.path.splitext(document_name)[0] + "_similarity_report.pdf"
                    report_path = os.path.join(self.download_dir, report_name)
                    
                    # Rename with retry mechanism
                    max_retries = 3
                    for attempt in range(max_retries):
                        try:
                            os.rename(latest_pdf, report_path)
                            break
                        except PermissionError:
                            if attempt < max_retries - 1:
                                time.sleep(2)
                            else:
                                # Use original filename if rename fails
                                report_path = latest_pdf
                    
                    # Create minimal results with just the PDF
                    results = {
                        'document_name': document_name,
                        'processed_at': datetime.utcnow(),
                        'report_path': report_path
                    }
                    
                    print(f"✅ PDF report downloaded successfully: {os.path.basename(report_path)}")
                    
                    # Close modal
                    try:
                        close_btn = self.driver.find_element(
                            By.XPATH, "//button[contains(., '×')] | //span[contains(@class, 'close')] | //button[@data-dismiss='modal']"
                        )
                        close_btn.click()
                        time.sleep(1)
                    except:
                        # Try pressing Escape key as fallback
                        try:
                            from selenium.webdriver.common.keys import Keys
                            self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                        except:
                            pass
                    
                    return results
                else:
                    print("❌ No PDF file found after download")
                    return None

            except Exception as download_error:
                print(f"❌ Could not download report: {str(download_error)}")
                return None

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
                        document.error_message = 'Failed to login to academi.cx'
                        db.session.commit()
                        return False

                # Check if document was already uploaded to academi.cx
                if not document.academi_uploaded:
                    print("📤 Uploading document to academi.cx...")
                    uploaded_name = self.upload_document(document.path)
                    if not uploaded_name:
                        document.status = 'failed'
                        document.error_message = 'Failed to upload document to academi.cx'
                        db.session.commit()
                        return False
                    
                    # Mark as uploaded and save timestamp
                    document.academi_uploaded = True
                    document.academi_upload_time = datetime.utcnow()
                    db.session.commit()
                    print("✅ Document uploaded successfully to academi.cx")
                    
                    # Initial wait after upload - academi.cx needs time to process the upload
                    print("⏳ Waiting for initial processing on academi.cx...")
                    time.sleep(30)
                else:
                    print("ℹ️  Document already uploaded to academi.cx, checking for results...")

                # Try to extract results (retry mechanism for waiting)
                max_retries = 40  # Increased for 500-700 second wait time
                wait_time = 15    # Check every 15 seconds
                
                for attempt in range(max_retries):
                    elapsed_time = attempt * wait_time
                    print(f"🔄 Attempt {attempt + 1}/{max_retries} to extract results... (elapsed: {elapsed_time}s)")
                    
                    results = self.extract_results(document.original_filename)

                    if results:
                        # Update document with results
                        document.status = 'completed'
                        document.processed_at = results['processed_at']

                        # Only store what we have from the PDF download
                        document.similarity_score = 0.0
                        document.ai_percentage = 0.0
                        document.word_count = 0

                        # Store report path if available
                        if 'report_path' in results:
                            # Store relative path for web access
                            document.report_path = os.path.basename(results['report_path'])

                        db.session.commit()
                        print(f"✅ Document processing completed successfully!")
                        return True

                    # Wait before retry
                    print(f"⏳ Results not ready yet, waiting {wait_time} seconds...")
                    time.sleep(wait_time)

                # If we get here, processing timed out
                print("❌ Document processing timed out after maximum retries")
                document.status = 'failed'
                document.error_message = 'Processing timed out - results not available after maximum wait time'
                db.session.commit()
                return False

            except Exception as e:
                print(f"❌ Error processing document: {str(e)}")
                try:
                    document.status = 'failed'
                    document.error_message = str(e)
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
    app = create_app()
    
    with app.app_context():
        try:
            # Check if credentials are set
            if not os.getenv('ACADEMI_EMAIL') or not os.getenv('ACADEMI_PASSWORD'):
                print("❌ ACADEMI_EMAIL and ACADEMI_PASSWORD environment variables not set")
                document = Document.query.get(document_id)
                if document:
                    document.status = 'failed'
                    db.session.commit()
                return False
                
            processor = DocumentProcessor()
            success = processor.process_document(document_id)
            return success
        except Exception as e:
            print(f"❌ Background processing error: {str(e)}")
            # Update document status to failed
            try:
                document = Document.query.get(document_id)
                if document:
                    document.status = 'failed'
                    db.session.commit()
            except:
                pass
            return False
        finally:
            try:
                processor.cleanup()
            except:
                pass

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

