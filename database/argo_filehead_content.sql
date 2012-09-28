DROP TABLE IF EXISTS `argo_filehead_content`;
CREATE TABLE IF NOT EXISTS `argo_filehead_content` (
       `pid` int(11) unsigned NOT NULL,
       `content` text,
       `signature` text,
       PRIMARY KEY (`pid`)
) ENGINE=InnoDB DEFAULT CHARSET=UTF8;
