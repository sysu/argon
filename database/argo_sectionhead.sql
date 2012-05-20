
DROP TABLE IF EXISTS `argo_sectionhead`;
CREATE TABLE IF NOT EXISTS `argo_sectionhead` (
    `id` int(11) unsigned NOT NULL auto_increment,
    `sectionname` varchar(20) NOT NULL,
    `description` varchar(50) NOT NULL,

    PRIMARY KEY (`id`),
    KEY `sectionname` (`sectionname`)
) ENGINE=MyISAM  DEFAULT CHARSET=UTF8;

