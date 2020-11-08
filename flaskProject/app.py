import random
import sys

import pymongo
import json
from pymongo import MongoClient
from flask import Flask, render_template, request
from flask import jsonify
from flask_apscheduler import APScheduler

client = MongoClient('localhost', 27017)

# 声明数据集
players = client.webgame.players
markets = client.webgame.markets
treasures = client.webgame.treasures
pictures = client.webgame.picurls
app = Flask(__name__)
# 为了防止json中文乱码请加入这两行
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_MIMETYPE'] = "application/json;charset=utf-8"


# 默认访问登录页
@app.route("/", methods=['GET'])
def game_start():
    return render_template('index.html')


@app.route('/json', methods=['POST'])
def json_process():
    treasure_j = 'test'
    treasure2_j = 'test'
    price_j = 0
    json_info = request.get_data(as_text=True)

    dict1 = json.loads(json_info)
    username_j = dict1["username"]
    operation_j = dict1["operation"]
    if "treasure" in dict1.keys():
        treasure_j = dict1["treasure"]
    if "treasure2" in dict1.keys():
        treasure2_j = dict1["treasure2"]
    if "price" in dict1.keys():
        price_j = dict1["price"]

    return find_method(username_j, operation_j, treasure_j, treasure2_j, price_j)


@app.route('/test', methods=['POST', 'GET'])
def test():
    return jsonify({"username": "qk"})


# 以下是不同表单的处理函数，跳转到对应的后端函数中
@app.route('/process', methods=['POST', 'GET'])
def process():
    if request.method == 'POST':
        username = request.form.get("Name")
        password = request.form.get("Password")
        return login(username, password)


@app.route('/process_box', methods=['POST', 'GET'])
def process_box():
    if request.method == 'POST':
        username = request.form.get("Name")
        return look_box(username)


@app.route('/process_market', methods=['POST', 'GET'])
def process_market():
    if request.method == 'POST':
        username = request.form.get("Name")
        return look_market(username)


@app.route('/process_wear', methods=['POST', 'GET'])
def process_wear():
    if request.method == 'POST':
        username = request.form.get("Name")
        treasure = request.form.get("Treasure")
        return wear(username, treasure)


@app.route('/process_buy', methods=['POST', 'GET'])
def process_buy():
    if request.method == 'POST':
        username = request.form.get("Name")
        treasure = request.form.get("Treasure")
        return buy(username, treasure)


@app.route('/process_sell', methods=['POST', 'GET'])
def process_sell():
    if request.method == 'POST':
        username = request.form.get("Name")
        treasure = request.form.get("Treasure")
        price = request.form.get("Price")
        return sell(username, treasure, price)


@app.route('/process_withdraw', methods=['POST', 'GET'])
def process_withdraw():
    if request.method == 'POST':
        username = request.form.get("Name")
        treasure = request.form.get("Treasure")
        return withdraw(username, treasure)


@app.route('/process_merge', methods=['POST', 'GET'])
def process_merge():
    if request.method == 'POST':
        username = request.form.get("Name")
        treasure = request.form.get("Treasure")
        treasure2 = request.form.get("Treasure2")
        return merge(username, treasure, treasure2)


@app.route('/process_finish', methods=['POST', 'GET'])
def process_finish():
    if request.method == 'POST':
        username = request.form.get("Name")
        return finish(username)


@app.route('/process_pic', methods=['POST', 'GET'])
def process_pic():
    if request.method == 'POST':
        pic_url = request.form.get("Treasure")
        pic_url = pic_url + ".jpg"
        return pic_find(pic_url)


@app.route('/picture/<string:pic_url>', methods=['POST', 'GET'])
def pic_find(pic_url):
    if pictures.find_one({"name": pic_url}) is None:
        return "<h1>找不到该图片信息</h1>"
    return render_template('picture.html', Name=pic_url)


# 根据不同参数设置不同路由，用于url的访问
@app.route("/<string:username>/<string:operation>", methods=['GET'])
@app.route("/<string:username>/<string:operation>/<string:treasure>", methods=['GET'])
@app.route("/<string:username>/<string:operation>/<string:treasure>/<int:price>", methods=['GET'])
@app.route("/<string:username>/<string:operation>/<string:treasure>/<string:treasure2>", methods=['GET'])
# 一个中转站根据路由进行重定向
def find_method(username, operation, treasure='test', treasure2='test', price=0):
    if operation == 'login':
        return login(username, "123456")
    elif operation == 'box':
        return look_box(username)
    elif operation == 'market':
        return look_market(username)
    elif operation == 'wear':
        return wear(username, treasure)
    elif operation == 'buy':
        return buy(username, treasure)
    elif operation == 'withdraw':
        return withdraw(username, treasure)
    elif operation == 'sell':
        return sell(username, treasure, price)
    elif operation == 'merge':
        return merge(username, treasure, treasure2)
    elif operation == 'finish':
        return finish(username)
    else:
        return "<h1>输入或操作错误</h1>"


# 如果宝箱充满系统回收等级最低宝物
def recovery_treasure(name):
    box = players.find_one({"name": name})['box']
    treasure_name = box[0]
    level = treasures.find_one({"name": box[0]})['level']
    # 找到等级最低宝物
    for treasure in box[1:]:
        temp = treasures.find_one({"name": treasure})['level']
        if temp < level:
            level = temp
            treasure_name = treasure
    # 删除该宝物
    for treasure in box:
        if treasure == treasure_name:
            box.remove(treasure)
            break
    # 更新宝箱
    players.update_one({'name': name}, {"$set": {"box": box}})
    print("玩家 %-6s 被系统回收宝物 %-6s" % (name, treasure_name))


# 处理每个操作返回的结果,
def show_dict(dictionary):
    dict_ = {}
    for key in dictionary.keys():
        if key != '_id' and key != "password":
            dict_[key] = dictionary[key]
    return dict_


# 登录，转到用户主页
def login(username, password):
    players.create_index([("name", pymongo.ASCENDING)], unique=True)
    if players.find_one({"name": username}) is None:
        return register(username, password)
    else:
        if players.find_one({"name": username})['password'] != password:
            return "<h1>玩家 %s 密码错误请重新输入</h1>" % username
        user_dict = str(show_dict(players.find_one({"name": username})))
        return render_template('game.html', Name=username, Userdict=user_dict)


# 注册
def register(username, password):
    var = players.insert_one({"name": username, "money": 1000, "password": password,
                              "treasure": {"T": "1级工具", "A": "1级饰品"},
                              "box": []}).inserted_id
    return "<h1>玩家 %s 注册成功，请返回登录页面</h1>" % username + "<br><br>"


def look_box(username):
    answer = show_dict(players.find_one({"name": username}))

    answer["answer"] = "这是%s的box返回结果：" % username

    return jsonify(answer)


# 浏览市场
def look_market(username):
    # 没找到用户
    if players.find_one({"name": username}) is None:
        return "<h1>请先注册用户</h1>"
    # 显示market
    res = {
        "answer": "玩家%s查看市场" % username
    }
    for treasure in markets.find():
        res["%s" % treasure["_id"]] = show_dict(treasure)
    return jsonify(res)


'''
    res = ''
    for treasure in markets.find():
        res += str(show_dict(treasure))
        res += '<br><br>'
    return "<h1>玩家 %s 查看市场</h1>" % username + "<br><br>" + res
'''


# 佩戴宝物
def wear(username, treasure):
    # box中没有该宝物
    if treasures.find_one({"name": treasure}) is None:
        return jsonify({"error": "该宝物名不存在"})
        '''
        return "<h1>宝物库中没有 %s 宝物</h1>" % treasure + "<br><br>" + \
               str(show_dict(players.find_one({"name": username})))
        '''

    # 要佩戴的宝物类型
    t_class = treasures.find_one({"name": treasure})['property']
    # 要替换的当前佩戴在身上的该类型宝物
    original = players.find_one({"name": username})["treasure"][t_class]

    # 用flag判断宝箱中有没有该宝物
    flag = 0
    box = players.find_one({'name': username})['box']
    player_treasure = players.find_one({"name": username})["treasure"]
    for t in box:
        if t == treasure:
            box.remove(t)
            box.append(original)
            player_treasure[t_class] = treasure
            # 更新宝箱和佩戴的宝物
            players.update_one({"name": username}, {"$set": {"box": box}})
            players.update_one({"name": username}, {"$set": {"treasure": player_treasure}})
            flag = 1
            answer = show_dict(players.find_one({"name": username}))
            answer["answer"] = "玩家%s穿戴成功" % username
            return jsonify(answer)
    if flag == 0:
        return jsonify({"error": "存储箱没有该宝物"})


'''      
            return "<h1>佩戴 %s 宝物成功</h1>" % treasure + "<br><br>" \
                   + str(show_dict(players.find_one({"name": username})))
    # 存储箱没有对应的宝物
    if flag == 0:
        return "<h1>存储箱没有 %s 宝物</h1>" % treasure + "<br><br>" \
               + str(show_dict(players.find_one({"name": username})))
'''


# 购买宝物
def buy(username, treasure):
    # 市场没有该宝物
    if markets.find_one({"name": treasure}) is None:
        return jsonify({"error": "市场无此宝物"})
        '''
        return "<h1>市场暂无 %s 宝物</h1>" % treasure + "<br><br>" \
               + str(show_dict(players.find_one({"name": username})))
        '''
    player = players.find_one({"name": username})
    box1 = player['box']
    if len(box1) >= 10:
        recovery_treasure(username)
    box = player['box']
    box.append(treasure)
    players.update_one({"name": username}, {"$set": {"box": box}})
    treasure_money = sys.maxsize
    id_ = markets.find_one({"name": treasure})['_id']  # 用id进行记录，因为市场重复
    for thing in markets.find({"name": treasure}):
        if int(thing['price']) < treasure_money:
            treasure_money = int(thing['price'])
            id_ = thing['_id']
    money1 = player['money'] - treasure_money
    # 买不起
    if money1 < 0:
        return jsonify({"error": "余额不足"})
    players.update_one({"name": username}, {"$set": {"money": money1}})
    owner = markets.find_one({"_id": id_})['owner']
    money2 = players.find_one({"name": owner})['money'] + treasure_money
    players.update_one({"name": owner}, {"$set": {"money": money2}})
    # 市场删除该宝物
    markets.delete_one({"name": treasure})
    return jsonify({"answer": "购买完成，请查看背包"})

    '''
    return "<h1>玩家 %-6s 收钱到账 %d</h1>" % (owner, treasure_money) + "<br><br>" \
           + "买家" + str(show_dict(players.find_one({"name": username}))) + "<br><br>" \
           + "卖家" + str(show_dict(players.find_one({"name": owner})))
    '''


# 收回挂牌宝物
def withdraw(username, treasure):
    # 市场没有该宝物
    if markets.find_one({"name": treasure, "owner": username}) is None:
        return jsonify({"error": "市场无此宝物"})
        '''
        return "<h1>市场没有 %s 宝物</h1>" % treasure + "<br><br>" \
               + str(show_dict(players.find_one({"name": username})))
        '''
    # 市场删除宝物
    markets.delete_one({"name": treasure, "owner": username})
    # 玩家收回宝物，同理充满则进行系统回收
    box = players.find_one({"name": username})['box']
    if len(box) >= 10:
        recovery_treasure(username)
    box = players.find_one({"name": username})['box']
    box.append(treasure)
    players.update_one({"name": username}, {"$set": {"box": box}})
    return jsonify({"answer": "收回成功，请查看背包"})
    '''
    return "<h1>收回宝物 %s 成功</h1>" % treasure + "<br><br>" + \
           str(show_dict(players.find_one({"name": username})))
    '''


# 出卖宝物
def sell(username, treasure, price):
    box = players.find_one({'name': username})['box']
    if treasure not in box:
        return jsonify({"error": "存储箱没有该宝物"})
    price = int(price)
    player = players.find_one({"name": username})
    # 卖家宝物到位
    box = player['box']
    for t in box:
        if t == treasure:
            box.remove(t)
            break
    players.update_one({"name": username}, {"$set": {"box": box}})
    # 市场宝物到位
    markets.insert_one({"name": treasure, "price": price, "owner": username})
    return jsonify({"answer": "挂牌成功，请查看市场"})
    '''
    return "<h1>挂牌成功</h1>" + "<br><br>" + \
           str(show_dict(players.find_one({"name": username})))
    '''


# 融合宝物
def merge(username, treasure, treasure2):
    player = players.find_one({"name": username})
    box = player['box']
    if player['money'] < 1000:
        return "<h1>操作失败，当前金币小于1000无法寻宝</h1>" + "<br><br>" \
               + str(show_dict(players.find_one({"name": username})))

    if treasure not in box:
        return "<h1>操作失败，存储箱没有 %s 宝物</h1>" % treasure + "<br><br>" \
               + str(show_dict(players.find_one({"name": username})))
    if treasure2 not in box:
        return "<h1>操作失败，存储箱没有 %s 宝物</h1>" % treasure2 + "<br><br>" \
               + str(show_dict(players.find_one({"name": username})))
    if treasure == treasure2:
        num = 0
        for t in box:
            if t == treasure:
                num += 1
        if num < 2:
            return "<h1>操作失败，存储箱没有两件 %s 宝物</h1>" % treasure2 + "<br><br>" \
                   + str(show_dict(players.find_one({"name": username})))
    for t in box:
        if t == treasure:
            box.remove(t)
            break
    for t in box:
        if t == treasure2:
            box.remove(t)
            break
    ls = []
    for col in treasures.find():
        ls.append(col)
        # 随机寻宝
    x = random.randint(0, len(ls) - 1)
    new_treasure_name = ls[x]['name']
    box.append(ls[x]['name'])
    players.update_one({"name": username}, {"$set": {"box": box}})
    money1 = player['money'] - 100
    players.update_one({"name": username}, {"$set": {"money": money1}})
    return "<h1>融合成功，得到 %s ，请查看背包，100元已经扣除</h1>" % new_treasure_name + "<br><br>" + \
           str(show_dict(players.find_one({"name": username})))


def finish(username):
    player = players.find_one({"name": username})
    box = player['box']
    player_treasure = player["treasure"]
    flag_t = 0
    flag_a = 0
    for t in box:
        if t == "10级工具":
            flag_t = 1
            break
    for t in box:
        if t == "10级饰品":
            flag_a = 1
            break
    if player_treasure["T"] == "10级工具":
        flag_t = 1
    if player_treasure["A"] == "10级饰品":
        flag_a = 1
    if flag_a == 1 and flag_t == 1:
        return "<h1>通关成功，谢谢游玩</h1>" + "<br><br>" \
               + str(show_dict(players.find_one({"name": username})))
    else:
        return "<h1>不好意思，您还未集齐10级工具和10级饰品，请继续游玩</h1>" + "<br><br>" \
               + str(show_dict(players.find_one({"name": username})))


# 配置自动任务的类
class Config(object):
    JOBS = [
        {
            'id': 'job1',
            'func': '__main__:find_treasure',
            'trigger': 'interval',
            'seconds': 20,

        },
        {
            'id': 'job2',
            'func': '__main__:find_money',
            'trigger': 'interval',
            'seconds': 20,

        }
    ]


# 自动寻宝
def find_treasure():
    # 遍历每个玩家
    for player in players.find():
        name = player["name"]
        # 宝箱已满
        if len(player['box']) >= 10:
            print("存储箱已满将回收一件低端宝物")
            recovery_treasure(name)
        # 得到的宝物和饰品的级别有关
        box = players.find_one({"name": name})['box']
        wear_treasure_name = player['treasure']['A']
        wear_treasure_level = treasures.find_one({"name": wear_treasure_name})['level']
        ls = []
        for col in treasures.find({"level": {"$lte": wear_treasure_level + 2, "$gte": wear_treasure_level - 2}}):
            ls.append(col)
        # 随机寻宝
        x = random.randint(0, len(ls) - 1)
        box.append(ls[x]['name'])
        # 更新宝物
        players.update_one({"name": name}, {"$set": {"box": box}})
        print("玩家 %-6s 获得宝物 %s" % (name, ls[x]['name']))


# 自动赚钱
def find_money():
    # 遍历每个玩家
    for player in players.find():
        wear_treasure_name = player['treasure']['T']
        wear_treasure_level = treasures.find_one({"name": wear_treasure_name})['level']
        # 得到的金钱和工具的级别有关
        money_get = random.randint((wear_treasure_level - 1) * 100, (wear_treasure_level + 1) * 100)
        # 打入账户
        money = player['money'] + money_get
        name = player["name"]
        # 更新账户
        players.update_one({"name": name}, {"$set": {"money": money}})
        print("玩家 %-6s 金币到账 %d" % (name, money_get))


if __name__ == "__main__":
    app.config.from_object(Config())  # 配置自动执行任务，后台寻宝赚钱
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()
    app.run()  # app开始运行
