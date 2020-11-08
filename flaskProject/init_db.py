import pymongo
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from pymongo.errors import BulkWriteError


# 顾名思义
def init_db(treasures):
    treasures_name = [{"name": "10级工具", "property": "T", "level": 10},
                      {"name": "9级工具", "property": "T", "level": 9},
                      {"name": "8级工具", "property": "T", "level": 8},
                      {"name": "7级工具", "property": "T", "level": 7},
                      {"name": "6级工具", "property": "T", "level": 6},
                      {"name": "5级工具", "property": "T", "level": 5},
                      {"name": "4级工具", "property": "T", "level": 4},
                      {"name": "3级工具", "property": "T", "level": 3},
                      {"name": "2级工具", "property": "T", "level": 2},
                      {"name": "1级工具", "property": "T", "level": 1},
                      {"name": "10级饰品", "property": "A", "level": 10},
                      {"name": "9级饰品", "property": "A", "level": 9},
                      {"name": "8级饰品", "property": "A", "level": 8},
                      {"name": "7级饰品", "property": "A", "level": 7},
                      {"name": "6级饰品", "property": "A", "level": 6},
                      {"name": "5级饰品", "property": "A", "level": 5},
                      {"name": "4级饰品", "property": "A", "level": 4},
                      {"name": "3级饰品", "property": "A", "level": 3},
                      {"name": "2级饰品", "property": "A", "level": 2},
                      {"name": "1级饰品", "property": "A", "level": 1},

                      ]
    # 建立unique索引
    treasures.create_index([("name", pymongo.ASCENDING)], unique=True)
    try:
        treasures.insert_many(treasures_name)
        print("宝物信息库已更新")
    except BulkWriteError or DuplicateKeyError:
        print("宝物信息库重复更新")


def init_pic_db(pictures):
    pictest = [{"name": "10级工具.jpg"},
               {"name": "9级工具.jpg"},
               {"name": "8级工具.jpg"},
               {"name": "7级工具.jpg"},
               {"name": "6级工具.jpg"},
               {"name": "5级工具.jpg"},
               {"name": "4级工具.jpg"},
               {"name": "3级工具.jpg"},
               {"name": "2级工具.jpg"},
               {"name": "1级工具.jpg"},
               {"name": "10级饰品.jpg"},
               {"name": "9级饰品.jpg"},
               {"name": "8级饰品.jpg"},
               {"name": "7级饰品.jpg"},
               {"name": "6级饰品.jpg"},
               {"name": "5级饰品.jpg"},
               {"name": "4级饰品.jpg"},
               {"name": "3级饰品.jpg"},
               {"name": "2级饰品.jpg"},
               {"name": "1级饰品.jpg"},
               ]
    pictures.insert_many(pictest)


if __name__ == "__main__":
    client = MongoClient('localhost', 27017)
    players = client.webgame.players
    markets = client.webgame.markets
    treasures = client.webgame.treasures
    init_db(treasures)

    pictures = client.webgame.picurls
    init_pic_db(pictures)
