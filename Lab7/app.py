from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import re

# Initialize SQLAlchemy
db = SQLAlchemy()

def check_password_requirements(password):
    # Initialize flags to track which requirements are not met
    length_flag = len(password) >= 8
    lowercase_flag = any(char.islower() for char in password)
    uppercase_flag = any(char.isupper() for char in password)
    end_number_flag = password[-1].isdigit()

    # Determine which requirements are not met
    requirements_not_met = []
    if not length_flag:
        requirements_not_met.append("Password should be at least 8 characters.")
    if not lowercase_flag:
        requirements_not_met.append("Password must contain at least one lowercase letter.")
    if not uppercase_flag:
        requirements_not_met.append("Password must contain at least one uppercase letter.")
    if not end_number_flag:
        requirements_not_met.append("Password must end with a number.")

    # Return False if any requirement is not met, along with the list of unsatisfied requirements
    if not (length_flag and lowercase_flag and uppercase_flag and end_number_flag):
        return False, requirements_not_met
    
    return True, []


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Import models and routes
    with app.app_context():
        from models import User
        db.create_all()
    
    # Define routes here to avoid circular imports
    @app.route('/', methods=['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            password = request.form['password']
            confirm_password = request.form['confirm_password']

            # Check if the email is already in use
            '''existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('Email address is already in use!', 'danger')
                return redirect(url_for('signup'))'''

            # Password validation
            if password != confirm_password:
                flash('Passwords do not match!', 'danger')
                return redirect(url_for('signup'))

            is_valid, requirements_not_met = check_password_requirements(password)

            if not is_valid:
                flash('Password must contain a lowercase letter, an uppercase letter, a number, and be at least 8 characters long.', 'danger')
                return redirect(url_for('signup'))

            try:
                new_user = User(first_name=first_name, last_name=last_name, email=email, password=password)
                db.session.add(new_user)
                db.session.commit()
            except Exception as e:
                if 'UNIQUE constraint failed: user.email' in str(e):
                    flash('Account with this email already existing', 'danger')
                    #flash(f'An error occurred: {e}', 'danger')
                    return redirect(url_for('signup'))
            else:   
                return redirect(url_for('thankyou'))
        
        return render_template('signup.html')

    @app.route('/signin', methods=['GET', 'POST'])
    def signin():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']

            try:

                user = User.query.filter_by(email=email).first()
                if user and user.password == password:
                    return redirect(url_for('secretPage'))
                else:
                    flash('Invalid credentials', 'danger')
                    return redirect(url_for('signin'))
        
            except Exception as e:
                flash(f'An error occurred: {e}', 'danger')
                return redirect(url_for('signin'))
        
        return render_template('signin.html')

    @app.route('/secretPage')
    def secretPage():
        return render_template('secretPage.html')

    @app.route('/thankyou')
    def thankyou():
        return render_template('thankyou.html')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
