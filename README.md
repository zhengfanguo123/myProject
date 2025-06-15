# Workflow Manager Example

This repository contains a simple Flask application demonstrating a dashboard layout with a sidebar navigation, greeting panel, notifications section, and user information area.

## Running

1. Install dependencies (preferably in a virtual environment):
   ```bash
   pip install -r requirements.txt
   ```
2. Start the server:
   ```bash
   python app.py
   ```
3. Open `http://localhost:5000/login` to sign in.
   After login, visit `http://localhost:5000/dashboard` for the dashboard,
   `http://localhost:5000/users` for user management,
   `http://localhost:5000/wm/user_groups` for the user groups page,
   `http://localhost:5000/wm/roles` for role management, or
   `http://localhost:5000/wm/ldapserver` to manage LDAP server connections.

When creating users through the API or UI, make sure the provided group name
matches an existing user group. The User Groups page lists all groups along with
their current user counts.

### Login

Use the dropdown on the login page to choose **Local** or **LDAP** authentication.
For local users, passwords are securely hashed. A sample account is created on first run:

```
username: admin
password: admin
```

For LDAP, the app binds to the configured server and fetches profile attributes such as
`cn` and `mail` when creating a user record.
