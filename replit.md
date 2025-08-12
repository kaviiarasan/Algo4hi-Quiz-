# Quiz Competition Website

## Overview

A Flask-based web application for managing competitive quizzes with real-time scoring and admin controls. The platform allows users to register, participate in timed quizzes with exactly 2 questions, and compete for points based on accuracy and speed. Features include user authentication, admin dashboard for quiz management, real-time timer functionality, and comprehensive results tracking.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Web Framework
- **Flask**: Chosen as the primary web framework for its simplicity and flexibility in building web applications
- **Jinja2 templating**: Used for server-side rendering of HTML templates with dynamic content
- **Flask-Login**: Handles user session management and authentication state
- **Flask-WTF**: Provides form handling, validation, and CSRF protection

### Database Design
- **SQLAlchemy ORM**: Chosen for database abstraction and relationship management
- **SQLite**: Default database for development (configurable via environment variables)
- **Four main entities**:
  - User: Stores participant information and authentication data
  - Admin: Separate admin accounts with elevated privileges
  - Quiz: Contains quiz metadata, questions, and timing information
  - QuizSubmission: Records user responses, scores, and timing data

### Authentication & Authorization
- **Dual authentication system**: Separate login flows for regular users and administrators
- **Password hashing**: Uses Werkzeug's security utilities for secure password storage
- **Session-based authentication**: Flask sessions for maintaining login state
- **Role-based access control**: Admin-specific routes protected by custom decorators

### Frontend Architecture
- **Bootstrap 5**: Responsive CSS framework with dark theme support
- **Font Awesome**: Icon library for consistent UI elements
- **JavaScript timer**: Client-side real-time timer for quiz sessions
- **Progressive enhancement**: Core functionality works without JavaScript

### Quiz Scoring System
- **Fixed scoring model**: 10 points per correct answer, maximum 25 points
- **Speed bonus**: Additional 5 points for completing both questions correctly under 60 seconds
- **Time tracking**: Precise timing recorded for tie-breaking and bonus calculation
- **Single submission rule**: Prevents multiple attempts per user per quiz

### Admin Features
- **Quiz creation**: Form-based interface for creating timed quizzes
- **Submission monitoring**: Real-time view of all quiz responses
- **Result publication**: Admin-controlled release of quiz results
- **Data export**: CSV export functionality for external analysis
- **Quiz locking**: Prevents further submissions and triggers winner calculation

## External Dependencies

### Frontend Libraries
- **Bootstrap 5**: CSS framework loaded from Replit CDN
- **Font Awesome 6.4.0**: Icon library from Cloudflare CDN
- **Custom JavaScript**: Timer functionality and form handling

### Python Packages
- **Flask**: Web application framework
- **Flask-SQLAlchemy**: Database ORM and management
- **Flask-Login**: User session management
- **Flask-WTF**: Form handling and validation
- **WTForms**: Form field validation and rendering
- **Werkzeug**: Security utilities for password hashing

### Deployment Configuration
- **ProxyFix middleware**: Handles reverse proxy headers for proper URL generation
- **Environment variables**: Database URL and session secret configuration
- **Replit compatibility**: Configured for deployment on Replit platform