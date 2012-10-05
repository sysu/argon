DROP TABLE IF EXISTS `argo_annhead`;
CREATE TABLE IF NOT EXISTS `argo_annhead`(
    `id` int(11) unsigned NOT NULL auto_increment ,
    `bid` int(11) unsigned NOT NULL default 0,
    `pid` int(11) unsigned NOT NULL default 0,
    `rank` int(11) unsigned NOT NULL,
    `title` varchar(60),
    
    `owner` varchar(20),
    `editor` varchar(20),
    
    `mtime` timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
    
    `tags` varchar(64),
    `content` text,

    PRIMARY KEY (id),
    KEY bid_id (bid, id)
) ENGINE=InnoDB  DEFAULT CHARSET=UTF8 PARTITION BY KEY (id) PARTITIONS 13;

