like-argo
=========

用python实现的argo。用[cháofēng](https://github.com/argo-admin/chaofeng)框架。

like包括love和similarity。like-argo不仅仅是对旧版本的克隆，而是继承和创新。

Install
-------

  1. 安装mysql和redis
  2. 建立初始的sql表
  
```bash
# test_db_orm.py 在 argon/下
python test_db_orm.py init_database
```

  3. 增加讨论区分类，和相关的版块。貌似没有这部会崩溃T.T

```bash
python test_db_orm.py # 查看全部可能的命令
python test_db_orm.py help add_section # 查看增加分类命令
python test_db_orm.py help add_board   # 查看增加版块命令
python test_db_orm.py add_section 'Section 1' '分类区1'  # 增加一个分类区
python test_db_orm.py add_board 'Test' 'Section 1' '测试版块' # 增加一个版块
```

  4. 启动服务器

```bash
python server.py
```

  5. 测试
  
```bash
telnet localhost 5000
```

-----------------------------------------

继续努力中……
