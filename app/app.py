import os, json, pymysql
from datetime import datetime
from flask import Flask, render_template, request, url_for, redirect, flash
from dotenv import load_dotenv
from pathlib import Path
from celery import Celery

APP_ROOT = os.path.join(os.path.dirname(__file__), '.')   # refers to application_top
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET')

# Celery configuration
redis_uri = 'redis://{}:{}/0'.format(os.getenv('REDIS_HOST'),os.getenv('REDIS_PORT'))

# Celery configuration
app.config['CELERY_BROKER_URL'] = redis_uri
app.config['CELERY_RESULT_BACKEND'] = redis_uri


# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)



class MySQL:

    host = os.getenv('MYSQL_HOST')
    user = os.getenv('MYSQL_USER')
    password = os.getenv('MYSQL_PASS')
    db = os.getenv('MYSQL_DB')
    con = pymysql.connect(host=host, user=user, password=password, db=db, cursorclass=pymysql.cursors.
                                DictCursor)
    cur = con.cursor()

    def insert_data(self, time, temperature, server_time):
        sql = "INSERT INTO `data` (`time`, `temperature`, `server_time`) VALUES (%s, %s, %s)"
        self.cur.execute(sql, (time, temperature, server_time))
        self.con.commit()


@celery.task
def save(request_data):
    db = MySQL()
    db.insert_data(request_data.time,request_data.temperature, request_data.server_time)



@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        return render_template('index.html')

    temperature =  float((request.form['temperature']).replace(',','.'))
    server_time = datetime.now().strftime('%Y%m%d%H%M%S')
    time = datetime.strptime(request.form['time'],'%Y-%m-%d %H:%M:%S').strftime('%Y%m%d%H%M%S')
    
    request_data = {
        'temperature': temperature,
        'time': time,
        'server_time': server_time
    }

    save.apply_async(args=[request_data], countdown=60)
    flash('A record will be sent in a minute')
    return redirect(url_for('home'))


if __name__ == '__main__':
    # Initialize Celery
    celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    app.secret_key = app.config['SECRET_KEY']
    app.run(host="localhost", port=8000, debug=True)