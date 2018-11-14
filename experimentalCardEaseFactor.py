# https://eshapard.github.io/
#
from __future__ import division
from anki.hooks import addHook
from aqt import mw
from aqt.utils import tooltip
#from aqt.utils import showInfo
import math
targetRatio = 0.85
showCardStats=True #Show the card stats in a pop-up
minRevs = 4 #minium number of reviews before ease factors are adjusted

def findSuccessRate(cardID):
    reviews = mw.col.db.scalar("select count() from revlog where type = 1 and cid = ?", cardID)
    if not reviews or reviews < minRevs:
        return 0, 0, 0, 0
    correct = mw.col.db.scalar("select count() from revlog where type = 1 and cid = ? and ease > 1", cardID)
    if not correct: correct = 0
    avgEase = mw.col.db.scalar("select avg(1000*ivl/lastIvl) from revlog where type = 1 and cid = ? and lastIvl > 0 and ivl > 0 group by cid", cardID)
    if not avgEase:
        return 0, 0, 0, 0
    factor = int(round(avgEase))
    successRate = float(correct)/float(reviews)
    return reviews, correct, factor, successRate

def calcNewEase(sRate, avgFactor, curFactor):
    top = int(round(curFactor * 1.2))
    bottom = int(round(curFactor * 0.8))
    #Ebbinghaus formula
    if sRate > 0.99:
        sRate = 0.99 # ln(1) = 0; avoid divide by zero error
    if sRate < 0.01:
        sRate = 0.01
    dRatio = math.log(targetRatio) / math.log(sRate)
    #showInfo("dRatio: %s" % dRatio)
    sugFactor = int(round(avgFactor * dRatio))
    if sugFactor > top:
        sugFactor = top
    if sugFactor < bottom:
        sugFactor = bottom
    return sugFactor

def easeAdjustFunc():
    #cardObj = mw.reviewer.card
    #showInfo("%s" % cardObj)
    queue = mw.reviewer.card.queue
    if queue == 2:
        curFactor = mw.reviewer.card.factor
        cardID = mw.reviewer.card.id
        rev, cor, fac, srate = findSuccessRate(cardID)
        if rev:
            sugFactor = calcNewEase(srate, fac, curFactor)
        else: #there were no reviews, so don't change a thing.
            sugFactor = curFactor
        #quick sanity checks
        if srate < targetRatio and sugFactor > curFactor: sugFactor = curFactor #if under target, decrease factor only
        if srate > targetRatio and sugFactor < curFactor: sugFactor = curFactor #if over target, increase factor only
        if rev:
            if showCardStats: 
                tooltip("cardID: %s\nsRate: %s\navgFactor: %s\ncurFactor: %s\nsugFactor: %s" % (cardID, round(srate,2), round(fac), curFactor, sugFactor))

        #Set new card ease factor
        mw.reviewer.card.factor = sugFactor

addHook('showQuestion', easeAdjustFunc)
