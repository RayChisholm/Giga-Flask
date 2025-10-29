import os
from app import create_app, db
from app.models import User, ZendeskSettings, Job

app = create_app(os.getenv('FLASK_ENV') or 'default')


@app.shell_context_processor
def make_shell_context():
    """Make database objects available in Flask shell"""
    return {
        'db': db,
        'User': User,
        'ZendeskSettings': ZendeskSettings,
        'Job': Job
    }


@app.cli.command()
def init_db():
    """Initialize the database"""
    db.create_all()
    print('Database initialized!')


@app.cli.command()
def create_admin():
    """Create an admin user"""
    username = input('Enter admin username: ')
    email = input('Enter admin email: ')
    password = input('Enter admin password: ')

    # Check if user already exists
    if User.query.filter_by(username=username).first():
        print(f'Error: User {username} already exists!')
        return

    if User.query.filter_by(email=email).first():
        print(f'Error: Email {email} is already registered!')
        return

    # Create admin user
    admin = User(
        username=username,
        email=email,
        role='admin',
        active=True
    )
    admin.set_password(password)

    db.session.add(admin)
    db.session.commit()

    print(f'Admin user {username} created successfully!')


# Import tool implementations to trigger registration
from app.tools.implementations import *


if __name__ == '__main__':
    app.run(debug=True)
