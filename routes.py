from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import app, db
from models import User, Quiz, QuizSubmission, Winner
from forms import LoginForm, RegisterForm, QuizSubmissionForm
import random

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Check for admin login by email (case insensitive)
        if form.email.data.lower() == 'kaviiarasan.sv@gktech.ai' and form.password.data == 'algogkt@123':
            session['admin_logged_in'] = True
            session['admin_user'] = 'Algo admin'
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        
        # Regular user login
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            next_page = request.args.get('quiz')
            if next_page:
                return redirect(url_for('take_quiz', quiz_id=next_page))
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if user already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered. Please login instead.', 'danger')
            return redirect(url_for('login'))
        
        # Create new user
        user = User(
            name=form.name.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data)
        )
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        flash('Registration successful! Welcome to Quiz Competition!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get current active quiz
    now = datetime.utcnow()
    active_quiz = Quiz.query.filter(
        Quiz.start_time <= now,
        Quiz.end_time >= now,
        Quiz.is_locked == False
    ).first()
    
    # Get user's past submissions
    past_submissions = QuizSubmission.query.filter_by(user_id=current_user.id).all()
    
    # Check if user has already submitted for active quiz
    already_submitted = False
    if active_quiz:
        already_submitted = QuizSubmission.query.filter_by(
            user_id=current_user.id,
            quiz_id=active_quiz.id
        ).first() is not None
    
    # Get winners for showcase
    from models import Winner
    winners = Winner.query.filter_by(is_active=True).order_by(Winner.display_order).all()
    
    # Debug: Print winners info
    print(f"Found {len(winners)} winners")
    for winner in winners:
        print(f"Winner: {winner.name}, Photo: {winner.photo_url}")
        if winner.photo_url:
            import os
            photo_path = os.path.join(app.root_path, 'static', winner.photo_url)
            exists = os.path.exists(photo_path)
            print(f"  File exists at {photo_path}: {exists}")
            if exists:
                file_size = os.path.getsize(photo_path)
                print(f"  File size: {file_size} bytes")
    
    return render_template('dashboard.html', 
                         active_quiz=active_quiz, 
                         past_submissions=past_submissions,
                         already_submitted=already_submitted,
                         winners=winners)

@app.route('/q/<quiz_url>')
def direct_quiz_access(quiz_url):
    quiz = Quiz.query.filter_by(quiz_url=quiz_url).first_or_404()
    
    if not current_user.is_authenticated:
        return redirect(url_for('login', quiz=quiz.id))
    
    return redirect(url_for('take_quiz', quiz_id=quiz.id))

@app.route('/quiz/<int:quiz_id>')
@login_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Check if quiz is active
    now = datetime.utcnow()
    if now < quiz.start_time:
        flash('Quiz has not started yet.', 'warning')
        return redirect(url_for('dashboard'))
    
    if now > quiz.end_time or quiz.is_locked:
        flash('Quiz has ended.', 'warning')
        return redirect(url_for('dashboard'))
    
    # Check if user has already submitted
    existing_submission = QuizSubmission.query.filter_by(
        user_id=current_user.id,
        quiz_id=quiz_id
    ).first()
    
    if existing_submission:
        flash('You have already submitted this quiz.', 'info')
        return redirect(url_for('quiz_submitted', quiz_id=quiz_id))
    
    form = QuizSubmissionForm()
    return render_template('quiz.html', quiz=quiz, form=form)

@app.route('/quiz/<int:quiz_id>/submit', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Check if quiz is still active
    now = datetime.utcnow()
    if now > quiz.end_time or quiz.is_locked:
        flash('Quiz submission time has ended.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Check if user has already submitted
    existing_submission = QuizSubmission.query.filter_by(
        user_id=current_user.id,
        quiz_id=quiz_id
    ).first()
    
    if existing_submission:
        flash('You have already submitted this quiz.', 'warning')
        return redirect(url_for('quiz_submitted', quiz_id=quiz_id))
    
    form = QuizSubmissionForm()
    if form.validate_on_submit():
        # Calculate score
        score = 0
        correct_answers = 0
        
        if form.answer1.data == quiz.question1_correct:
            score += 10
            correct_answers += 1
        
        if form.answer2.data == quiz.question2_correct:
            score += 10
            correct_answers += 1
        
        # Check for bonus (both correct and under 1 minute)
        bonus_awarded = False
        if correct_answers == 2 and form.time_taken.data < 60:
            score += 5
            bonus_awarded = True
        
        # Create submission
        submission = QuizSubmission(
            user_id=current_user.id,
            quiz_id=quiz_id,
            answer1=form.answer1.data,
            answer2=form.answer2.data,
            time_taken=form.time_taken.data,
            score=score,
            bonus_awarded=bonus_awarded
        )
        
        db.session.add(submission)
        db.session.commit()
        
        flash('Quiz submitted successfully!', 'success')
        return redirect(url_for('quiz_submitted', quiz_id=quiz_id))
    
    return render_template('quiz.html', quiz=quiz, form=form)

@app.route('/quiz/<int:quiz_id>/submitted')
@login_required
def quiz_submitted(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Get user's submission
    submission = QuizSubmission.query.filter_by(
        user_id=current_user.id,
        quiz_id=quiz_id
    ).first()
    
    if not submission:
        flash('No submission found for this quiz.', 'warning')
        return redirect(url_for('dashboard'))
    
    return render_template('quiz_submitted.html', quiz=quiz, submission=submission)

@app.route('/results/<int:quiz_id>')
def view_results(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Check if results are published
    if not quiz.results_published:
        flash('Results are not yet published for this quiz.', 'info')
        return redirect(url_for('dashboard'))
    
    # Get all submissions for leaderboard
    submissions = QuizSubmission.query.filter_by(quiz_id=quiz_id)\
        .order_by(QuizSubmission.score.desc(), QuizSubmission.time_taken.asc())\
        .all()
    
    return render_template('results.html', quiz=quiz, submissions=submissions)

@app.route('/winner/<int:winner_id>')
def winner_landing(winner_id):
    winner = Winner.query.get_or_404(winner_id)
    
    # Debug winner data
    print(f"Loading winner landing for: {winner.name}")
    print(f"Photo URL: {winner.photo_url}")
    if winner.photo_url:
        import os
        photo_path = os.path.join(app.root_path, 'static', winner.photo_url)
        exists = os.path.exists(photo_path)
        print(f"Photo file exists: {exists} at {photo_path}")
        
        # Generate the full URL that will be used
        from flask import url_for
        if winner.photo_url.startswith('http'):
            full_url = winner.photo_url
        else:
            full_url = url_for('static', filename=winner.photo_url)
        print(f"Generated URL: {full_url}")
    
    return render_template('winner_landing.html', winner=winner)

@app.route('/test-images')
def test_images():
    """Test route to check image accessibility"""
    winners = Winner.query.filter_by(is_active=True).all()
    results = []
    
    for winner in winners:
        result = {
            'name': winner.name,
            'photo_url': winner.photo_url,
            'file_exists': False,
            'full_path': None,
            'generated_url': None
        }
        
        if winner.photo_url:
            import os
            from flask import url_for
            photo_path = os.path.join(app.root_path, 'static', winner.photo_url)
            result['file_exists'] = os.path.exists(photo_path)
            result['full_path'] = photo_path
            
            if winner.photo_url.startswith('http'):
                result['generated_url'] = winner.photo_url
            else:
                result['generated_url'] = url_for('static', filename=winner.photo_url)
        
        results.append(result)
    
    return {'winners': results}


