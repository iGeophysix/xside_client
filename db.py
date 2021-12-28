import json
import sqlite3
from random import random

import geopandas as gpd
import pandas as pd
from shapely.geometry import shape, Point


class DB:
    """DB connector"""

    def __init__(self):
        self._conn = sqlite3.connect('local.db')

    def create_items_table(self):
        """
        Recreate table with items
        """
        c = self._conn.cursor()
        c.execute("drop table if exists items;")
        c.execute("""create table items
                     (
                         id   integer
                             constraint items_pk
                                 primary key,
                         data json
                     );""")
        c.close()

    def commit(self):
        """Commit changes to DB"""
        self._conn.commit()

    def add_items(self, items):
        """Add items info. items must contain id field - will be used as pk"""
        c = self._conn.cursor()
        for item in items:
            item_id = item["id"]
            c.execute("Insert into items (id, data) values (?, ?)",
                      [item_id, json.dumps(item)])
        self.commit()
        c.close()

    def get_items(self):
        """
        Get all items
        """
        sql = """select id,
       json_extract(data, '$.areas') as areas,
       json_extract(data, "$.name") as name,
       json_extract(data, "$.max_rate") as max_rate,
       json_extract(data, "$.images") as images from items;"""
        df = pd.read_sql(sql, self._conn)
        df['areas'] = df['areas'].apply(json.loads).apply(shape)
        gdf = gpd.GeoDataFrame(df, geometry='areas')
        return gdf


if __name__ == "__main__":
    def add_dummy_data():
        db = DB()
        db.create_items_table()
        test_items = [
            {'id': id,
             'client': 'Client1',
             'name': f'TestItem{id}',
             'areas': {'type': 'MultiPolygon', 'coordinates': [[[[37.53638963683332, 55.76877240107082],
                                                                 [37.53296814303996, 55.73951490339483],
                                                                 [37.59325530537307, 55.73839870521004],
                                                                 [37.592354938387864, 55.76150288793271],
                                                                 [37.53638963683332, 55.76877240107082]]]]},
             'is_active': True,
             'max_rate': round(random() * 100 + 10, 2),
             'max_daily_spend': 100.0,
             'images': ['images/Client1/TestItem1/Cambdridge.jpg']}
            for id in range(10)
        ]
        db.add_items(test_items)


    db = DB()
    df = db.get_items()
    current_point = Point(37.558538, 55.746994, )
    print(df[df.contains(current_point)])  # show items containing current_point
