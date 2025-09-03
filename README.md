# Plagiarism Checker

A web-based plagiarism detection system built with Flask that allows users to upload documents and check for potential plagiarism against online sources and previously submitted documents.

## Features

- User authentication (login/register)
- Document upload and management
- Plagiarism detection with similarity scoring
- Detailed similarity reports
- Admin dashboard for user management
- Responsive design for all devices
- Secure file handling
- Exportable reports

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/plagiarism-checker.git
   cd plagiarism-checker
   ```

2. Create and activate a virtual environment:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the root directory with the following variables:
   ```
   FLASK_APP=wsgi.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///app.db
   ADMIN_EMAIL=admin@example.com
   ADMIN_PASSWORD=admin123
   ```

5. Initialize the database:
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. Run the application:
   ```bash
   flask run
   ```

7. Open your browser and navigate to `http://localhost:5000`

## Usage

1. Register a new account or log in with existing credentials
2. Upload a document (supports .pdf, .doc, .docx, .txt)
3. Wait for the document to be processed
4. View the similarity report and analysis
5. Download the report or export it in different formats

## Admin Features

- View all users and their documents
- Activate/deactivate user accounts
- Monitor system usage
- Manage application settings

## Project Structure

```
plagiarism-checker/
├── app/
│   ├── __init__.py       # Application factory and extensions
│   ├── auth/             # Authentication routes and views
│   ├── admin/            # Admin routes and views
│   ├── main/             # Main application routes and views
│   └── templates/        # HTML templates
├── instance/             # Instance folder for database and uploads
├── migrations/           # Database migrations
├── static/               # Static files (CSS, JS, images)
├── .env                  # Environment variables
├── .gitignore
├── config.py             # Configuration settings
├── extensions.py         # Flask extensions
├── models.py             # Database models
├── requirements.txt      # Project dependencies
└── wsgi.py               # WSGI entry point
```

## Dependencies

- Flask - Web framework
- Flask-SQLAlchemy - ORM for database operations
- Flask-Login - User session management
- Flask-WTF - Form handling and validation
- Flask-Migrate - Database migrations
- Selenium - Web scraping for plagiarism detection
- NLTK - Natural language processing
- Other dependencies listed in requirements.txt

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Bootstrap](https://getbootstrap.com/)
- [Font Awesome](https://fontawesome.com/)
