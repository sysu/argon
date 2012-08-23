/*
    using crond to check this table,
    and free some guys 

*/
DROP TABLE IF EXISTS `argo_undenylist`;
CREATE TABLE IF NOT EXISTS `argo_undenylist`(
    `uid` int(11) unsigned NOT NULL auto_increment,
    `id` int(11) unsigned ,
    `userid` varchar(16) NOT NULL,
    `executor` varchar(16),
    `boardname` varchar(20), 
    `why` varchar(128) NOT NULL, /* why deny */
    `denytime` TIMESTAMP,
    `freetime` TIMESTAMP, 
    PRIMARY KEY (`uid`)
) ENGINE=MyISAM  DEFAULT CHARSET=UTF8;
