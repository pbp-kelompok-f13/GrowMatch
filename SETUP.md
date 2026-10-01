
# Initial Setup

## Linux & MacOS

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## Windows PowerShell

```bash
py -m venv env
.\env\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Windows Command Prompt (CMD)

```bash
py -m venv env
env\Scripts\activate.bat
python -m pip install -r requirements.txt
```

# Running The Program

```bash
python manage.py check
python manage.py migrate
python manage.py runserver
```
Then, open http://127.0.0.1:8000/ on your local browser
