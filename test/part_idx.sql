DROP TABLE IF EXISTS `argo_pindex`;
CREATE TABLE IF NOT EXISTS `argo_pindex` (
       `pid` int(11) unsigned NOT NULL auto_increment,
       `bid` int(11) unsigned NOT NULL default 0,
       `owner` varchar(20) NOT NULL default '',
       `title` varchar(60) NOT NULL default 'null',
    
       `content` text,

       KEY (pid),
       PRIMARY KEY bid_pid (bid, pid),
       KEY owner (owner)
)ENGINE=InnoDB DEFAULT CHARSET=UTF8 PARTITION BY KEY (bid) PARTITIONS 256;

