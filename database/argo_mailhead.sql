DROP TABLE IF EXISTS `argo_mailhead`;
CREATE TABLE IF NOT EXISTS `argo_mailhead` (
    `mid` int(11) unsigned NOT NULL auto_increment,
    `fromuserid` varchar(16) NOT NULL,
    `touserid` varchar(16) NOT NULL,
    `attachidx` varchar(128),

    `tid` int(11) unsigned ,
    `replyid` int(11) unsigned NOT NULL default 0,
    `title` varchar(60),

    `sendtime` timestamp NOT NULL default CURRENT_TIMESTAMP ,
    `fromaddr` varchar(64),
    `content` text,
    `signature` text,
   
    `readmark` boolean NOT NULL default 0, 
    `flag` int(11) unsigned NOT NULL default 0,
    
    KEY (mid),
    PRIMARY KEY userid_mid (touserid, mid)

)ENGINE=InnoDB DEFAULT CHARSET=UTF8 PARTITION BY KEY (touserid) PARTITIONS 13;

