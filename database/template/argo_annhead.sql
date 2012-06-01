/*
    pid : Parent annhead id
    editor:  The bm who edited this ann
    flag: 
        'r'->regular file(post)
        'd'->dir
        'l'->link
    Find all of the children:
        select id from argo_annhead_xxx where pid = id
*/
DROP TABLE IF EXISTS `argo_annhead_${bid}`;
CREATE TABLE IF NOT EXISTS `argo_annhead_${bid}` (
    `id` int(11) unsigned NOT NULL auto_increment,
    `pid` int(11) unsigned NOT NULL default 0,
    `title` varchar(60),
    
    `owner` varchar(14),
    `editor` varchar(14),
    
    `flag` varchar(2),
    `mtime` timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
    
    `content` text,

    PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=UTF8;

