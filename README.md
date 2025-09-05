# Access Portal Web Application

This is a Flask-based web application for managing user and admin access portals. It includes user registration, login, password management, and request handling features.

## Features

- User and Admin authentication and authorization
- User dashboard and admin dashboard
- Request submission and management
- Email notifications via Flask-Mail
- Database migrations with Flask-Migrate
- Responsive UI with Bootstrap and custom CSS

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd accessportalv4
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On Linux/macOS
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure environment variables and instance/config.py:

- Copy `instance/config.py` and update the `SECRET_KEY` and `SQLALCHEMY_DATABASE_URI` as needed.
- Ensure `instance/config.py` is excluded from version control.
- For production, use strong, randomly generated secrets for `SECRET_KEY`.
- Configure database connection strings securely (avoid hardcoding credentials).

5. Initialize the database:

```bash
flask db upgrade
```

6. For database migrations (when making changes to models):

```bash
# Create a new migration
flask db migrate -m "Description of changes"

# Apply the migration
flask db upgrade

# Rollback if needed
flask db downgrade
```

7. Run the application:

```bash
python app.py
```

The app will be available at `http://localhost:8082`.

## Deployment

- For production, set `FLASK_ENV=production` and configure the app to run with a production-ready server like Gunicorn.
- Update `app.py` to read configuration from environment variables for debug mode and port.
- Use database migrations to keep the schema up to date.
- Consider adding a `Procfile` or `Dockerfile` for deployment on platforms like Heroku or Docker containers.

## License

This project is licensed under the MIT License.
