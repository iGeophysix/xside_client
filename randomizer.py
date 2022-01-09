import json
from collections import defaultdict
from random import choices

from geopandas import GeoDataFrame
from shapely.geometry import Point

from db import DB


def hist(array):
    out = {}
    out = defaultdict(lambda: 0, out)
    for item in array:
        out[item] += 1
    out = dict(sorted(out.items(), key=lambda a: a[1], reverse=True))
    return out


def get_image_in_point(gdf: GeoDataFrame, point: Point) -> str:
    """
    Get image path to show in current point
    """
    items_in_point = gdf[gdf.contains(point)]
    items = items_in_point.set_index('id')[['max_rate', 'images']].to_dict()
    image_id = choices(list(items['max_rate'].keys()), weights=items['max_rate'].values())[0]
    images = json.loads(items['images'][image_id])
    return choices(images)[0]


if __name__ == "__main__":
    db = DB()
    df = db.get_items()
    current_point = Point(37.572631, 55.745983, )
    random_list = [get_image_in_point(df, current_point) for _ in range(1000)]
    print(hist(random_list))
