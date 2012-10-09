DROP TABLE IF EXISTS `argo_filehead_junk`;
CREATE TABLE IF NOT EXISTS `argo_filehead_junk` (
       `pid` int(11) unsigned NOT NULL auto_increment,
       `bid` int(11) unsigned NOT NULL default 0,
       `owner` varchar(20) NOT NULL default '',
       `real_owner` varchar(20) NOT NULL default '',
       `title` varchar(63) NOT NULL default 'null',
       `tid` int(11) unsigned NOT NULL default 0,
       `replyid` int(11) unsigned NOT NULL default 0,
       `posttime` timestamp NOT NULL default CURRENT_TIMESTAMP
                  on update CURRENT_TIMESTAMP,
       `oldfilename` varchar(32) NOT NULL default '',
   
       `agree` int(11) unsigned NOT NULL default 0,
       `disagree` int(11) unsigned NOT NULL default 0,
        
       `attachidx` varchar(32) NOT NULL default '',
       `fromaddr` varchar(20) NOT NULL default '',
       `fromhost` varchar(32) NOT NULL default "逸仙时空",
       `content` text,
       `signature` text,

       `mark_g` boolean NOT NULL default false,
       `mark_m` boolean NOT NULL default false,
       `replyable` boolean NOT NULL default true,
       `flag` int(11) unsigned NOT NULL default 0,

       KEY (pid),
       PRIMARY KEY bid_pid (bid, pid),
       KEY bid_tid (bid, tid),
       KEY bid_mark_g (bid, mark_g),
       KEY bid_mark_m (bid, mark_m),
       KEY owner (owner)

)ENGINE=InnoDB DEFAULT CHARSET=UTF8 PARTITION BY KEY (bid) PARTITIONS 13;

