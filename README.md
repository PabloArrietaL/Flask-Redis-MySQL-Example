# Flask-Redis-MySQL-Example

## Setup for development

Install the dependencies (run the following command in the app directory).
```bash
pip install -r requirements.txt
```
Run the following command to start the app.
```bash
python app.py
```
Run the following command to start the Celery server.
```bash
celery worker -A app.celery --loglevel=info --pool=solo
```

To stop it just press CTRL + C.
