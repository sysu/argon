/*
    For example:

    LTS's friends: gcc Cypress
    a = [['gcc', 'Big cc'], ['Cypress', 'berlin']] //'Big cc' and 'berlin' is remark
    b = cPickle.dumps(a, 2)
    friends  = b
    
    Others are similar.
*/

DROP TABLE IF EXISTS `argo_userattr`;
CREATE TABLE IF NOT EXISTS `argo_userattr` (
    `userid` varchar(20) NOT NULL,
    `friends` blob,
    `rejects` blob,
    `favorite` blob,
   
    /* more */

     PRIMARY KEY (`userid`)
) ENGINE=MyISAM  DEFAULT CHARSET=UTF8;
