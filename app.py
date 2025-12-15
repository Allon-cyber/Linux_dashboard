from flask import Flask, render_template, jsonify, request, redirect, url_for, session
import psutil
import subprocess
import os
import json
from functools import wraps

app = Flask(__name__)
app.secret_key = 'linux_dashboard_secret_2025'

PASSWORD_FILE = 'password.json'

def get_password():
    if os.path.exists(PASSWORD_FILE):
        with open(PASSWORD_FILE, 'r') as f:
            data = json.load(f)
            return data.get('password')
    return None

def set_password(password):
    with open(PASSWORD_FILE, 'w') as f:
        json.dump({'password': password}, f)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'authenticated' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if get_password() is not None:
        return redirect(url_for('login'))
    if request.method == 'POST':
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        if password and password == confirm:
            set_password(password)
            return redirect(url_for('login'))
        else:
            return render_template('setup.html', error='Passwords do not match')
    return render_template('setup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if get_password() is None:
        return redirect(url_for('setup'))
    if request.method == 'POST':
        password = request.form.get('password')
        if password == get_password():
            session['authenticated'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current = request.form.get('current')
        new = request.form.get('new')
        confirm = request.form.get('confirm')
        if current == get_password() and new == confirm:
            set_password(new)
            return redirect(url_for('index'))
        else:
            return render_template('change_password.html', error='Invalid current password or passwords do not match')
    return render_template('change_password.html')

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/api/system_info')
@login_required
def system_info():
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    uptime = psutil.boot_time()
    from datetime import datetime
    uptime_str = str(datetime.now() - datetime.fromtimestamp(uptime)).split('.')[0]
    return jsonify({
        'cpu': cpu,
        'memory': {
            'total': memory.total // (1024**2),  # MB
            'used': memory.used // (1024**2),
            'percent': memory.percent
        },
        'disk': {
            'total': disk.total // (1024**3),  # GB
            'used': disk.used // (1024**3),
            'percent': disk.percent
        },
        'uptime': uptime_str
    })

@app.route('/api/processes')
@login_required
def processes():
    procs = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            procs.append({
                'pid': proc.info['pid'],
                'name': proc.info['name'],
                'cpu': proc.info['cpu_percent'] or 0,
                'memory': proc.info['memory_percent'] or 0
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    # Sort by CPU usage descending, take top 10
    procs.sort(key=lambda x: x['cpu'], reverse=True)
    return jsonify(procs[:10])

@app.route('/api/network')
@login_required
def network():
    net_io = psutil.net_io_counters()
    connections = len(psutil.net_connections())
    return jsonify({
        'sent': net_io.bytes_sent // (1024**2),  # MB
        'recv': net_io.bytes_recv // (1024**2),
        'connections': connections
    })

@app.route('/api/shutdown', methods=['POST'])
@login_required
def shutdown():
    if request.method == 'POST':
        try:
            subprocess.run(['sudo', 'shutdown', 'now'], check=True)
            return jsonify({'status': 'success', 'message': 'System shutting down'})
        except subprocess.CalledProcessError as e:
            return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/restart', methods=['POST'])
@login_required
def restart():
    if request.method == 'POST':
        try:
            subprocess.run(['sudo', 'reboot'], check=True)
            return jsonify({'status': 'success', 'message': 'System restarting'})
        except subprocess.CalledProcessError as e:
            return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/restart_service', methods=['POST'])
@login_required
def restart_service():
    service = request.json.get('service')
    if not service:
        return jsonify({'status': 'error', 'message': 'Service name required'})
    try:
        subprocess.run(['sudo', 'systemctl', 'restart', service], check=True)
        return jsonify({'status': 'success', 'message': f'Service {service} restarted'})
    except subprocess.CalledProcessError as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/service_status', methods=['POST'])
@login_required
def service_status():
    service = request.json.get('service')
    if not service:
        return jsonify({'status': 'error', 'message': 'Service name required'})
    try:
        result = subprocess.run(['systemctl', 'is-active', service], capture_output=True, text=True)
        status = result.stdout.strip()
        return jsonify({'status': 'success', 'message': f'Service {service} is {status}'})
    except subprocess.CalledProcessError as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/run_command', methods=['POST'])
@login_required
def run_command():
    command = request.json.get('command')
    if not command:
        return jsonify({'status': 'error', 'message': 'Command required'})
    # Security: allow only safe commands
    allowed_commands = ['ls', 'df', 'free', 'uptime', 'whoami', 'ps', 'top -n 1']
    if command not in allowed_commands and not command.startswith('ls ') and not command.startswith('df ') and not command.startswith('free ') and not command.startswith('uptime ') and not command.startswith('whoami ') and not command.startswith('ps ') and not command.startswith('top '):
        return jsonify({'status': 'error', 'message': 'Command not allowed'})
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return jsonify({'status': 'success', 'output': result.stdout or result.stderr})
    except subprocess.CalledProcessError as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/view_logs')
@login_required
def view_logs():
    try:
        result = subprocess.run(['tail', '-20', '/var/log/syslog'], capture_output=True, text=True)
        return jsonify({'status': 'success', 'logs': result.stdout})
    except subprocess.CalledProcessError as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
