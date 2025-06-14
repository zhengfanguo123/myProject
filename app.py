from flask import Flask, jsonify, render_template, request, send_file, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import csv
import io

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    principal_name = db.Column(db.String(120))
    role = db.Column(db.String(80))
    email = db.Column(db.String(120))
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

# Dummy notifications data
notifications = []

@app.route('/dashboard')
def dashboard():
    username = 'fanguo'
    return render_template('dashboard.html', username=username)


@app.route('/users')
def users_page():
    role = request.args.get('role')
    group = request.args.get('group')
    query = User.query
    if role and role != 'all':
        query = query.filter_by(role=role)
    if group and group != 'all':
        query = query.filter_by(group_name=group)
    users = query.all()
    return render_template('users.html', users=users, username='admin')


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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
