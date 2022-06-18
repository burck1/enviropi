from datetime import datetime, timezone
from re import L
from zoneinfo import ZoneInfo
from flask import Flask, render_template, g, request

from db2 import SensorDB

# DATABASE = 'data.db'
DATABASE = 'envData.db'

app = Flask(__name__)

def get_db():
    db: SensorDB = getattr(g, '_database', None)
    if db is None:
        db = g._database = SensorDB(DATABASE)
        db.open()
    return db

@app.teardown_appcontext
def close_connection(exception):
    db: SensorDB = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def home():
    db = get_db()
    return render_template('home2.html.jinja', data=db.select_sensor_hourly_averages())

@app.route('/api/history')
def api_history():
    tz = request.args.get('tz', default='UTC', type=str)
    interval = request.args.get('interval', default='hourly', type=str).lower()
    if interval not in ['hourly', 'minutely']:
        raise Exception(f'Invalid interval value {interval}')
    db = get_db()
    data = None
    if interval == 'hourly':
        data = [row.to_dict() for row in db.select_sensor_hourly_averages()]
    else:
        data = [row.to_dict() for row in db.select_sensor_minutely_averages()]
    for row in data:
        ts = datetime.fromisoformat(row['ts'])
        ts = ts.replace(tzinfo=timezone.utc)
        ts = ts.astimezone(ZoneInfo(tz))
        row['ts'] = str(ts)[11:16]
    return {'data': data}
