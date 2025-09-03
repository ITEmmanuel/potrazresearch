from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_from_directory, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import os

# Create blueprint
bp = Blueprint('main', __name__)

# Import models and forms after creating the blueprint to avoid circular imports
from ..models import db, Document
from ..forms import DocumentUploadForm

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@bp.route('/')
@bp.route('/index')
def index():
    if current_user.is_authenticated:
        # Get user's documents, most recent first
        documents = Document.query.filter_by(user_id=current_user.id)\
                                 .order_by(Document.uploaded_at.desc())\
                                 .all()
        return render_template('index.html', documents=documents)
    return render_template('index.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    # Get user's documents, most recent first
    documents = Document.query.filter_by(user_id=current_user.id)\
                             .order_by(Document.uploaded_at.desc())\
                             .all()
    return render_template('dashboard.html', documents=documents)

@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = DocumentUploadForm()
    
    if form.validate_on_submit():
        file = form.document.data
        
        if not file:
            flash('No file selected', 'danger')
            return redirect(request.url)
            
        if not allowed_file(file.filename):
            flash('File type not allowed', 'danger')
            return redirect(request.url)
            
        # Create a secure filename
        filename = secure_filename(file.filename)
        # Add timestamp to avoid filename collisions
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        filename = f"{timestamp}_{filename}"
        
        # Ensure upload directory exists
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        # Save the file
        file.save(filepath)
        
        # Create document record
        document = Document(
            filename=filename,
            original_filename=file.filename,
            path=filepath,
            user_id=current_user.id,
            status='processing',
            uploaded_at=datetime.utcnow()
        )
        
        db.session.add(document)
        db.session.commit()

        # Process document for plagiarism in background
        from ..document_processor import process_document_background
        from threading import Thread

        # Start background processing
        processing_thread = Thread(target=process_document_background, args=(document.id,))
        processing_thread.daemon = True
        processing_thread.start()

        flash('Document uploaded successfully and is being processed', 'success')
        return redirect(url_for('main.dashboard'))
        
    return render_template('upload.html', form=form)

@bp.route('/document/<int:document_id>')
@login_required
def view_document(document_id):
    document = Document.query.get_or_404(document_id)
    
    # Ensure the user owns the document
    if document.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to view this document', 'danger')
        return redirect(url_for('main.dashboard'))
        
    # Check if report exists
    report_exists = False
    if document.report_path and os.path.exists(os.path.join(current_app.config['DOWNLOAD_DIR'], document.report_path)):
        report_exists = True

    return render_template('view_document.html', document=document, report_exists=report_exists)

@bp.route('/download/<path:filename>')
@login_required
def download_file(filename):
    # Ensure the file exists and the user has permission to download it
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        flash('File not found', 'danger')
        return redirect(url_for('main.dashboard'))
        
    # Check if the document belongs to the user or if the user is an admin
    document = Document.query.filter_by(filename=filename).first()
    if not document:
        flash('Document not found in database', 'danger')
        return redirect(url_for('main.dashboard'))
        
    if document.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to download this file', 'danger')
        return redirect(url_for('main.dashboard'))
        
    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
        filename,
        as_attachment=True
    )

@bp.route('/download_report/<int:document_id>')
@login_required
def download_report(document_id):
    """Download similarity report for a document"""
    document = Document.query.get_or_404(document_id)

    # Ensure the user owns the document
    if document.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to download this report', 'danger')
        return redirect(url_for('main.dashboard'))

    if not document.report_path:
        flash('Report not available for this document', 'warning')
        return redirect(url_for('main.view_document', document_id=document_id))

    report_path = os.path.join(current_app.config['DOWNLOAD_DIR'], document.report_path)

    if not os.path.exists(report_path):
        flash('Report file not found', 'danger')
        return redirect(url_for('main.view_document', document_id=document_id))

    return send_from_directory(
        current_app.config['DOWNLOAD_DIR'],
        document.report_path,
        as_attachment=True,
        download_name=f"{document.original_filename}_similarity_report.pdf"
    )

@bp.route('/reprocess/<int:document_id>', methods=['POST'])
@login_required
def reprocess_document(document_id):
    """Reprocess a failed document"""
    document = Document.query.get_or_404(document_id)

    # Ensure the user owns the document
    if document.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to reprocess this document', 'danger')
        return redirect(url_for('main.dashboard'))

    # Reset document status
    document.status = 'processing'
    document.processed_at = None
    document.similarity_score = 0.0
    document.report_path = None
    db.session.commit()

    # Start background processing
    from ..document_processor import process_document_background
    from threading import Thread

    processing_thread = Thread(target=process_document_background, args=(document.id,))
    processing_thread.daemon = True
    processing_thread.start()

    flash('Document reprocessing started', 'info')
    return redirect(url_for('main.view_document', document_id=document_id))

@bp.route('/delete/<int:document_id>', methods=['POST'])
@login_required
def delete_document(document_id):
    document = Document.query.get_or_404(document_id)
    
    # Ensure the user owns the document or is an admin
    if document.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to delete this document', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Delete the file from the filesystem
    try:
        if os.path.exists(document.filepath):
            os.remove(document.filepath)
    except Exception as e:
        current_app.logger.error(f'Error deleting file {document.filepath}: {str(e)}')
        flash('Error deleting file', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Delete the database record
    db.session.delete(document)
    db.session.commit()
    
    flash('Document deleted successfully', 'success')
    return redirect(url_for('main.dashboard'))
