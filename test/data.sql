DROP TABLE IF EXISTS `argo_content`;
CREATE TABLE IF NOT EXISTS `argo_content` (
    `pid` int(11) unsigned NOT NULL,
    `content` text,
    `signature` text,
    PRIMARY KEY (`pid`)
) ENGINE=InnoDB DEFAULT CHARSET=UTF8;
 
