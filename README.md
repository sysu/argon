argon
=====

argon是全新的[argo](http://bbs.sysu.edu.cn)实现。使用python实现。

  * database: sql表，数据库层
  * model: 数据表达层,提供Board, User等模型及其相关操作，封装底层数据库操作
  * web: argo 的web端逻辑, 使用tornado
  * lib: 公用函数库
  * test: 各类测试工具
  * telnet: argo 的telnet端逻辑. base on [chaofeng](https://github.com/LTaoist/chaofeng)

我们不喜欢重造轮子，如果你有好的建议，务必告诉我们！

一些我们的讨论可以在[这里](http://bbs.sysu.edu.cn/bbstcon?board=Programming&file=M.1338262485.A)找到。

Todo
----

  * 完善数据库及model建设
  * telnet建设
  * 更多人的参与
  * ...

About Argo
----------

> 1996年3月，中山大学校园BBS设立，定名为“逸仙时空”（Yat-sen Channel）。
与其他高校所不同的是，逸仙时空还有一个别称argo，也可以用argo.sysu.edu.cn访
问。说起argo这个别称的起源，众说纷纭。有说中大早期网络中心电脑为星座编号，
argo代表南船座，排名最前故名之。 -- [《argo十年，BBS是大学的盐》](http://bbs.sysu.edu.cn:874/#!/anc/D.1044599037.A/D.1152876984.A/D.1152862690.A/M.1152862408.A)

Welcome to join us.

Overview
--------

>  -------- ----------------
>  | Web | telnet | 开放API |
>  --------- ----------------
>  |     Model封装          |
>  ---------- ---------------
>  |    Mysql | redis      |
>  ------------------------
 
采用python实现。

Dependencies
------------

  * python2
  * jinja2
  * python-mysql
  * python-redis
  * eventlet
  * bcrypt

其中jinja2目前被telnet端使用，可能会被web端使用。

web端准备使用tornado 。

Install
-------

目前telnet可用，但功能还在进一步开发。

### 获取本项目

```bash
git clone https://github.com/argo-admin/argon.git
```

测试一下需要的依赖是否被满足:

```bash
python -c 'import MySQLdb,eventlet,jinjia2,redis'
```

应该没有任何异常输出。

### 安装数据库Mysql和Redis

```bash
sudo pacman -S mysql redis
```

目前很多一部分代码都在硬编码。配置还没有整合到一起。而数据库的
封装层在model文件夹，他的配置文件在 argon/argo_config.py

```python

class ConfigDB:
    '''
        Database config
    '''
    host = "localhost"
    port= 3306
    user= "bbs"
    passwd= "forargo"
    dbname = "argo"

class ConfigCache:
    '''
        Cache config
    '''
    host = "localhost"
    port = 6379

```

### 初始化数据库

我们目前提供一个简单的python脚本:

```bash
./admin.sh
>>> init_database()
```

如果数据库正常启动，配置无错误，telnet即可启动了：

```bash
$ cd telnet/
$ python server.py
```

然后客户端登陆进来：

```bash
$ telnet localhost 5000
```

注册一个帐号。然后就可以登陆了。但注意到现在还没有设置
版块等等，也没有讨论区分区。

目前没有写好管理的接口，但我们还是可以手动来：

```bash
./admin.sh # 继续admin.sh
>>> manager.section.add_section(sectionname="BBS 系统",description="[站务] [意见]")
>>> manager.section.get_all_section() # 记住sid，一般是1
>>> manager.board.add_board(boardname="Test",description="系统测试",sid=1)
>>> manager.post._create_table(boardname="Test")
>>> manager.board.get_all_boards()
>>> manager.board.get_by_sid(1)
>>> manager.board.get_board("Test")
```

如果没有问题，那么我们已经成功添加了一个`BBS 系统`讨论区分类，和一个`Test`版块。

`admin.sh`实际上在调用`admin.py`,而后者则直接加载`model/manager.py` 。更多的
接口参加源代码。

telnet端的更多说明见`telnet/README.md`。

