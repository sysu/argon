DROP TABLE IF EXISTS `argo_filehead`;
CREATE TABLE IF NOT EXISTS `argo_filehead` (
       `pid` int(11) unsigned NOT NULL auto_increment,
       `bid` int(11) unsigned NOT NULL,
       `owner` varchar(20) NOT NULL,
       `real_owner` varchar(20) NOT NULL default '',
       `title` varchar(60) NOT NULL,
       `tid` int(11) unsigned NOT NULL default 0,
       `replyid` int(11) unsigned NOT NULL default 0,
       `posttime` timestamp NOT NULL default CURRENT_TIMESTAMP
                  on update CURRENT_TIMESTAMP,
       `fromaddr` varchar(20) NOT NULL,
       `fromhost` varchar(64) NOT NULL default "Yat-sen Channel",

       `originalfilename` varchar(32) ,

       `mark_g` boolean NOT NULL default false,
       `mark_m` boolean NOT NULL default false,
       `replyable` boolean NOT NULL default true,
       `flag` int(11) unsigned default 0,

       PRIMARY KEY (`pid`),
       KEY bid (bid),
       KEY owner (owner)
       KEY tid (tid)
       KEY mark_g (mark_g)
       KEY mark_m (mark_m)
       KEY replyable (replyable)
) DEFAULT CHARSET=UTF8;
