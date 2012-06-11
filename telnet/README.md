like-argo
=========

用python实现的argo。用[cháofēng](https://github.com/argo-admin/chaofeng)框架。

like包括love和similarity。like-argo不仅仅是对旧版本的克隆，而是继承和创新。

这是一个充满爱的活动。

!!!目前只用cterm进行过测试，其他终端机会极度不正常。

static目录
----------

一个画面一个Frame，对应一个类。

巨大的字符串常量存在static里面，然后当需要的时候
导入，内部全部用utf8编码：

  * .tpl 读入，实例化为标准python库string Template
  * .txt 导入，用`\r\n`换行，普通的字符串
  * .seq 读入，每行为list的一个对象
  * .ani 实例化为Animation类
  * .jtpl 实例化jinja2的Template render
  * .jtxt 实例化为jinja2的Template后直接render为字符串
  
目录
----

```
 \-
  |- static        # 字符串常量
    |- help        # 帮助文件
      ...
    |- template    # jinja2的模板
      help.jtpl    # 输出帮助时候的模板
      post.jtpl    # 输出文章的时候的模板
      history.jtpl # 输出历史记录的模板 
    |- bottom_bar  # 底栏控制
    ...            # 历史原因，还有很多乱七八糟待清理
  |- chaofeng      # telnet的底层框架
    ...
  |- editor.py     # 编辑相关，发帖、回帖、修改，etc
  |- login.py      # 登陆画面，用户的入口
  |- special_frame.py   # 一些特殊的情况的处理画面
  |- user.py       # 用户资料管理（待清理）
  |- argo_frame.py # 全部画面的基类，包含大多数的常用函数
  |- common.py     # 一些常用的全局变量
  |- menu.py       # 主菜单（登陆后入口），讨论区选单，etc
  |- board.py      # 版块功能
  |- config.py     # 配置文件
  |- libtelnet.py  # 底层函数，待清理
  |- view.py       # 阅读相关，看贴，帮助，etc
  |- template.py   # 模板使用，包含了jinja2的相关设置
  |- boardlist.py  # 讨论区列表
  |- server.py     # 开始运行服务
  ...
  
```

每个文件约100~200行，以后考虑合并

Feature
--------

……勉强算Feature吧

  1. 历史记录。 Ctrl+\启用
  2. 页面间跳转。 在阅读的时候按a
  3. 改善的帮助说明。每个画面通过按下h来获取当前画面的帮助。
  4. 安全中断：随时按下Ctrl+C来结束当前的画面，并回退到上个
     画面。
     
Todo
----

  1. 精华区，站内信，用户资料管理，讯息（数据库接口和底层表示都基本确定）
  2. 管理相关（权限、版主功能、站务，etc）
  3. 新的Featrue
  。。。

