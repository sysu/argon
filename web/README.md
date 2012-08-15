
目录：
------
* comm:     公共目录，负责mobile和pybbs的公共handler，包括ajax和api的handler在此。其中comm/urls.py下有所有handler的总路由表
* mobile：  移动版（简化版）的主handler目录
* pybbs：   网页版的主handler目录
* static：  js/css/img 
* template：模版
* server.py 服务器程序, python server.py即可，默认端口8080

安装：
------
* 需事先安装tornado： ```easy_install tornado```
* 运行 pyhon server.py  然后在浏览器打开127.0.0.1:8080/m/即为移动版
* 移动版已经完成，web版目前正在开发前端原型。



