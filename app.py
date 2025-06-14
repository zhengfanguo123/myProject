from flask import Flask, jsonify, render_template, request, send_file
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

# Dummy notifications data
notifications = []

@app.route('/dashboard')
def dashboard():
    username = 'fanguo'
    return render_template('dashboard.html', username=username)


@app.route('/users')
def users_page():
    users = User.query.all()
    return render_template('users.html', users=users)


@app.route('/api/users')
def api_users():
    users = [u.to_dict() for u in User.query.all()]
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


@app.route('/export/users')
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
