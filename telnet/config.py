# -*- coding: utf-8 -*-
from chaofeng import ascii

root = 'welcome'

menu = {
    "main":(
        ( ("menu",{"name":"section"}),'e',(12,5)),
        ( ("unf",{}),'d' ),
        ( ("unf",{}),'f' ),
        ( ("unf",{}),'r' ),
        ( ("unf",{}),'m' ),
        ( ("unf",{}),'t' ),
        ( ("unf",{}),'i' ),
        ( ("unf",{}),'s' ),
        ( ("unf",{}),'c' ),
        ( ("unf",{}),'p' ),
        ( ("bye",{}),'g' )),
    "section":(
        ( ( ("boardlist",{"sid":0}),'0',(11,6)),
          ( ("boardlist",{"sid":1}),'1'),
          ( ("boardlist",{"sid":2}),'2'),
          ( ("boardlist",{"sid":3}),'3'),
          ( ("boardlist",{"sid":4}),'4'),
          ( ("boardlist",{"sid":5}),'5'),
          ( ("boardlist",{"sid":6}),'6'),
          ( ("boardlist",{"sid":7}),'7'),
          ( ("boardlist",{"sid":8}),'8'),
          ( ("boardlist",{"sid":9}),'9'),
          ( ("boardlist",{}),            'a',(11,41)),
          ( ("boardlist",{"new":True}),  'n'),
          ( ("menu",     {"name":"main"}),'e'),
          )
    )
}
