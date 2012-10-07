
目录：
------
* server.py 服务器程序,默认端口8080。包括了总路由表
* mobile：  移动版（简化版）的主handler目录
* static：  js/css/img 
* template：模版
* index.py : 首页，登入登出
* lib.py : 公共函数和类
* comm_ajax.py : 公用的ajax接口
* board.py : 版块
* uimodules.py : 封装的tornado的ui组件，userbox（左侧栏）在此

安装：
------
* 需事先安装tornado： ```easy_install tornado```
* 运行 pyhon server.py  然后在浏览器打开127.0.0.1:8080/m/即为移动版
* 移动版已经完成，web版目前正在开发前端原型。



