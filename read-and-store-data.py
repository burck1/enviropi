from datetime import datetime, timedelta
from vnoise import Noise
from db import SensorDB, SensorRow

SECONDS_PER_DAY = 86400

def main():
    noise = Noise()
    print('Writing Data')
    with SensorDB('data.db') as db:
        now = datetime.now()
        now = now.replace(microsecond=0)
        db.insert_sensor_rows((SensorRow(now - timedelta(seconds=i), round(37.4 + (noise.noise1(i / SECONDS_PER_DAY) * 100), 2), 10.1, 40.6, 0.75, 0.12, 0.22, 0.33, 0.44, 0.55, 0.66) for i in range(SECONDS_PER_DAY, 0, -1)))
        # db.insert_sensor_rows([
        #     SensorRow(now - timedelta(seconds=9), 37.4, 10.1, 40.6, 0.75, 0.12, 0.22, 0.33, 0.44, 0.55, 0.66),
        #     SensorRow(now - timedelta(seconds=8), 37.3, 10.1, 40.6, 0.75, 0.12, 0.22, 0.33, 0.44, 0.55, 0.66),
        #     SensorRow(now - timedelta(seconds=7), 37.2, 10.1, 40.6, 0.75, 0.12, 0.22, 0.33, 0.44, 0.55, 0.66),
        #     SensorRow(now - timedelta(seconds=6), 37.1, 10.1, 40.6, 0.75, 0.12, 0.22, 0.33, 0.44, 0.55, 0.66),
        #     SensorRow(now - timedelta(seconds=5), 37.2, 10.1, 40.6, 0.75, 0.12, 0.22, 0.33, 0.44, 0.55, 0.66),
        #     SensorRow(now - timedelta(seconds=4), 37.3, 10.1, 40.6, 0.75, 0.12, 0.22, 0.33, 0.44, 0.55, 0.66),
        #     SensorRow(now - timedelta(seconds=3), 37.4, 10.1, 40.6, 0.75, 0.12, 0.22, 0.33, 0.44, 0.55, 0.66),
        #     SensorRow(now - timedelta(seconds=2), 37.5, 10.1, 40.6, 0.75, 0.12, 0.22, 0.33, 0.44, 0.55, 0.66),
        #     SensorRow(now - timedelta(seconds=1), 37.6, 10.1, 40.6, 0.75, 0.12, 0.22, 0.33, 0.44, 0.55, 0.66),
        #     SensorRow(now, 37.7, 10.1, 40.6, 0.75, 0.12, 0.22, 0.33, 0.44, 0.55, 0.66),
        # ])

if __name__ == '__main__':
    main()
