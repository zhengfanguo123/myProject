from flask import Flask, jsonify, render_template, request, send_file, abort, session, redirect, url_for
from functools import wraps
from ldap3 import Server as Ldap3Server, Connection as Ldap3Connection, ALL as LDAP_ALL
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import csv
import io

app = Flask(__name__)
app.secret_key = 'change-me'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)


def admin_required(f):
    """Simple decorator to restrict a view to admin users."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get('role') != 'admin':
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return wrapper


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    principal_name = db.Column(db.String(120))
    role = db.Column(db.String(80))
    email = db.Column(db.String(120))
    password_hash = db.Column(db.String(255))
    group_name = db.Column(db.String(80))
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    is_logged_in = db.Column(db.Boolean, default=False)
    is_enabled = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'principal_name': self.principal_name,
            'role': self.role,
            'email': self.email,
            'group': self.group_name,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'logged_in': self.is_logged_in,
            'enabled': self.is_enabled,
        }

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash or '', password)


class UserGroup(db.Model):
    __tablename__ = 'user_group'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('user_group.id'), nullable=True)
    user_count = db.Column(db.Integer, default=0)
    is_enabled = db.Column(db.Boolean, default=True)

    parent = db.relationship('UserGroup', remote_side=[id])

    def to_dict(self):
        count = User.query.filter_by(group_name=self.name).count()
        return {
            'id': self.id,
            'name': self.name,
            'parent_id': self.parent_id,
            'user_count': count,
            'enabled': self.is_enabled,
        }


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    permissions = db.Column(db.String(255))  # comma separated

    def to_dict(self):
        perms = self.permissions.split(',') if self.permissions else []
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'permissions': perms,
        }


class LdapServer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    type = db.Column(db.String(50))
    ldaps = db.Column(db.Boolean, default=False)
    host = db.Column(db.String(255))
    port = db.Column(db.Integer)
    dn_path = db.Column(db.String(255))
    default_user_group = db.Column(db.String(80))
    default_role = db.Column(db.String(80))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'ldaps': self.ldaps,
            'host': self.host,
            'port': self.port,
            'dn_path': self.dn_path,
            'default_user_group': self.default_user_group,
            'default_role': self.default_role,
        }

# Dummy notifications data
notifications = []

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_type = request.form.get('login_type', 'local')
        username = request.form.get('username')
        password = request.form.get('password')

        if login_type == 'ldap':
            server = LdapServer.query.first()
            if not server:
                abort(400, 'No LDAP server configured')
            try:
                ldap_server = Ldap3Server(server.host, port=server.port, use_ssl=server.ldaps, get_info=LDAP_ALL)
                conn = Ldap3Connection(ldap_server, user=username, password=password, auto_bind=True)
                conn.search(server.dn_path, f'(sAMAccountName={username})', attributes=['cn', 'mail'])
                entry = conn.entries[0] if conn.entries else None
                full_name = entry.cn.value if entry and 'cn' in entry else username
                email = entry.mail.value if entry and 'mail' in entry else f'{username}@example.com'
                conn.unbind()
            except Exception:
                return render_template('login.html', error='Invalid LDAP credentials')

            user = User.query.filter_by(principal_name=username).first()
            if not user:
                user = User(
                    name=full_name,
                    principal_name=username,
                    role=server.default_role,
                    email=email,
                    group_name=server.default_user_group,
                )
                user.set_password('')
                db.session.add(user)
            else:
                user.name = full_name
                user.email = email
        else:
            user = User.query.filter_by(principal_name=username).first()
            if not user or not user.check_password(password):
                return render_template('login.html', error='Invalid credentials')

        user.last_login = datetime.utcnow()
        user.is_logged_in = True
        db.session.commit()
        session['user_id'] = user.id
        session['role'] = user.role
        return redirect(url_for('dashboard'))

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    user = User.query.get(user_id)
    if not user:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=user)


@app.route('/users')
@admin_required
def users_page():
    role = request.args.get('role')
    group = request.args.get('group')
    query = User.query
    if role and role != 'all':
        query = query.filter_by(role=role)
    if group and group != 'all':
        query = query.filter_by(group_name=group)
    users = query.all()
    current_user = None
    if 'user_id' in session:
        current_user = User.query.get(session['user_id'])
    return render_template('users.html', users=users, username=current_user.name if current_user else None)


@app.route('/api/users', methods=['GET', 'POST'])
def api_users():
    if request.method == 'POST':
        data = request.json or {}
        group_name = data.get('group')
        if group_name:
            if not UserGroup.query.filter_by(name=group_name).first():
                abort(400, 'group does not exist')
        user = User(
            name=data.get('name'),
            principal_name=data.get('principal_name'),
            role=data.get('role'),
            email=data.get('email'),
            group_name=group_name,
            is_enabled=data.get('enabled', True)
        )
        if data.get('password'):
            user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        return jsonify(user.to_dict()), 201

    role = request.args.get('role')
    group = request.args.get('group')
    query = User.query
    if role:
        query = query.filter_by(role=role)
    if group:
        query = query.filter_by(group_name=group)
    users = [u.to_dict() for u in query.all()]
    return jsonify(users)


@app.route('/api/users/<int:user_id>/enable', methods=['PUT'])
def api_user_enable(user_id):
    user = User.query.get_or_404(user_id)
    user.is_enabled = True
    db.session.commit()
    return jsonify({'status': 'enabled'})


@app.route('/api/users/<int:user_id>/disable', methods=['PUT'])
def api_user_disable(user_id):
    user = User.query.get_or_404(user_id)
    user.is_enabled = False
    db.session.commit()
    return jsonify({'status': 'disabled'})


@app.route('/api/users/<int:user_id>', methods=['PUT', 'DELETE'])
def api_user_detail(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'PUT':
        data = request.json or {}
        user.name = data.get('name', user.name)
        user.principal_name = data.get('principal_name', user.principal_name)
        user.role = data.get('role', user.role)
        user.email = data.get('email', user.email)
        group_name = data.get('group', user.group_name)
        if group_name:
            if not UserGroup.query.filter_by(name=group_name).first():
                abort(400, 'group does not exist')
        user.group_name = group_name
        if data.get('password'):
            user.set_password(data['password'])
        user.is_enabled = data.get('enabled', user.is_enabled)
        db.session.commit()
        return jsonify(user.to_dict())

    db.session.delete(user)
    db.session.commit()
    return jsonify({'status': 'deleted'})


@app.route('/api/users/<int:user_id>/transfer', methods=['POST'])
def api_user_transfer(user_id):
    data = request.json or {}
    target_id = data.get('target_id')
    if not target_id:
        abort(400, 'target_id required')
    # Placeholder transfer logic
    return jsonify({'status': 'transferred', 'to': target_id})


@app.route('/api/users/<int:user_id>/audit')
def api_user_audit(user_id):
    # Return simple dummy audit log entries
    logs = [
        {'timestamp': datetime.utcnow().isoformat(), 'action': 'login'},
        {'timestamp': datetime.utcnow().isoformat(), 'action': 'edit profile'},
    ]
    return jsonify(logs)


@app.route('/wm/user_groups')
@admin_required
def user_groups_page():
    groups = UserGroup.query.all()
    for g in groups:
        g.user_count = User.query.filter_by(group_name=g.name).count()
    return render_template('user_groups.html', groups=groups, username='admin')


@app.route('/api/user_groups', methods=['GET', 'POST'])
def api_user_groups():
    if request.method == 'POST':
        data = request.json or {}
        group = UserGroup(
            name=data.get('name'),
            parent_id=data.get('parent_id'),
            is_enabled=data.get('enabled', True)
        )
        db.session.add(group)
        db.session.commit()
        return jsonify(group.to_dict()), 201
    groups = [g.to_dict() for g in UserGroup.query.all()]
    return jsonify(groups)


@app.route('/api/user_groups/<int:group_id>', methods=['PUT', 'DELETE'])
def api_user_group_detail(group_id):
    group = UserGroup.query.get_or_404(group_id)
    if request.method == 'PUT':
        data = request.json or {}
        group.name = data.get('name', group.name)
        group.parent_id = data.get('parent_id', group.parent_id)
        group.is_enabled = data.get('enabled', group.is_enabled)
        db.session.commit()
        return jsonify(group.to_dict())
    db.session.delete(group)
    db.session.commit()
    return jsonify({'status': 'deleted'})


@app.route('/api/user_groups/<int:group_id>/audit_log')
def api_user_group_audit(group_id):
    logs = [
        {'timestamp': datetime.utcnow().isoformat(), 'action': 'group created'},
        {'timestamp': datetime.utcnow().isoformat(), 'action': 'group edited'},
    ]
    return jsonify(logs)


@app.route('/wm/roles')
@admin_required
def roles_page():
    roles = Role.query.all()
    return render_template('roles.html', roles=roles, username='admin')


@app.route('/api/roles', methods=['GET', 'POST'])
def api_roles():
    if request.method == 'POST':
        data = request.json or {}
        role = Role(
            name=data.get('name'),
            description=data.get('description'),
            permissions=','.join(data.get('permissions', []))
        )
        db.session.add(role)
        db.session.commit()
        return jsonify(role.to_dict()), 201
    roles = [r.to_dict() for r in Role.query.all()]
    return jsonify(roles)


@app.route('/api/roles/<int:role_id>', methods=['PUT', 'DELETE'])
def api_role_detail(role_id):
    role = Role.query.get_or_404(role_id)
    if request.method == 'PUT':
        data = request.json or {}
        role.name = data.get('name', role.name)
        role.description = data.get('description', role.description)
        if 'permissions' in data:
            role.permissions = ','.join(data.get('permissions', []))
        db.session.commit()
        return jsonify(role.to_dict())
    db.session.delete(role)
    db.session.commit()
    return jsonify({'status': 'deleted'})


@app.route('/api/roles/<int:role_id>/audit_log')
def api_role_audit(role_id):
    logs = [
        {'timestamp': datetime.utcnow().isoformat(), 'action': 'role created'},
        {'timestamp': datetime.utcnow().isoformat(), 'action': 'role edited'},
    ]
    return jsonify(logs)


@app.route('/wm/ldapserver')
@admin_required
def ldapserver_page():
    servers = LdapServer.query.all()
    return render_template('ldap_servers.html', servers=servers, username='admin')


@app.route('/wm/add_ldapserver')
@admin_required
def add_ldapserver_page():
    groups = UserGroup.query.all()
    roles = Role.query.all()
    return render_template('ldap_server_form.html', action='create', groups=groups, roles=roles, username='admin')


@app.route('/wm/edit_ldapserver/<int:server_id>')
@admin_required
def edit_ldapserver_page(server_id):
    server = LdapServer.query.get_or_404(server_id)
    groups = UserGroup.query.all()
    roles = Role.query.all()
    return render_template('ldap_server_form.html', action='edit', server=server, groups=groups, roles=roles, username='admin')


@app.route('/api/ldap_servers', methods=['GET', 'POST'])
def api_ldap_servers():
    if request.method == 'POST':
        data = request.json or {}
        server = LdapServer(
            name=data.get('name'),
            type=data.get('type'),
            ldaps=data.get('ldaps', False),
            host=data.get('host'),
            port=data.get('port'),
            dn_path=data.get('dn_path'),
            default_user_group=data.get('default_user_group'),
            default_role=data.get('default_role'),
        )
        db.session.add(server)
        db.session.commit()
        return jsonify(server.to_dict()), 201
    servers = [s.to_dict() for s in LdapServer.query.all()]
    return jsonify(servers)


@app.route('/api/ldap_servers/<int:server_id>', methods=['PUT', 'DELETE'])
def api_ldap_server_detail(server_id):
    server = LdapServer.query.get_or_404(server_id)
    if request.method == 'PUT':
        data = request.json or {}
        server.name = data.get('name', server.name)
        server.type = data.get('type', server.type)
        server.ldaps = data.get('ldaps', server.ldaps)
        server.host = data.get('host', server.host)
        server.port = data.get('port', server.port)
        server.dn_path = data.get('dn_path', server.dn_path)
        server.default_user_group = data.get('default_user_group', server.default_user_group)
        server.default_role = data.get('default_role', server.default_role)
        db.session.commit()
        return jsonify(server.to_dict())
    db.session.delete(server)
    db.session.commit()
    return jsonify({'status': 'deleted'})


@app.route('/api/ldap_servers/<int:server_id>/audit_log')
def api_ldap_server_audit(server_id):
    logs = [
        {'timestamp': datetime.utcnow().isoformat(), 'action': 'server created'},
        {'timestamp': datetime.utcnow().isoformat(), 'action': 'server edited'},
    ]
    return jsonify(logs)


@app.route('/api/users/export')
def export_users():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Name', 'Principal Name', 'Role', 'Email', 'Group', 'Last Login', 'Logged In', 'Enabled'])
    for user in User.query.all():
        writer.writerow([
            user.name,
            user.principal_name,
            user.role,
            user.email,
            user.group_name,
            user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else '',
            'Yes' if user.is_logged_in else 'No',
            'Yes' if user.is_enabled else 'No'
        ])
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name='users.csv')

@app.route('/api/notifications')
def api_notifications():
    return jsonify(notifications)

@app.route('/logout')
def logout():
    user_id = session.pop('user_id', None)
    session.pop('role', None)
    if user_id:
        user = User.query.get(user_id)
        if user:
            user.is_logged_in = False
            db.session.commit()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        inspector = inspect(db.engine)
        if 'user' in inspector.get_table_names():
            cols = [c['name'] for c in inspector.get_columns('user')]
            if 'password_hash' not in cols:
                db.drop_all()
        db.create_all()
        if not UserGroup.query.first():
            default_group = UserGroup(name='Default')
            db.session.add(default_group)
        if not Role.query.first():
            default_role = Role(name='admin', description='Administrator', permissions='')
            db.session.add(default_role)
        if not User.query.filter_by(principal_name='admin').first():
            user = User(name='Admin', principal_name='admin', role='admin', email='admin@example.com', group_name='Default')
            user.set_password('admin')
            db.session.add(user)
        db.session.commit()
    # Bind to all interfaces so the server is reachable from other machines
    app.run(host='0.0.0.0', port=5000, debug=True)
