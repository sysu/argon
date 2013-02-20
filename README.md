argon
=====

**由于缺少人手，本项目已基本停滞。本项目已基本完成了database,model,telnet部分，telnet部分已经基本可以使用。有兴趣接手者请联系我们。**

argon是全新的[argo](http://bbs.sysu.edu.cn)实现。使用python实现。

  * database: sql表，数据库层
  * model: 数据表达层,提供Board, User等模型及其相关操作，封装底层数据库操作
  * web: argo 的web端逻辑, 使用tornado
  * test: 各类测试工具
  * telnet: argo 的telnet端逻辑. base on [chaofeng](https://github.com/LTaoist/chaofeng)
  * tools: 配套工具

我们不喜欢重造轮子，如果你有好的建议，务必告诉我们！

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
  * chaofeng
  * tornado
  * yaml(python)
  * bootstrap

其中jinja2目前被telnet端使用，可能会被web端使用。

!!! redis版本应该在2.4以上！

```bash
redis -v
```

Install
-------

目前telnet可用，但功能还在进一步开发。

### 获取本项目

```bash
git clone https://github.com/argolab/argon.git
```

测试一下需要的依赖是否被满足:

```bash
python -c 'import jinja2,MySQLdb,redis,eventlet,bcrypt,chaofeng,tornado,yaml'
```

如果不使用telnet，chaofeng,eventlet和jinja2可以省去。

应该没有任何异常输出，继续下一步。

### 安装数据库Mysql和Redis

目前很多一部分代码都在硬编码。配置还没有整合到一起。而数据库的
封装层在model文件夹，他的配置文件在 argon/argo_config.py。

新建一个用户名为`bbs`，密码为`forargo`，并授权给`argo`数据库。

redis使用默认的6379端口。

初始化mysql和redis ：

```bash
./tools/init_database.sh
```

另外，需要初始化权限设置

```bash
./tools/init_redis.sh
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

```bash
cd ../ ## 回到 argon/
./admin.sh
>>> mrg.team.joint_team('你注册的帐号', 'SYS_SUPER')
```

这将会将你注册的帐号设置为超级帐号，然后登录（可能需要登出再登入）。
即可简单管理入口。

### 测试web

```bash
cd web
python server.py
```

使用8080端口。

### 补充

如果存在一些旧的数据和旧的设置，可能会导致出现问题（SQL和redis设置
发生变化，可能会出现bug）。这时候可以尝试 `mrg.favourite.init_user_favourite`
`mrg.userperm.init_user_team`, `init_boardteam` 。`model.Model.foreach`可以
对SQL进行一些简单的迭代，不过仅是测试或许直接重新建造更方便。

!!! redis
ubuntu 2.4的ppa
https://launchpad.net/~chris-lea/+archive/redis-server/+index#
