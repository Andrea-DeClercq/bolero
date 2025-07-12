#!/usr/bin/env python
"""
DOC
"""
# Import from stdlib
from datetime import datetime

# Imports from external libraries
import arrow
from path import Path
from tinydb import TinyDB, Query

# Import from local code


class LittleDB:
    """Extension Flask pour tinydb"""

    def __init__(self, app=None):
        self.app = app
        self.tinydb = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.littledb = self
        db_path = Path(app.config.littledb).expand().absolute()
        self.tinydb = TinyDB(db_path.absolute())

    def _get_table_cls(self, name):
        if name == "last_execution":
            return ArrowLittleDBTable
        return LittleDBTable

    def __getattr__(self, key):
        table_cls = self._get_table_cls(key)
        return table_cls(self.tinydb.table(key))

    def __getitem__(self, key):
        return getattr(self, key)


class LittleDBTable:
    def __init__(self, tinydb_table):
        self._table = tinydb_table
        self._query = Query()

    def _encode_value(self, value):
        return value

    def _decode_value(self, value):
        return value

    def __getattr__(self, key):
        value = self._table.get(self._query["key"] == key)
        if value:
            value = value["value"]
            value = self._decode_value(value)
        return value

    def __getitem__(self, key):
        return getattr(self, key)

    def __setattr__(self, key, value):
        if key.startswith("_"):
            self.__dict__[key] = value
            return
        self._table.upsert(
            {
                "key": key,
                "value": self._encode_value(value),
            },
            self._query["key"] == key,
        )

    def __setitem__(self, key, value):
        return setattr(self, key, value)


class ArrowLittleDBTable(LittleDBTable):
    def _encode_value(self, arrow_date):
        if isinstance(arrow_date, datetime):
            arrow_date = arrow.get(datetime)
        return arrow_date.to("utc").format("YYYY-MM-DD HH:mm:ss")

    def _decode_value(self, string_date):
        string_date = arrow.get(string_date, "YYYY-MM-DD HH:mm:ss")
        return string_date.to("local")

    def set_now(self, key):
        return setattr(self, key, arrow.utcnow())
