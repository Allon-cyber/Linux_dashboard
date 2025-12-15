# Linux Dashboard

A web-based dashboard for monitoring and managing a Linux system using Flask.

## Features

- Real-time system monitoring (CPU, memory, disk usage, uptime)
- Process monitoring (top 10 by CPU)
- Network statistics (bytes sent/received, active connections)
- System actions: shutdown, restart, update packages
- Service management: restart services, check status
- Run safe commands (ls, df, free, uptime, whoami, ps, top)
- View system logs (last 20 lines from /var/log/syslog)
- Secure password protection with setup and change options

## Requirements

- Python 3.6+
- Linux system (tested on Ubuntu/Debian)
- sudo privileges for system actions

### Installing Python

If Python is not installed on your system:

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

#### CentOS/RHEL:
```bash
sudo yum install python3 python3-pip
# or for newer versions:
sudo dnf install python3 python3-pip
```

#### Fedora:
```bash
sudo dnf install python3 python3-pip
```

#### Arch Linux:
```bash
sudo pacman -S python python-pip
```

#### Windows (for development):
Download from [python.org](https://www.python.org/downloads/) and install.

Verify installation:
```bash
python3 --version
pip3 --version
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Allon-cyber/linux_dashboard.git
   cd linux_dashboard
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the app:
   ```bash
   python app.py
   ```

## Usage

1. First run: Set up your password at `http://your_server_ip:5000/setup`
2. Login with your password at `http://your_server_ip:5000`
3. Access the dashboard with tabs for System Info, Processes, Network, and Actions

### Running in Background

To run the dashboard as a background service:

#### Option 1: Using nohup
```bash
nohup python app.py &
```

#### Option 2: Using systemd (recommended for production)
1. Create a service file `/etc/systemd/system/linux-dashboard.service`:
   ```bash
   sudo nano /etc/systemd/system/linux-dashboard.service
   ```
   Paste the following content:
   ```ini
   [Unit]
   Description=Linux Dashboard
   After=network.target

   [Service]
   Type=simple
   User=your_user
   WorkingDirectory=/path/to/linux_dashboard
   ExecStart=/path/to/linux_dashboard/.venv/bin/python app.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

2. Reload systemd and start:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl start linux-dashboard
   sudo systemctl enable linux-dashboard
   ```

The dashboard will be accessible at `http://your-server-ip:5000`.

## Security

- Password is stored locally in `password.json` (excluded from git)
- Actions requiring sudo must be run with elevated privileges
- For production, consider adding HTTPS and IP restrictions
- This is a basic implementation - not recommended for public servers without additional security measures

## Warning

Actions like shutdown, restart, and service management can affect system stability. Use with caution and ensure you have backup access methods.

## License

MIT License