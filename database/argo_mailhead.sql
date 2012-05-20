
DROP TABLE IF EXISTS `argo_mailhead`;
CREATE TABLE IF NOT EXISTS `argo_mailhead` (
    `id` int(11) unsigned NOT NULL auto_increment,
    `fromuserid` varchar(14) NOT NULL,
    `touserid` varchar(14) NOT NULL,
    `attachidx` varchar(20),
    
    `sendtime` int(11) unsigned NOT NULL default 0,
    `fromaddr` varchar(64),
    
    `readmark` int(11) unsigned NOT NULL default 0,
    `content` text,
    `quote` text,
    `signature` text,

    PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=UTF8;

