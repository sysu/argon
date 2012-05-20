-- Identity
--    1 : guest(anonymous)
--    2 : normal(unauthenticated)
--    4 : authenticated
--    8 : root

DROP TABLE IF EXISTS `argo_boardhead`;
CREATE TABLE IF NOT EXISTS `argo_boardhead` (
    `id` int(11) unsigned NOT NULL auto_increment,
    `sid` int(11) unsigned NOT NULL,
    `boardname` varchar(20) NOT NULL,
    `description` varchar(50) NOT NULL,
    `bm` varchar(80),
    `flag` int(11) unsigned default 0,
/*    `level` int(11) unsigned default 0, */
    `r_prem` int(11) unsigned default 1, /* read permissions */
    `p_prem` int(11) unsigned default 2, /* post permissions */
    PRIMARY KEY (`id`),
    KEY `boardname` (`boardname`)
) ENGINE=MyISAM  DEFAULT CHARSET=UTF8;
