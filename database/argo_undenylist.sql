/*
    using crond to check this table,
    and free some guys 

*/
DROP TABLE IF EXISTS `argo_undenylist`;
CREATE TABLE IF NOT EXISTS `argo_undenylist`(
    `id` int(11) unsigned NOT NULL auto_increment,
    `userid` varchar(16) NOT NULL,
    `executor` varchar(16),
    `boardname` varchar(20), 
    `why` varchar(128) NOT NULL, /* why deny */
    `denytime` int(11) unsigned NOT NULL, /* the timestamp when deny */
    `freetime` int(11) unsigned NOT NULL, /* when will be free */
    PRIMARY KEY (`id`),
    UNIQUE KEY (`userid`, `boardname`)
) ENGINE=MyISAM  DEFAULT CHARSET=UTF8;
