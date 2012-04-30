
DROP TABLE IF EXISTS `argo_boardhead`;
CREATE TABLE IF NOT EXISTS `argo_boardhead` (
    `bid` int(11) unsigned NOT NULL auto_increment,
    `sid` int(11) unsigned NOT NULL,
    `boardname` varchar(20) NOT NULL,
    `description` varchar(50) NOT NULL,
    `bm` varchar(80),
    `flag` int(11) unsigned default 0,
    `level` int(11) unsigned default 0,

    PRIMARY KEY (`bid`),
    KEY `boardname` (`boardname`)
) ENGINE=MyISAM  DEFAULT CHARSET=UTF8;

