# Workflow Manager Example

This repository contains a simple Flask application demonstrating a dashboard layout with a sidebar navigation, greeting panel, notifications section, and user information area.

## Running

1. Install dependencies:
   ```bash
   pip install flask flask_sqlalchemy
   ```
2. Start the server:
   ```bash
   python app.py
   ```
3. Open `http://localhost:5000/dashboard` for the dashboard,
   `http://localhost:5000/users` for user management, or
   `http://localhost:5000/wm/user_groups` for the user groups page.

## Community Website

Additional directories have been added to start a community website project.

- `backend/` contains a FastAPI application with a basic user system and JWT authentication.
- `frontend/` is a placeholder React/TailwindCSS project.

Follow the READMEs in each directory for setup instructions.
