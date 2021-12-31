import random
from collections import defaultdict

from shapely.geometry import Point

from db import DB


def hist(array):
    out = {}
    out = defaultdict(lambda: 0, out)
    for item in array:
        out[item] += 1
    out = dict(sorted(out.items(), key=lambda a: a[1], reverse=True))
    return out


if __name__ == "__main__":
    db = DB()
    df = db.get_items()
    current_point = Point(37.572631, 55.745983, )
    items_in_point = df[df.contains(current_point)]
    print(items_in_point)
    random_list = random.choices(items_in_point['images'], weights=items_in_point['max_rate'], k=100000)
    print(hist(random_list))
