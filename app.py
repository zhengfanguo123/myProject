from flask import Flask, jsonify, render_template

app = Flask(__name__)

# Dummy notifications data
notifications = []

@app.route('/dashboard')
def dashboard():
    username = 'fanguo'
    return render_template('dashboard.html', username=username)

@app.route('/api/notifications')
def api_notifications():
    return jsonify(notifications)

if __name__ == '__main__':
    app.run(debug=True)
