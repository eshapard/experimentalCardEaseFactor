# -*- mode: Python ; coding: utf-8 -*-
# Good / Again (Yes No) 2 buttons only
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# No support. Use it AS IS on your own risk.
from __future__ import division
from __future__ import unicode_literals
#import os

from aqt import mw
from aqt.reviewer import Reviewer
from aqt.utils import showInfo
from anki.hooks import wrap, addHook, runHook
from aqt.qt import *
import json

debugMsg = False
rightLabel = "Victory"
wrongLabel = "Defeat"
showAnswerText = "Attack!"

# Anki uses a single digit to track which button has been clicked.
RETEST = 5

remap = {2:  [None, 1, 2, 2, 2],    # - nil     Again   Good   Good    Good  -  default 2-buttons: 1 = Again, 2 = Good, 3=None, 4=None
         3:  [None, 1, 2, 2, 2],    # nil     Again   Good   Good    Good - def 3-buttons: 1 = Again, 2 = Good, 3 = Easy, 4=None
         4:  [None, 1, 3, 3, 3]}    # 0=nil/none   Again Good Good Good - def 4-buttons: 1 = Again, 2 = Hard, 3 = Good, 4 = Easy

# -- width in pixels
# --    Show Answer button, triple, double and single answers buttons
BEAMS4 = '99%'
BEAMS3 = '74%'
BEAMS2 = '48%'
BEAMS1 = '24%'

black = '#000'
red = '#c33'
#green = '#3c3'
green = '#080'

BUTTON_LABEL = ['<span style="color:' + black + ';">' + wrongLabel + '</span>',
                '<span style="color:' + green + ';">' + rightLabel + '</span>']

# Replace _answerButtonList method
def answerButtonList(self):
    '''
    l = ((
        1, '<style>button span{font-size:x-large;} button small ' +
        '{ color:#999; font-weight:400; padding-left:.35em; ' +
        'font-size: small; }</style><span>' + BUTTON_LABEL[0] + '</span>',
        BEAMS2),)
    '''
    l = ((
        1, '<style>button small ' +
        '{ color:#999; font-weight:400; padding-left:.35em; ' +
        'font-size: small; }</style><span>' + BUTTON_LABEL[0] + '</span>',
        BEAMS2),)
    cnt = self.mw.col.sched.answerButtons(self.card)
    if cnt == 2 or cnt == 3: #i believe i did this right: we want ease 2 = good if 2 or 3 buttons
	    return l + ((2, '<span>' + BUTTON_LABEL[1] + '</span>', BEAMS2),)
    elif cnt == 4: # b/c we want ease 3 = good in this version
        return l + ((3, '<span>' + BUTTON_LABEL[1] + '</span>', BEAMS2),)
    # the comma at the end is mandatory, a subtle bug occurs without it

def AKR_answerCard(self, ease):
    count = mw.col.sched.answerButtons(mw.reviewer.card)  # Get button count
    if count < 4: 
        if debugMsg: showInfo("Review Type: (Re)Learning")
    else:
        if debugMsg: showInfo("Review Type: Review")
    if debugMsg: showInfo("Selected: %s" % ease)
    try:
        ease = remap[count][ease]
        if debugMsg: showInfo("Remapped to: %s" % ease)
    except (KeyError, IndexError):
        pass
    __oldFunc(self, ease)

__oldFunc = Reviewer._answerCard
Reviewer._answerCard = AKR_answerCard

def myAnswerButtons(self, _old):
    times = []
    default = self._defaultEase()

    def but(i, label, beam):
        if i == default:
            extra = 'id=defease'
        else:
            extra = ''
        due = self._buttonTime(i)
        return '''
<td align=center style="width:%s;">%s<button %s %s
onclick='py.link("ease%d");'>
%s</button></td>''' % (
            beam, due, extra,
            ((' title=" '+_('Shortcut key: %s') % i)+' "'), i, label)

    buf = '<table cellpading=0 cellspacing=0><tr>'
    for ease, lbl, beams in answerButtonList(self):
        buf += but(ease, lbl, beams)
    buf += '</tr></table>'
    script = """
    <style>table tr td button { width: 100%; } </style>
<script>$(function () { $('#defease').focus(); });</script>"""
    return buf + script

Reviewer._answerButtons =\
    wrap(Reviewer._answerButtons, myAnswerButtons, 'around')

