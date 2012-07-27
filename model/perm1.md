组：

属于一个组表示你具有这个身份。一个人可以有多个身份。

guest：web未登录、telnet用guest登录
Welcome：注册但未验证通过id
USER：已经验证过的ID

比如，你属于USER组，表示你已经是经过验证id的了。

mas：在职站务组
masNewcomers：在职实习站务组
oldmas：退休站务组
maintainer：系统维护员
artist：系统美工
SYSOPs：超级管理员组
denyGlobal：全站封禁

你是mas组，表示你是站务。

_ZoneAdmin：(_代表下划线)_区主管，比如1ZoneAdmin
__BM：{__代表版块名称}__的版主，比如TestBM

版块
-----

一个版块有R/W/D/X是个属性，R表示read，W表示write、D表示deny、X表示admin。
分别表示那些人可以看到，那些人可以发帖，哪些人不能发帖，哪些人可以管理。

普通的版块允许任何人进入，但是没有验证过的id是不难发帖的。只有版主和
相关站务可以管理。所以一般可以设置如下：

R：Guest,Welcome,USER
W：USER
D：__Deny（本版封禁），denyGlobal
X：__BM

考虑到有区主管，所以可以把相关的区主管加入X里面。比如Test属于一区，
那么Test版可以这样设置：

X: TestBM, 1ZeonAdmin

名单版，目前这样就可以了：

R： TestAccept（可以进入该版的人加进来）
W： TestAccept
D： 可以讨论denyGlobal是否可以在名单版发
X： TestBM, SYSOPs

不过这样还是不够爽。比如我们站组实习版，允许全部的在职站务、实习站务、
退休站务，所以可以这样设置：

R： mas,masNewcomers,oldmas

而如果我们有个版（暂时叫做mas）是只允许在职站务的，可以这样设置：

R： mas

这样，实习站务就不可以进入mas版但是可以进入masNewcomers了。

然后某人转正，就将他从masNewcomers组转到mas组。然后他就可以两个
版都看见了。

或者来了个什么特殊时期，比如瘟疫爆发。需要开一个版，只允许相关的
负责人员和现在的站务进来。那你就开个版：

R: mas, WenYI2012

然后把那堆人全部加到WenYI2012里面。

然后，人手不够，研究决定，退休的站务也可以进来。然后你就把oldmas
加进来。

R: oldmas,mas,WenYI2012

加进来几天后，上面来文件，不允许站务组的人在里面喔。然后我们就把
mas和oldmas移除即可。如果有人又是站务组，又是WenYI2012,也不会有
影响（因为WenYI2012还是会让他通过的）。

组可能会催生很多内部版 = = 

讨论
-----

1 有哪些版面？比如上面的名单版和普通版。然后貌似freshmen是可以
让没有验证的id发帖的，那么就把welcome加进freshmen的W里面就可以了。

好像有些版还分校内校外ip？更复杂的情况？

2 管理具体包括哪些？

a) 删除帖子
b）封禁（将该人加入 __Deny组）
c）管理精华区

管理精华包括增加删除修改，需不需要细分？我建议不需要细分。

然后这几天好像看到还有y，是可以从所谓的废纸篓里面恢复吗？
这个需不需要细分（变成Y属性）？

