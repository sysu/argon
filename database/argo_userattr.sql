DROP TABLE IF EXISTS `argo_userattr`;
CREATE TABLE IF NOT EXISTS `argo_userattr` (
    `id` varchar(20) NOT NULL,
    `userid` varchar(20) NOT NULL,
    `attr` blob,

     PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=UTF8;

