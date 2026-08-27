# World Time Application - Setup Guide

## Prerequisites Installation

### macOS
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python and Git
brew install python git
```

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv git -y
```

### Windows
1. **Python**: Download from [python.org](https://www.python.org/downloads/) (check "Add Python to PATH")
2. **Git**: Download from [git-scm.com](https://git-scm.com/download/win)

---

## Application Setup

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd wt-2
```

### 2. Create Virtual Environment
**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Fetch Weather Data (Optional)
```bash
python3 weather.py
```
*Skip this step to run without weather data*

### 5. Run Application
**macOS/Linux:**
```bash
python3 app.py
```

**Windows:**
```cmd
python app.py
```

### 6. Access Application
Open browser: **http://localhost:5001**

---

## Quick Start Scripts

### macOS/Linux (`start.sh`)
```bash
#!/bin/bash
source venv/bin/activate
python3 app.py
```
Make executable: `chmod +x start.sh`

### Windows (`start.bat`)
```cmd
@echo off
call venv\Scripts\activate
python app.py
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 5001 in use | Edit `app.py` line 628 to change port |
| Weather not showing | Run `python3 weather.py` |
| Command not found | Ensure venv is activated |
| Permission denied | Use `sudo` (Linux) or run as Administrator (Windows) |

---

## Stopping the Application
Press `Ctrl+C` in the terminal

## Deactivating Virtual Environment
```bash
deactivate
