import sqlite3

from datetime import datetime
from collections.abc import Iterable
from typing import Generator

SQL_CREATE_TABLE_SENSOR = '''
create table if not exists sensor (
    ts timestamp primary key,
    temperature real,
    pressure real,
    humidity real,
    light real,
    oxidised real,
    reduced real,
    nh3 real,
    pm1 real,
    pm25 real,
    pm10 real
)
'''

SQL_CREATE_TABLES = [
    SQL_CREATE_TABLE_SENSOR,
]

SQL_INSERT_SENSOR = '''
insert into sensor values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
'''

SQL_SELECT_SENSOR = '''
select ts, temperature, pressure, humidity, light, oxidised, reduced, nh3, pm1, pm25, pm10 from sensor limit :limit
'''

SQL_SELECT_SENSOR_MINUTELY_AVERAGES = '''
select
    strftime('%Y-%m-%d %H:%M:00', ts) as ts,
    round(avg(temperature), 1) as temperature,
    round(avg(pressure), 1) as pressure,
    round(avg(humidity), 1) as humidity,
    round(avg(light), 1) as light,
    round(avg(oxidised), 1) as oxidised,
    round(avg(reduced), 1) as reduced,
    round(avg(nh3), 1) as nh3,
    round(avg(pm1), 1) as pm1,
    round(avg(pm25), 1) as pm25,
    round(avg(pm10), 1) as pm10
from sensor
where ts > datetime('now', '-1 days')
group by strftime('%Y-%m-%d %H:%M:00', ts)
order by ts desc
'''

SQL_SELECT_SENSOR_HOURLY_AVERAGES = '''
select
    strftime('%Y-%m-%d %H:00:00', ts) as ts,
    round(avg(temperature), 1) as temperature,
    round(avg(pressure), 1) as pressure,
    round(avg(humidity), 1) as humidity,
    round(avg(light), 1) as light,
    round(avg(oxidised), 1) as oxidised,
    round(avg(reduced), 1) as reduced,
    round(avg(nh3), 1) as nh3,
    round(avg(pm1), 1) as pm1,
    round(avg(pm25), 1) as pm25,
    round(avg(pm10), 1) as pm10
from sensor
where ts > datetime('now', '-1 days')
group by strftime('%Y-%m-%d %H:00:00', ts)
order by ts desc
'''

class SensorRow:
    def __init__(self, ts=None, temperature=None, pressure=None, humidity=None, light=None, oxidised=None, reduced=None, nh3=None, pm1=None, pm25=None, pm10=None):
        self.ts = ts
        if not self.ts:
            self.ts = datetime.now()
        self.temperature = temperature
        self.pressure = pressure
        self.humidity = humidity
        self.light = light
        self.oxidised = oxidised
        self.reduced = reduced
        self.nh3 = nh3
        self.pm1 = pm1
        self.pm25 = pm25
        self.pm10 = pm10

    def to_tuple(self):
        return (
            self.ts,
            self.temperature,
            self.pressure,
            self.humidity,
            self.light,
            self.oxidised,
            self.reduced,
            self.nh3,
            self.pm1,
            self.pm25,
            self.pm10,
        )

    def to_dict(self):
        return {
            'ts': self.ts,
            'temperature': self.temperature,
            'pressure': self.pressure,
            'humidity': self.humidity,
            'light': self.light,
            'oxidised': self.oxidised,
            'reduced': self.reduced,
            'nh3': self.nh3,
            'pm1': self.pm1,
            'pm25': self.pm25,
            'pm10': self.pm10,
        }

    @classmethod
    def from_row(cls, row: sqlite3.Row):
        return cls(
            row['ts'],
            row['temperature'],
            row['pressure'],
            row['humidity'],
            row['light'],
            row['oxidised'],
            row['reduced'],
            row['nh3'],
            row['pm1'],
            row['pm25'],
            row['pm10'],
        )

class SensorDB:
    def __init__(self, path=':memory:'):
        self._path = path
        self._connection = None

    def open(self):
        if self._connection:
            raise Exception('One connection at a time')
        self._connection = sqlite3.connect(self._path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        self._connection.row_factory = sqlite3.Row
        with self._connection:
            for sql in SQL_CREATE_TABLES:
                self._connection.execute(sql)

    def close(self):
        if self._connection:
            self._connection.close()
            self._connection = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    def insert_sensor_row(self, row: SensorRow):
        with self._connection:
            return self._connection.execute(SQL_INSERT_SENSOR, row.to_tuple())

    def insert_sensor_rows(self, rows: Iterable[SensorRow]):
        with self._connection:
            self._connection.executemany(SQL_INSERT_SENSOR, (row.to_tuple() for row in rows))

    def select_sensor_rows(self, limit=1000) -> Generator[SensorRow, None, None]:
        with self._connection:
            for row in self._connection.execute(SQL_SELECT_SENSOR, {'limit':limit}):
                yield SensorRow.from_row(row)

    def select_sensor_minutely_averages(self) -> Generator[SensorRow, None, None]:
        with self._connection:
            for row in self._connection.execute(SQL_SELECT_SENSOR_MINUTELY_AVERAGES):
                yield SensorRow.from_row(row)

    def select_sensor_hourly_averages(self) -> Generator[SensorRow, None, None]:
        with self._connection:
            for row in self._connection.execute(SQL_SELECT_SENSOR_HOURLY_AVERAGES):
                yield SensorRow.from_row(row)
