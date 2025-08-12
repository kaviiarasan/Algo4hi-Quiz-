from flask import render_template, request, redirect, url_for, flash, session, make_response
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import csv
import io
import os
import random
from app import app, db
from models import Admin, Quiz, QuizSubmission, User, Winner
from forms import AdminLoginForm, CreateQuizForm
import secrets
import string

# Allowed file extensions for uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def admin_required(f):
    def admin_decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Admin access required.', 'danger')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    admin_decorated_function.__name__ = f.__name__
    return admin_decorated_function

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))
    
    form = AdminLoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(email=form.username.data).first()
        if admin and check_password_hash(admin.password_hash, form.password.data):
            session['admin_logged_in'] = True
            session['admin_id'] = admin.id
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials', 'danger')
    
    return render_template('admin_login.html', form=form)

@app.route('/admin/logout')
@admin_required
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_id', None)
    flash('Admin logged out successfully.', 'info')
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    # Get all quizzes
    quizzes = Quiz.query.order_by(Quiz.created_at.desc()).all()
    
    # Get current time for status checking
    now = datetime.utcnow()
    
    return render_template('admin_dashboard.html', quizzes=quizzes, now=now)

def generate_quiz_url():
    """Generate a unique URL for quiz access"""
    while True:
        url = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(8))
        if not Quiz.query.filter_by(quiz_url=url).first():
            return url

@app.route('/admin/create-quiz', methods=['GET', 'POST'])
@admin_required
def create_quiz():
    if request.method == 'POST':
        # Handle dynamic form submission
        title = request.form.get('title')
        start_time = datetime.fromisoformat(request.form.get('start_time'))
        end_time = datetime.fromisoformat(request.form.get('end_time'))
        question1 = request.form.get('question1')
        question2 = request.form.get('question2')
        
        # Get question 1 options
        q1_options = []
        q1_correct = int(request.form.get('question1_correct'))
        i = 1
        while request.form.get(f'question1_option{i}'):
            q1_options.append(request.form.get(f'question1_option{i}'))
            i += 1
        
        # Get question 2 options
        q2_options = []
        q2_correct = int(request.form.get('question2_correct'))
        i = 1
        while request.form.get(f'question2_option{i}'):
            q2_options.append(request.form.get(f'question2_option{i}'))
            i += 1
        
        # Create quiz
        quiz = Quiz(
            title=title,
            start_time=start_time,
            end_time=end_time,
            question1=question1,
            question1_options=q1_options,
            question1_correct=q1_correct,
            question2=question2,
            question2_options=q2_options,
            question2_correct=q2_correct,
            quiz_url=generate_quiz_url()
        )
        
        db.session.add(quiz)
        db.session.commit()
        
        flash('Quiz created successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('create_quiz.html')

@app.route('/admin/edit-quiz/<int:quiz_id>', methods=['GET', 'POST'])
@admin_required
def edit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    if request.method == 'POST':
        quiz.title = request.form.get('title')
        quiz.start_time = datetime.fromisoformat(request.form.get('start_time'))
        quiz.end_time = datetime.fromisoformat(request.form.get('end_time'))
        quiz.question1 = request.form.get('question1')
        quiz.question2 = request.form.get('question2')
        
        # Update question 1 options
        q1_options = []
        q1_correct = int(request.form.get('question1_correct'))
        i = 1
        while request.form.get(f'question1_option{i}'):
            q1_options.append(request.form.get(f'question1_option{i}'))
            i += 1
        quiz.question1_options = q1_options
        quiz.question1_correct = q1_correct
        
        # Update question 2 options
        q2_options = []
        q2_correct = int(request.form.get('question2_correct'))
        i = 1
        while request.form.get(f'question2_option{i}'):
            q2_options.append(request.form.get(f'question2_option{i}'))
            i += 1
        quiz.question2_options = q2_options
        quiz.question2_correct = q2_correct
        
        db.session.commit()
        flash('Quiz updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('edit_quiz.html', quiz=quiz)

@app.route('/admin/winners')
@admin_required
def manage_winners():
    winners = Winner.query.order_by(Winner.display_order).all()
    return render_template('manage_winners.html', winners=winners)

@app.route('/admin/winner/add', methods=['GET', 'POST'])
@admin_required
def add_winner():
    if request.method == 'POST':
        # Handle file upload
        photo_url = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename != '' and allowed_file(file.filename):
                # Create uploads directory if it doesn't exist
                upload_dir = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
                os.makedirs(upload_dir, exist_ok=True)
                
                # Generate secure filename
                filename = secure_filename(file.filename)
                # Add timestamp to avoid conflicts
                timestamp = str(int(datetime.utcnow().timestamp()))
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{timestamp}{ext}"
                
                # Save file
                file_path = os.path.join(upload_dir, filename)
                file.save(file_path)
                
                # Store relative path for database
                photo_url = f"uploads/{filename}"
        
        winner = Winner(
            name=request.form.get('name'),
            photo_url=photo_url,
            achievement=request.form.get('achievement'),
            quiz_id=request.form.get('quiz_id') if request.form.get('quiz_id') else None,
            display_order=request.form.get('display_order', 0)
        )
        db.session.add(winner)
        db.session.commit()
        flash('Winner added successfully!', 'success')
        return redirect(url_for('manage_winners'))
    
    quizzes = Quiz.query.filter_by(is_locked=True).all()
    return render_template('add_winner.html', quizzes=quizzes)

@app.route('/admin/winner/<int:winner_id>/delete')
@admin_required
def delete_winner(winner_id):
    winner = Winner.query.get_or_404(winner_id)
    db.session.delete(winner)
    db.session.commit()
    flash('Winner removed successfully!', 'success')
    return redirect(url_for('manage_winners'))

@app.route('/admin/quiz/<int:quiz_id>/submissions')
@admin_required
def view_submissions(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Get all submissions for this quiz
    submissions = db.session.query(QuizSubmission, User).join(User).filter(
        QuizSubmission.quiz_id == quiz_id
    ).order_by(QuizSubmission.score.desc(), QuizSubmission.time_taken.asc()).all()
    
    return render_template('view_submissions.html', quiz=quiz, submissions=submissions)

@app.route('/admin/quiz/<int:quiz_id>/lock')
@admin_required
def lock_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    if quiz.is_locked:
        flash('Quiz is already locked.', 'warning')
        return redirect(url_for('admin_dashboard'))
    
    # Lock the quiz
    quiz.is_locked = True
    
    # Determine winner
    submissions = QuizSubmission.query.filter_by(quiz_id=quiz_id)\
        .order_by(QuizSubmission.score.desc(), QuizSubmission.time_taken.asc()).all()
    
    if submissions:
        # Get highest score
        highest_score = submissions[0].score
        top_submissions = [s for s in submissions if s.score == highest_score]
        
        if len(top_submissions) == 1:
            # Clear winner
            winner = top_submissions[0]
        else:
            # Tie-breaker: fastest time
            fastest_time = min(s.time_taken for s in top_submissions)
            fastest_submissions = [s for s in top_submissions if s.time_taken == fastest_time]
            
            if len(fastest_submissions) == 1:
                # Fastest time wins
                winner = fastest_submissions[0]
            else:
                # Random selection among tied submissions
                winner = random.choice(fastest_submissions)
        
        quiz.winner_id = winner.user_id
    
    db.session.commit()
    
    flash('Quiz locked successfully! Winner has been determined.', 'success')
    return redirect(url_for('view_submissions', quiz_id=quiz_id))

@app.route('/admin/quiz/<int:quiz_id>/publish-results')
@admin_required
def publish_results(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    if not quiz.is_locked:
        flash('Quiz must be locked before publishing results.', 'warning')
        return redirect(url_for('admin_dashboard'))
    
    quiz.results_published = True
    db.session.commit()
    
    flash('Results published successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/quiz/<int:quiz_id>/export-csv')
@admin_required
def export_csv(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Get all submissions with user data
    submissions = db.session.query(QuizSubmission, User).join(User).filter(
        QuizSubmission.quiz_id == quiz_id
    ).order_by(QuizSubmission.score.desc(), QuizSubmission.time_taken.asc()).all()
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow([
        'Name', 'Email', 'Answer 1', 'Answer 2', 'Score', 
        'Time Taken (seconds)', 'Bonus Awarded', 'Submitted At'
    ])
    
    # Write data
    for submission, user in submissions:
        writer.writerow([
            user.name,
            user.email,
            chr(65 + submission.answer1),  # Convert to A, B, C, D
            chr(65 + submission.answer2),
            submission.score,
            submission.time_taken,
            'Yes' if submission.bonus_awarded else 'No',
            submission.submitted_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename={quiz.title}_results.csv'
    response.headers['Content-type'] = 'text/csv'
    
    return response
