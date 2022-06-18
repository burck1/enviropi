import sqlite3

from datetime import datetime
from collections.abc import Iterable
from typing import Generator

SQL_CREATE_TABLE_SENSOR = '''
create table if not exists sensor (
    time integer unique,
    temp real,
    hum real,
    pres real,
    light real,
    oxi real,
    reduc real,
    primary key(time)
)
'''

SQL_CREATE_TABLES = [
    SQL_CREATE_TABLE_SENSOR,
]

SQL_INSERT_SENSOR = '''
insert into sensor values (unixepoch(?), ?, ?, ?, ?, ?, ?)
'''

SQL_SELECT_SENSOR = '''
select datetime(time, 'unixepoch') as ts, temp, hum, pres, light, oxi, reduc from sensor limit :limit
'''

SQL_SELECT_SENSOR_MINUTELY_AVERAGES = '''
select
    strftime('%Y-%m-%d %H:%M:00', datetime(time, 'unixepoch')) as ts,
    round(avg(temp), 1) as temp,
    round(avg(hum), 1) as hum,
    round(avg(pres), 1) as pres,
    round(avg(light), 1) as light,
    round(avg(oxi), 1) as oxi,
    round(avg(reduc), 1) as reduc
from sensor
where datetime(time, 'unixepoch') > datetime('now', '-1 days')
group by strftime('%Y-%m-%d %H:%M:00', datetime(time, 'unixepoch'))
order by ts asc
'''

SQL_SELECT_SENSOR_HOURLY_AVERAGES = '''
select
    strftime('%Y-%m-%d %H:00:00', datetime(time, 'unixepoch')) as ts,
    round(avg(temp), 1) as temp,
    round(avg(hum), 1) as hum,
    round(avg(pres), 1) as pres,
    round(avg(light), 1) as light,
    round(avg(oxi), 1) as oxi,
    round(avg(reduc), 1) as reduc
from sensor
where datetime(time, 'unixepoch') > datetime('now', '-1 days')
group by strftime('%Y-%m-%d %H:00:00', datetime(time, 'unixepoch'))
order by ts asc
'''

class SensorRow:
    def __init__(self, ts=None, temp=None, hum=None, pres=None, light=None, oxi=None, reduc=None):
        self.ts = ts
        if not self.ts:
            self.ts = datetime.now()
        self.temp = temp
        self.hum = hum
        self.pres = pres
        self.light = light
        self.oxi = oxi
        self.reduc = reduc

    def to_tuple(self):
        return (
            self.ts,
            self.temp,
            self.hum,
            self.pres,
            self.light,
            self.oxi,
            self.reduc,
        )

    def to_dict(self):
        return {
            'ts': self.ts,
            'temp': self.temp,
            'hum': self.hum,
            'pres': self.pres,
            'light': self.light,
            'oxi': self.oxi,
            'reduc': self.reduc,
        }

    @classmethod
    def from_row(cls, row: sqlite3.Row):
        return cls(
            row['ts'],
            row['temp'],
            row['hum'],
            row['pres'],
            row['light'],
            row['oxi'],
            row['reduc'],
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
