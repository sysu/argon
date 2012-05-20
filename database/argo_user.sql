DROP TABLE IF EXISTS `argo_user`;
CREATE TABLE IF NOT EXISTS `argo_user` (
    `id` int(11) unsigned NOT NULL auto_increment,
    `userid` varchar(20) NOT NULL,
    `passwd` varchar(60),
    `nickname` varchar(20),
    `email` varchar(80),
/*    `userlevel` int(11) unsigned NOT NULL default 0, */
    `identity` int(11) unsigned NOT NULL default 2,
    `netid`  varchar(20),
    `iconidx` varchar(20),

    `firstlogin` datetime NOT NULL default '1970-01-01 00:00:00',
    `firsthost` varchar(20),
    `lastlogin` datetime NOT NULL default '1970-01-01 00:00:00',
    `lasthost` varchar(20),
    `lastlogout` datetime NOT NULL default '1970-01-01 00:00:00',
    `numlogins` int(11) unsigned default 0,
    `numposts` int(11) unsigned default 0,
    `credit` int(11) unsigned default 0,
    `lastpost` datetime NOT NULL default '1970-01-01 00:00:00',
    `stay` int(11) unsigned default 0,
    `life`  int(11) default 365,
    `lastupdate` timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,

    `birthday` date NOT NULL default '1990-01-01',
    `address` varchar(50), 
    `usertitle` varchar(20) NOT NULL default 'user',
    `gender`  int(11) unsigned default 1,
    `realname` varchar(20),
    
    `dattr` blob,

    PRIMARY KEY (`id`),
    KEY `userid` (`userid`)

) ENGINE=InnoDB  DEFAULT CHARSET=UTF8;

