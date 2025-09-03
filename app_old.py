from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
                
                # Wait for email field and enter credentials
                try:
                    print("🔑 Entering credentials...")
                    email_field = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.NAME, "email"))
                    )
                    email_field.clear()
                    email_field.send_keys(EMAIL)
                    
                    # Enter password and submit
                    password_field = driver.find_element(By.NAME, "password")
                    password_field.clear()
                    password_field.send_keys(PASSWORD)
                    
                    # Try to find and click the submit button
                    try:
                        submit_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'], input[type='submit']"))
                        )
                        submit_button.click()
                        print("✅ Submitted login form")
                    except Exception as btn_error:
                        print(f"⚠️ Could not find submit button, pressing Enter: {str(btn_error)}")
                        password_field.send_keys(Keys.RETURN)
                    
                    # Wait for either successful login or error message
                    try:
                        # Check for login error message
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'),'invalid') or contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'),'login failed')]"))
                        )
                        error_text = driver.find_element(By.XPATH, "//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'),'invalid') or contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'),'login failed')]").text
                        print(f"❌ Login failed: {error_text}")
                        return False
                    except:
                        # If no error message, check for successful login
                        WebDriverWait(driver, 20).until(EC.url_contains("dashboard"))
                        print("✅ Successfully logged in")
                        return True
                        
                except Exception as e:
                    print(f"❌ Error during login process: {str(e)}")
                    driver.save_screenshot('login_error.png')
                    print("📸 Saved screenshot: login_error.png")
                    return False
                    
            except Exception as e:
                print(f"Login error: {str(e)}")
                # Take screenshot for debugging
                try:
                    screenshot_path = os.path.join('static', 'login_error.png')
                    driver.save_screenshot(screenshot_path)
                    print(f"Screenshot saved to {screenshot_path}")
                except Exception as screenshot_error:
                    print(f"Failed to take screenshot: {str(screenshot_error)}")
                return False
        
        def safe_find_and_click(by, value, max_retries=2):
            for attempt in range(max_retries):
                try:
                    element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((by, value)))
                    element.click()
                    return element
                except Exception as e:
                    if attempt < max_retries - 1:
                        if not login():
                            raise Exception("Failed to login after multiple attempts")
                        continue
                    raise

        # First check if we can even login
        login_attempts = 0
        max_login_attempts = 2
        
        while login_attempts < max_login_attempts:
            if login():
                break
            login_attempts += 1
            print(f"Login attempt {login_attempts} failed. Retrying...")
            time.sleep(2)  # Wait before retry
        else:
            raise Exception("Unable to login to the service. Please check your credentials and try again.")

        # Check for limit reached message on dashboard
        try:
            limit_elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//*[contains(., 'limit') or contains(., 'quota') or contains(., 'exceeded')]")
                )
            )
            if any('limit' in el.text.lower() or 'quota' in el.text.lower() or 'exceeded' in el.text.lower() for el in limit_elements):
                raise Exception("Limit reached. Please try again later.")
        except:
            pass  # No limit message found, continue

        # Step 1: Upload file with unique name
        unique_file_name = generate_unique_name(os.path.basename(file_path))
        unique_file_path = os.path.join(os.path.dirname(file_path), unique_file_name)
        shutil.copy(file_path, unique_file_path)

        # Upload the file
        try:
            print("🔍 Looking for file upload input...")
            # Take a screenshot before looking for the upload input
            driver.save_screenshot('before_upload.png')
            print("📸 Took screenshot: before_upload.png")
            
            # Try different selectors for the file input
            upload_selectors = [
                "input[type='file']",
                "input[accept*='.doc']",
                "input[accept*='.docx']",
                "input[accept*='.pdf']",
                "input[accept*='document']",
                "//input[@type='file']"
            ]
            
            upload_input = None
            for selector in upload_selectors:
                try:
                    upload_input = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR if '//' not in selector else By.XPATH, selector))
                    )
                    print(f"✅ Found upload input with selector: {selector}")
                    break
                except:
                    continue
            
            if not upload_input:
                raise Exception("Could not find file upload input on the page")
            
            # Make the input visible if it's hidden
            driver.execute_script("arguments[0].style.display = 'block';", upload_input)
            driver.execute_script("arguments[0].style.visibility = 'visible';", upload_input)
            driver.execute_script("arguments[0].style.opacity = 1;", upload_input)
            
            print(f"📤 Uploading file: {os.path.abspath(unique_file_path)}")
            upload_input.send_keys(os.path.abspath(unique_file_path))
            print("✅ File selected for upload")
            
            # Wait for the upload to complete and results to appear
            print("⏳ Waiting for processing to complete (this may take up to 2 minutes)...")
            
            # Wait for the processing to start
            time.sleep(10)
            
            # Wait for up to 2 minutes for processing to complete
            max_wait = 120  # 2 minutes max
            start_time = time.time()
            processing_complete = False
            
            while time.time() - start_time < max_wait:
                # Check for completion indicators
                try:
                    # Look for any completion indicators
                    complete_indicators = [
                        "Your document is being processed",
                        "Processing complete",
                        "Results ready",
                        "View Results",
                        "Similarity"
                    ]
                    
                    # Check page source for any indicators
                    page_source = driver.page_source.lower()
                    if any(indicator.lower() in page_source for indicator in complete_indicators):
                        print("✅ Processing complete indicator found")
                        processing_complete = True
                        break
                        
                    # Also check for any progress bars or loading indicators
                    loading_elements = driver.find_elements(
                        By.XPATH, 
                        "//*[contains(@class, 'progress') or contains(@class, 'loading') or contains(@class, 'spinner')]"
                    )
                    
                    if not loading_elements:
                        print("✅ No loading indicators found, assuming processing is complete")
                        processing_complete = True
                        break
                        
                    print(f"⏳ Still processing... ({int(time.time() - start_time)}s elapsed)")
                    time.sleep(5)  # Check every 5 seconds
                    
                except Exception as e:
                    print(f"⚠️ Error while checking processing status: {str(e)}")
                    time.sleep(5)
            
            if not processing_complete:
                print("⚠️ Processing took too long, continuing anyway")
            
            # Look for either results or error messages
            print("🔍 Looking for results or error messages...")
            
            # Take a screenshot after upload
            driver.save_screenshot('after_upload.png')
            print("📸 Took screenshot: after_upload.png")
            
            # Check for common error messages
            error_messages = [
                "error", "failed", "limit", "quota", "exceeded",
                "try again", "something went wrong"
            ]
            
            try:
                # Look for any error messages
                error_elements = driver.find_elements(
                    By.XPATH, 
                    "//*[contains(translate(., 'ERROR', 'error'), 'error') or "
                    "contains(translate(., 'FAILED', 'failed'), 'failed') or "
                    "contains(., 'limit') or contains(., 'quota') or "
                    "contains(., 'exceeded') or contains(., 'try again') or "
                    "contains(., 'something went wrong')]"
                )
                
                for element in error_elements:
                    if element.is_displayed() and element.text.strip():
                        error_text = element.text.strip()
                        if any(msg in error_text.lower() for msg in error_messages):
                            print(f"❌ Error detected: {error_text}")
                            raise Exception(f"Upload failed: {error_text}")
            except Exception as e:
                print(f"⚠️ Error while checking for error messages: {str(e)}")
            
            print("✅ File upload and processing appears successful")
            
        except Exception as e:
            driver.save_screenshot('upload_error.png')
            print(f"❌ Error during file upload: {str(e)}")
            print("📸 Saved screenshot: upload_error.png")
            raise Exception(f"Failed to upload file: {str(e)}. Please check the screenshots for more details.")

        # Step 2: Handle the results page
        try:
            print("🔍 Looking for results or view buttons...")
            
            # Take a screenshot of the results page
            driver.save_screenshot('results_page.png')
            print("📸 Took screenshot: results_page.png")
            
            # Wait for the results to be ready (up to 400 seconds)
            print("⏳ Waiting for results to be ready (this may take up to 7 minutes)...")
            max_wait = 400  # ~6.5 minutes
            start_time = time.time()
            results_found = False
            
            while time.time() - start_time < max_wait and not results_found:
                # Look for the "View Results" button or similar
                view_results_selectors = [
                    "//button[contains(., 'View Results')]",
                    "//a[contains(., 'View Results')]",
                    "//button[contains(., 'View Report')]",
                    "//a[contains(., 'View Report')]"
                ]
                
                for selector in view_results_selectors:
                    try:
                        view_btn = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        if view_btn.is_displayed():
                            print(f"✅ Found results button with selector: {selector}")
                            safe_click(driver, view_btn)
                            print("✅ Clicked view results button")
                            results_found = True
                            break
                    except:
                        continue
                
                if results_found:
                    break
                    
                # Check if we're already on the results page
                if "results" in driver.current_url.lower() or "report" in driver.current_url.lower():
                    print("✅ Already on results page")
                    results_found = True
                    break
                    
                print(f"⏳ Still waiting for results... ({int(time.time() - start_time)}s elapsed)")
                time.sleep(5)  # Check every 5 seconds
            
            if not results_found:
                print("⚠️ Results not found after waiting, continuing with current page")
            
            # Take a screenshot of the final page
            driver.save_screenshot('final_results_page.png')
            print("📸 Took screenshot: final_results_page.png")
            
            # After clicking View Results, look for Download Similarity Report button
            print("🔍 Looking for Download Similarity Report button...")
            download_clicked = False
            download_selectors = [
                "//button[contains(., 'Download Similarity Report')]",
                "//a[contains(., 'Download Similarity Report')]",
                "//button[contains(., 'Download') and contains(., 'Report')]",
                "//a[contains(., 'Download') and contains(., 'Report')]"
            ]
            
            for selector in download_selectors:
                try:
                    download_btn = WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    if download_btn.is_displayed():
                        print(f"✅ Found download button with selector: {selector}")
                        safe_click(driver, download_btn)
                        print("✅ Clicked download button")
                        download_clicked = True
                        break
                except:
                    continue
            
            if not download_clicked:
                print("⚠️ Could not find download button, continuing...")
            
            # Wait for download to complete
            time.sleep(5)
            
            # Get the downloaded file
            download_dir = os.path.expanduser("~/Downloads")
            files = glob.glob(os.path.join(download_dir, "*similarity*.pdf")) + \
                    glob.glob(os.path.join(download_dir, "*report*.pdf")) + \
                    glob.glob(os.path.join(download_dir, "*plagiarism*.pdf"))
            
            report_path = None
            if files:
                latest_file = max(files, key=os.path.getctime)
                print(f"✅ Found downloaded report: {latest_file}")
                
                # Save to our downloads directory
                if not os.path.exists(DOWNLOAD_DIR):
                    os.makedirs(DOWNLOAD_DIR)
                
                dest_filename = f"similarity_report_{int(time.time())}.pdf"
                report_path = os.path.join(DOWNLOAD_DIR, dest_filename)
                shutil.copy2(latest_file, report_path)
                print(f"✅ Saved report to: {report_path}")
            
            # Logout
            try:
                print("🔒 Logging out...")
                # Look for user menu and logout button
                user_menu = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'user-menu') or contains(@class, 'profile')]"))
                )
                safe_click(driver, user_menu)
                
                logout_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//*[contains(., 'Logout') or contains(., 'Sign out')]"))
                )
                safe_click(driver, logout_btn)
                print("✅ Successfully logged out")
            except Exception as e:
                print(f"⚠️ Could not log out: {str(e)}")
            
            result = {
                'status': 'success',
                'report_path': report_path,
                'result_url': driver.current_url,
                'screenshot': 'final_results_page.png'
            }
            print(f"✅ Processing complete. Result: {result}")
            return result
        except Exception as e:
            if 'limit' in str(e).lower() or 'quota' in str(e).lower() or 'exceeded' in str(e).lower():
                raise Exception("Limit reached. Please try again later.")
            # If it's not a limit error, check one more time for limit messages
            try:
                limit_elements = driver.find_elements(
                    By.XPATH, 
                    "//*[contains(., 'limit') or contains(., 'quota') or contains(., 'exceeded')]"
                )
                if limit_elements and any('limit' in el.text.lower() or 'quota' in el.text.lower() or 'exceeded' in el.text.lower() for el in limit_elements):
                    raise Exception("Limit reached. Please try again later.")
            except:
                pass
            raise

        for i in range(len(documents)):
            print(f"📄 Processing document {i+1}...")

            try:
                documents = driver.find_elements(
                    By.XPATH, "//button[contains(., 'View Results')] | //a[contains(., 'View Results')]"
                )
                if i >= len(documents):
                    break
                safe_find_and_click(By.XPATH, f"(//button[contains(., 'View Results')] | //a[contains(., 'View Results')])[{i+1}]")
            except Exception as e:
                if "stale element" in str(e).lower():
                    login()
                    continue
                raise

            # Step 4: Wait for modal with limit check
            try:
                modal = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//div[contains(@class, 'modal-content') or contains(., 'Results')]")
                    )
                )
            except:
                # Check if limit reached message is shown in modal
                limit_elements = driver.find_elements(By.XPATH, "//*[contains(., 'limit reached') or contains(., 'limit exceeded') or contains(., 'quota')]")
                if limit_elements:
                    raise Exception("Limit reached. Please try again later.")
                raise

            # Step 5: Extract results
            doc_name = driver.find_element(By.XPATH, "//b[contains(text(), 'Document Name:')]/parent::p").text
            word_count = driver.find_element(By.XPATH, "//b[contains(text(), 'Word Count:')]/parent::p").text
            ai_percentage = driver.find_element(By.XPATH, "//b[contains(text(), 'AI Percentage:')]/parent::p").text
            similarity_percentage = driver.find_element(By.XPATH, "//b[contains(text(), 'Similarity Percentage:')]/parent::p").text

            # Step 6: Download similarity report
            similarity_download_btn = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(., 'Download similarity report')] | //a[contains(., 'Download similarity report')]")
                )
            )
            safe_click(driver, similarity_download_btn)

            wait_for_download(DOWNLOAD_DIR, timeout=180)

            # Rename PDF
            list_of_files = glob.glob(os.path.join(DOWNLOAD_DIR, "*.pdf"))
            latest_file = max(list_of_files, key=os.path.getctime)
            final_pdf_name = os.path.splitext(unique_file_name)[0] + "_similarity.pdf"
            final_pdf_path = os.path.join(DOWNLOAD_DIR, final_pdf_name)
            os.rename(latest_file, final_pdf_path)

            results_data.append({
                "Unique Document": unique_file_name,
                "Word Count": word_count,
                "AI %": ai_percentage,
                "Similarity %": similarity_percentage,
                "Report File": final_pdf_path
            })

            # Close modal
            close_btn = driver.find_element(
                By.XPATH, "//button[contains(., '×')] | //span[contains(@class, 'close')]"
            )
            safe_click(driver, close_btn)
            WebDriverWait(driver, 10).until(EC.invisibility_of_element(modal))

        # Save results
        with open(CSV_OUTPUT, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["Unique Document", "Word Count", "AI %", "Similarity %", "Report File"]
            )
            writer.writeheader()
            writer.writerows(results_data)

        return results_data

    except Exception as e:
        error_msg = str(e).lower()
        print(f"Error in process_document: {error_msg}")
        
        # Check for limit-related errors
        if any(term in error_msg for term in ['limit', 'quota', 'exceeded']):
            raise Exception("Limit reached. Please try again later or contact support if this continues.")
        else:
            raise Exception("An error occurred while processing the document. Please try again later.")
    finally:
        try:
            if driver:
                driver.quit()
        except Exception as e:
            print(f"Error during driver cleanup: {str(e)}")
        time.sleep(2)  # Short delay to ensure resources are released

def get_documents():
    """Get list of uploaded documents with their status"""
    documents = []
    upload_dir = os.path.abspath(app.config['UPLOAD_FOLDER'])
    
    # Check if documents.json exists and load it
    docs_file = os.path.join(os.path.dirname(upload_dir), 'documents.json')
    
    # If documents.json doesn't exist, create it
    if not os.path.exists(docs_file):
        with open(docs_file, 'w') as f:
            json.dump([], f, indent=2)
    
    try:
        # Load existing documents
        with open(docs_file, 'r') as f:
            documents = json.load(f)
        
        # Get list of all files in uploads directory
        existing_files = {}
        for filename in os.listdir(upload_dir):
            if filename.endswith(('.doc', '.docx', '.pdf')):
                file_path = os.path.join(upload_dir, filename)
                base_name = os.path.splitext(filename)[0]
                existing_files[base_name] = {
                    'filename': filename,
                    'path': file_path,
                    'timestamp': datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S'),
                    'status': 'completed'  # Default status
                }
        
        # Update status from status files
        status_dir = os.path.join(os.path.dirname(upload_dir), 'status')
        if os.path.exists(status_dir):
            for status_file in os.listdir(status_dir):
                if status_file.endswith('.status'):
                    base_name = status_file.replace('.status', '')
                    if base_name in existing_files:
                        try:
                            with open(os.path.join(status_dir, status_file), 'r') as f:
                                existing_files[base_name]['status'] = f.read().strip()
                        except Exception as e:
                            print(f"Error reading status file {status_file}: {str(e)}")
        
        # Update documents list with existing files
        updated_documents = []
        for doc in documents:
            if os.path.exists(doc.get('path', '')):
                base_name = os.path.splitext(os.path.basename(doc['path']))[0]
                if base_name in existing_files:
                    # Update existing document with any new status
                    doc.update(existing_files[base_name])
                    updated_documents.append(doc)
                    del existing_files[base_name]
        
        # Add any new files that weren't in the documents list
        for file_info in existing_files.values():
            updated_documents.append(file_info)
        
        # Save the updated documents back
        with open(docs_file, 'w') as f:
            json.dump(updated_documents, f, indent=2)
        
        return updated_documents
        
    except Exception as e:
        print(f"Error loading documents: {str(e)}")
        return []

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            # Check if file was uploaded
            if 'file' not in request.files:
                return jsonify({"status": "error", "message": "No file part"}), 400
            
            file = request.files['file']
            
            # Check if file was selected
            if file.filename == '':
                return jsonify({"status": "error", "message": "No selected file"}), 400
            
            # Check file extension
            if not allowed_file(file.filename):
                return jsonify({"status": "error", "message": "File type not allowed"}), 400
            
            # Create necessary directories
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            status_dir = os.path.join(os.path.dirname(app.config['UPLOAD_FOLDER']), 'status')
            os.makedirs(status_dir, exist_ok=True)
            os.makedirs(DOWNLOADS_DIR, exist_ok=True)
            
            # Generate unique filename and paths
            filename = secure_filename(file.filename)
            unique_filename = generate_unique_name(filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            status_file = os.path.join(status_dir, f"{os.path.splitext(unique_filename)[0]}.status")
            
            # Save the uploaded file
            file.save(file_path)
            
            # Mark as processing
            with open(status_file, 'w') as f:
                f.write('processing')
            
            try:
                # Process the document
                result = process_document(file_path)
                
                if not result or not isinstance(result, dict) or result.get('status') != 'success':
                    raise Exception(result.get('message', 'Failed to process document'))
                
                # Update status to completed
                with open(status_file, 'w') as f:
                    f.write('completed')
                
                # Verify report exists
                if not result.get('report_path') or not os.path.exists(result['report_path']):
                    raise Exception("Report file not found after processing")
                
                # Update documents list
                documents = get_documents()
                document_data = {
                    'filename': filename,
                    'path': file_path,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'result_url': result.get('result_url', ''),
                    'report_path': result.get('report_path', ''),
                    'status': 'completed'
                }
                documents.insert(0, document_data)
                save_documents(documents)
                
                # Return appropriate response
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'status': 'success',
                        'message': 'Document processed successfully!',
                        'result_url': url_for('download_file', 
                                          filename=os.path.basename(result['report_path']))
                    })
                
                return render_template('index.html', 
                                    documents=documents,
                                    success='Document processed successfully!')
                
            except Exception as e:
                # Mark as failed
                with open(status_file, 'w') as f:
                    f.write('failed')
                
                error_msg = str(e).lower()
                if 'limit' in error_msg or 'quota' in error_msg:
                    return jsonify({
                        'status': 'error', 
                        'message': 'Limit reached. Please try again later.'
                    }), 500
                
                return jsonify({
                    'status': 'error',
                    'message': f'Failed to process document: {str(e)}'
                }), 500
                
        except Exception as e:
            print(f"Error in index route: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f'An unexpected error occurred: {str(e)}'
            }), 500
    
    # Handle GET request
    try:
        documents = get_documents()
        return render_template("index.html", documents=documents)
    except Exception as e:
        print(f"Error loading documents: {str(e)}")
        return render_template("index.html", documents=[])

@app.route("/download/<path:filename>")
def download_file(filename):
    return send_file(filename, as_attachment=True)

# ---------------- MAIN ----------------
if __name__ == "__main__":
    app.run(debug=True)
