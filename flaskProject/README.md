整个项目代码位于flaskProject文件夹中。

1.执行init_db.py，初始化treasures宝物库。

2.执行app.py，后台自动运行寻宝和赚钱进程，每20s结果会显示在命令行上；登录localhost:5000/ 即可进入登录界面，登录界面对应templates/index.html

3.用浏览器在localhost:5000/中执行注册/登录操作进入用户页面,用户界面对应templates/game.html

4.在用户界面网页中允许用户使用post form提交表单来执行操作，也可以直接遵循app.py中的路由规则用url的get执行相关操作

（如果用postman测试，还支持post json的输入）

5.如果要用pytest，在命令行中输入pytest即可，pytest的配置文件为\_init\_.py和conftest.py，pytest会按顺序运行test_user.py中的函数。（注意运行时要先把mongodb中markets和players两个collection更改为collection markets.json和collection players两个json文件的内容，删除当前数据然后用MongoDB compass直接导入即可，否则有些测试代码如买卖商品会无法执行。）

6.为了重现本项目测试的过程，我将用到的四个collection中的数据存了下来，分别为collection markets.json，collection players.json，collection treasures.json和picurl.json，后两个是在init_db.py时自动生成的不用手动去建立，前两个是用户使用过程中产生的，可以直接往名为webgame的数据库中的markets和players collection中导入。

