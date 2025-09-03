# POTPLAG API Documentation

## Overview

POTPLAG is a Flask-based plagiarism detection system that integrates with academi.cx to provide comprehensive document analysis and similarity checking.

## Architecture

### System Components

1. **Flask Web Application**: Core web interface
2. **SQLAlchemy Database**: User and document management
3. **Selenium Automation**: Integration with academi.cx
4. **Background Processing**: Document analysis pipeline
5. **File Management**: Secure upload and download handling

### Technology Stack

- **Backend**: Flask 2.3.3 with Python 3.x
- **Database**: SQLAlchemy (supports MySQL/SQLite)
- **Frontend**: Bootstrap 5, JavaScript, HTML5
- **Automation**: Selenium WebDriver with Chrome
- **Security**: Flask-Login, Flask-WTF, Werkzeug

## Authentication System

### User Management

#### User Model
```python
class User(db.Model):
    id: Integer (Primary Key)
    username: String(80) (Unique, Indexed)
    email: String(120) (Unique, Indexed) 
    password_hash: String(128)
    is_active: Boolean (Default: True)
    is_admin: Boolean (Default: False)
    created_at: DateTime
    last_login: DateTime
    documents: Relationship to Document model
```

#### Authentication Endpoints

##### POST /register
Register a new user account.

**Request Body:**
```json
{
    "username": "string",
    "email": "string",
    "password": "string",
    "confirm_password": "string"
}
```

**Response:**
- Success: Redirect to login page
- Error: Form validation errors

**Business Logic:**
- New users are created as inactive
- Admin approval required for activation
- Username and email must be unique

##### POST /login
Authenticate user and create session.

**Request Body:**
```json
{
    "email": "string",
    "password": "string",
    "remember_me": "boolean"
}
```

**Response:**
- Success: Redirect to dashboard
- Error: Invalid credentials message

**Security Features:**
- Password hashing with Werkzeug
- Account activation check
- Session management

##### GET /logout
End user session and logout.

**Response:**
- Redirect to home page with logout confirmation

## Document Management System

### Document Model
```python
class Document(db.Model):
    id: Integer (Primary Key)
    filename: String(255) (Stored filename)
    original_filename: String(255) (Original upload name)
    path: String(500) (File system path)
    status: String(20) (processing|completed|failed)
    uploaded_at: DateTime
    processed_at: DateTime
    user_id: Integer (Foreign Key to users.id)
    similarity_score_value: Float
    ai_percentage: Float
    word_count: Integer
    report_path: String(255)
    error_message: Text
```

### Document Processing Endpoints

#### GET /dashboard
User dashboard showing all uploaded documents.

**Authentication:** Required
**Response:** HTML page with document list

#### POST /upload
Upload document for plagiarism analysis.

**Authentication:** Required
**Content-Type:** multipart/form-data

**Request:**
- File: Document file (.pdf, .doc, .docx, .txt)
- Maximum size: 16MB

**Response:**
- Success: Document uploaded, processing started
- Error: File validation errors

**Processing Pipeline:**
1. File validation and security checks
2. Secure filename generation with timestamp
3. Database record creation
4. Background processing initiation
5. Selenium automation with academi.cx

#### GET /document/{id}
View document details and results.

**Authentication:** Required
**Authorization:** Document owner or admin

**Response:**
- Document metadata
- Processing status
- Plagiarism results (if available)
- Download links for reports

#### POST /reprocess/{id}
Reprocess a failed document.

**Authentication:** Required
**Authorization:** Document owner or admin

**Response:**
- Reset document status
- Restart background processing

#### POST /delete/{id}
Delete a document and associated files.

**Authentication:** Required  
**Authorization:** Document owner or admin

**Response:**
- Remove file from filesystem
- Delete database record

#### GET /download_report/{id}
Download similarity report PDF.

**Authentication:** Required
**Authorization:** Document owner or admin

**Response:**
- PDF file download
- Error if report not available

## Admin System

### Admin Endpoints

All admin endpoints require admin privileges and are prefixed with `/admin/`.

#### GET /admin/dashboard
Admin dashboard with user management interface.

**Authentication:** Required (Admin only)
**Response:** HTML page with user list and controls

#### GET /admin/user/toggle/{user_id}
Toggle user active status.

**Authentication:** Required (Admin only)
**Authorization:** Cannot modify own account

**Response:**
- Toggle user.is_active
- Redirect to admin dashboard

#### GET /admin/user/make_admin/{user_id}
Grant admin privileges to user.

**Authentication:** Required (Admin only)
**Authorization:** Cannot modify own account

#### GET /admin/user/remove_admin/{user_id}
Remove admin privileges from user.

**Authentication:** Required (Admin only)
**Authorization:** Cannot modify own account

#### POST /admin/user/delete/{user_id}
Delete user account and associated data.

**Authentication:** Required (Admin only)
**Authorization:** Cannot delete own account

## Document Processing Integration

### Selenium Automation Pipeline

The system uses Selenium WebDriver to automate interaction with academi.cx:

#### DocumentProcessor Class

**Methods:**
- `setup_driver()`: Configure Chrome browser
- `login()`: Authenticate with academi.cx
- `upload_document()`: Upload file to service
- `extract_results()`: Parse plagiarism results
- `wait_for_download()`: Handle report downloads
- `cleanup()`: Close browser and cleanup

#### Background Processing

Documents are processed asynchronously using Python threading:

```python
def process_document_background(document_id):
    processor = DocumentProcessor()
    try:
        success = processor.process_document(document_id)
        return success
    finally:
        processor.cleanup()
```

#### Processing Status Workflow

1. **uploaded**: Initial state after file upload
2. **processing**: Document being analyzed by academi.cx
3. **completed**: Analysis finished, results available
4. **failed**: Error occurred during processing

### Results Extraction

The system extracts the following data from academi.cx:

- **Document Name**: Original filename
- **Word Count**: Total words in document
- **AI Percentage**: AI-generated content score
- **Similarity Percentage**: Plagiarism similarity score
- **Report File**: Downloadable PDF report

## Security Features

### Authentication Security
- Password hashing with Werkzeug PBKDF2
- Session management with Flask-Login
- CSRF protection via Flask-WTF
- Account activation workflow

### File Security
- File type validation
- Secure filename generation
- Path traversal protection
- Size limit enforcement (16MB)
- Temporary file cleanup

### Authorization
- Role-based access control (Admin/User)
- Document ownership verification
- Admin privilege separation
- Route-level permission checks

## Error Handling

### Document Processing Errors
- Connection failures to academi.cx
- Upload timeouts
- Result extraction failures
- Browser automation issues

### Application Errors
- Database connection issues
- File system errors
- Validation failures
- Authentication errors

## Configuration

### Environment Variables

Required for production deployment:

```bash
# Flask Configuration
FLASK_APP=wsgi.py
FLASK_ENV=production
SECRET_KEY=your-secure-secret-key

# Database Configuration
DATABASE_URL=mysql+pymysql://user:pass@host:port/db
# OR MySQL individual settings:
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=username
MYSQL_PASSWORD=password
MYSQL_DATABASE=potplag

# Admin Account
ADMIN_EMAIL=admin@yourcompany.com
ADMIN_PASSWORD=secure-admin-password

# Academi.cx Integration
ACADEMI_EMAIL=your-academi-email
ACADEMI_PASSWORD=your-academi-password

# Email Configuration (Optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email
MAIL_PASSWORD=your-app-password
```

### File Configuration

- **Upload Directory**: `uploads/` (auto-created)
- **Download Directory**: `downloads/` (auto-created)
- **Status Directory**: `status/` (processing status files)
- **Database File**: `app.db` (SQLite fallback)

## Performance Considerations

### Optimization Strategies
- Background processing for long-running operations
- Database indexing on frequently queried fields
- Efficient file handling with streaming
- Session management optimization

### Scalability Notes
- Consider task queue (Celery) for production
- Database connection pooling for high load
- File storage optimization (cloud storage)
- Browser automation scaling challenges

## Error Codes and Responses

### HTTP Status Codes
- **200**: Success
- **302**: Redirect (authentication, authorization)
- **400**: Bad request (validation errors)
- **401**: Unauthorized (login required)
- **403**: Forbidden (insufficient privileges)
- **404**: Not found (document/user not exists)
- **500**: Internal server error

### Custom Error Messages
- Authentication failures
- File validation errors
- Processing failures
- Permission denials

## Monitoring and Logging

### Application Logging
- Authentication events
- Document processing status
- Error conditions
- Admin actions

### Health Checks
- Database connectivity
- File system access
- External service availability
- Background processing status
