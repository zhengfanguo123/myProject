# Workflow Manager Example

This repository contains a simple Flask application demonstrating a dashboard layout with a sidebar navigation, greeting panel, notifications section, and user information area.

## Running

1. Install dependencies (preferably in a virtual environment):
   ```bash
   pip install -r requirements.txt
   ```
2. Start the server. To allow access from other machines, bind to all interfaces:
   ```bash
   python app.py
   ```
   The server runs on port 5000 and listens on `0.0.0.0` so it is reachable via your server's IP.
   Ensure your firewall or security group allows inbound connections on port `5000`.
3. Open `http://<server-ip>:5000/login` to sign in from another device, or use `http://localhost:5000/login` locally.
After login, visit `http://localhost:5000/dashboard` for the dashboard,
   `http://localhost:5000/users` for user management,
   `http://localhost:5000/wm/user_groups` for the user groups page,
   `http://localhost:5000/wm/roles` for role management, or
   `http://localhost:5000/wm/ldapserver` to manage LDAP server connections.

When creating users through the API or UI, make sure the provided group name
matches an existing user group. The User Groups page lists all groups along with
their current user counts.

### Sidebar visibility

Menu items shown in the sidebar depend on the role stored in the session. After
login, `session['role']` is set from the user record. Admins see **Home**,
**Users**, **User Groups**, **Roles**, **LDAP Server**, **Licensing**, and
**HPC**. Regular users only see **Home**, **Notification Email**, **Models**,
**Input Files**, and **Scheduling**. Pages such as `/users` and `/wm/roles` are
restricted with `roles_required('admin')`.

The application checks the SQLite schema on startup and will recreate the
database if required columns such as `password_hash` are missing. Delete
`data.db` if you prefer to preserve existing data and run migrations manually.

### Login

Use the dropdown on the login page to choose **Local** or **LDAP** authentication.
For local users, passwords are securely hashed. On startup the application seeds two roles, `admin` and `user`, along with sample accounts:

```
username: admin
password: admin
```
A regular user account is also created:

```
username: user1
password: user1
```

The application defines two roles: `admin` and `user`. Sidebar items and access
to management pages depend on this role. The helper decorator `roles_required`
can be used to restrict routes, and `admin_required` now simply calls
`roles_required('admin')`.

For LDAP, the app binds to the configured server and fetches profile attributes such as
`cn` and `mail` when creating a user record.

When creating users through the `/api/users` endpoint or the Users page,
provide a `password` value so the account can authenticate locally. The
application hashes this value before storing it.

## Kiosk

A basic kiosk interface is available at `/kiosk`. This page lets customers browse menu items and add them to a cart. Checkout is currently a placeholder.

