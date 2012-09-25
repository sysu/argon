#!/usr/bin/python2
# -*- coding: utf-8 -*-

from Model import Model

PERM_BASE_ADMIN = '$BASE_ADMIN'
PERM_BASE_USER = '$USER'
PERM_AUTHED_USER = '$AUTHED_USER'
PERM_ACCOUNT = "$ADMIN_ACCOUNT"
PERM_BM = "$ADMIN_BM"
PERM_TELNET_ART = "$TELNET_ART"
PERM_MASTER = '$MASTER'
PERM_SYS_CONFIG = "$SYS_CONFIG"
PERM_DENY_GLOBAL = "$DENY_GLOBAL"
PERM_SUPER = '$SYS_SUPER'

BOARDPERM_ALLOW = "$BOARD_ALLOW"
BOARDPERM_POST = "$BOARD_POST"
BOARDPERM_DENY = "$BOARD_DENEY"
BOARDPERM_ADMIN = "$BOARD_ADMIN"
BOARDPERM_ADMIN_ACCEPTED = "$BOARD_ACCEPTED"

TEAM_GUEST = 'SYS_GUEST'
TEAM_WELCOME = 'SYS_WELCOME'
TEAM_USER = 'SYS_USER'
TEAM_DENY_GLOBAL = 'SYS_DENY_GLOBAL'
TEAM_SYSOPS = 'SYS_SYSOPS'
TEAM_SUPER = 'SYS_SUPER'

BOARDTEAM_ACCEPTED = "SYS_{}_ACCEPTED"

BOARDTEAM_BM = "SYS_{}_BM"
BOARDTEAM_DENY = "SYS_{}_DENY"

ALL_TEAM = dict(
    TEAM_GUEST=TEAM_GUEST,
    TEAM_WELCOME=TEAM_WELCOME,
    TEAM_USER=TEAM_USER,
    TEAM_DENY_GLOBAL=TEAM_DENY_GLOBAL,
    TEAM_SYSOPS=TEAM_SYSOPS,
    TEAM_SUPER=TEAM_SUPER
    )

INIT_TEAM = [
    (TEAM_GUEST, u'游客', False),
    (TEAM_WELCOME, u'未验证用户', False),
    (TEAM_USER, u'验证用户', False),
    (TEAM_DENY_GLOBAL, u'全站封禁', False),
    (TEAM_SYSOPS, u'站务组', True),
    (TEAM_SUPER, u'超级帐号', False),
    ]

INIT_PERM_TEAM = {
    PERM_BASE_ADMIN : (TEAM_SYSOPS, TEAM_SUPER),
    PERM_BASE_USER : (TEAM_WELCOME, TEAM_USER),
    PERM_AUTHED_USER : (TEAM_USER,),
    PERM_ACCOUNT : (TEAM_SYSOPS, TEAM_SUPER),
    PERM_BM : (TEAM_SYSOPS, TEAM_SUPER),
    PERM_TELNET_ART : (TEAM_SYSOPS, TEAM_SUPER),
    PERM_SYS_CONFIG : (TEAM_SYSOPS, TEAM_SUPER),
    PERM_MASTER : (TEAM_SYSOPS, TEAM_SUPER),
    PERM_SUPER : (TEAM_SUPER,)
    }

DEFAULT_USER_TEAM = (
    TEAM_WELCOME,
    )

class ArgoTeam(Model):

    def __init__(self, manager):
        super(ArgoTeam, self).__init__(manager)
        self.team = manager.get_module('team')
        self.perm = manager.get_module('perm')

    def init_system(self):
        for teamid, teamname, publish in INIT_TEAM:
            self.team.register_team(teamid, teamname, publish)
        for perm in INIT_PERM_TEAM :
            self.perm.clear_perm(perm)
            self.perm.give_perm(perm, *INIT_PERM_TEAM[perm])

    def init_user_team(self, userid):
        for team in DEFAULT_USER_TEAM :
            self.team.join_team(userid, team)

    def _to_boardteams(self, string, boardname):
        return string.replace('{}', boardname).split(',')

    def _to_boardteam(self, string, boardname):
        return string.replace('{}', boardname)

    def init_boardteam(self, boardname):
        self.team.register_team(self._to_boardteam(BOARDTEAM_DENY, boardname),
                                u'%s版封禁' % boardname, False)
        self.team.register_team(self._to_boardteam(BOARDTEAM_BM, boardname),
                                u'%s版版主' % boardname, False)

    def get_board_ability(self, userid, boardname):
        r,w,d,s = self.perm.checkmany_boardperm(userid, boardname,
                                                BOARDPERM_ALLOW, BOARDPERM_POST,
                                                BOARDPERM_DENY, BOARDPERM_ADMIN)
        return ( r , r and not d and w, d, s)

    def join_board_bm(self, boardname, bm):
        self.team.join_team(bm, self._to_boardteam(BOARDTEAM_BM, boardname))

    def remove_board_bm(self, boardname, bm):
        self.team.remove_team(bm, self._to_boardteam(BOARDTEAM_BM, boardname))

    def get_bm(self, boardname):
        self.team.all_members(self._to_boardteam(BOARDTEAM_BM, boardname))

    def set_deny(self, boardname, userid):
        self.team.join_team(userid, self._to_boardteam(BOARDTEAM_DENY, boardname))

    def remove_deny(self, boardname, userid):
        self.team.remove_team(userid, self._to_boardteam(BOARDTEAM_DENY, boardname))

    def all_deny(self, boardname):
        return self.team.all_members(self._to_boardteam(BOARDTEAM_DENY, boardname))

    def set_deny_global(self, userid):
        self.team.join_team(userid, TEAM_DENY_GLOBAL)

    def remove_deny_global(self, userid):
        self.team.remove_team(userid, TEAM_DENY_GLOBAL)

    def all_global_deny(self, userid):
        return self.team.all_members(TEAM_DENY_GLOBAL)

    def _set_board_perm(self, boardname, perm, team_str):
        self.perm.clear_boardperm(boardname, perm)
        self.perm.give_boardperm(boardname, perm, *self._to_boardteams(team_str, boardname))

    def set_board_allow(self, boardname, team_str):
        self._set_board_perm(boardname, BOARDPERM_ALLOW, team_str)

    def set_board_post(self, boardname, team_str):
        self._set_board_perm(boardname, BOARDPERM_POST, team_str)

    def set_board_deny(self, boardname, team_str):
        self._set_board_perm(boardname, BOARDPERM_DENY, team_str)

    def set_board_admin(self, boardname, team_str):
        self._set_board_perm(boardname, BOARDPERM_ADMIN, team_str)

    def get_board_allow(self, boardname):
        return self.perm.get_teams_with_boardperm(boardname, BOARDPERM_ALLOW)

    def get_board_deny(self, boardname):
        return self.perm.get_teams_with_boardperm(boardname, BOARDPERM_DENY)

    def get_board_post(self, boardname):
        return self.perm.get_teams_with_boardperm(boardname, BOARDPERM_POST)

    def get_board_admin(self, boardname):
        return self.perm.get_teams_with_boardperm(boardname, BOARDPERM_ADMIN)
