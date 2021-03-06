# -*- coding: utf-8 -*-

# Copyright (C) 2014-2017  Music Technology Group - Universitat Pompeu Fabra
#
# This file is part of AlignmentDuration:  tool for Lyrics-to-audio alignment with syllable duration modeling

#
# AlignmentDuration is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation (FSF), either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the Affero GNU General Public License
# version 3 along with this program. If not, see http://www.gnu.org/licenses/



'''
Created on Sep 23, 2015

@author: joro

'''

import os
import sys
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir)) 

if parentDir not in sys.path:
    sys.path.append(parentDir)
    

from doitOneChunkAlign import doitOneChunkAlign, loadLyrics
from lyricsParser import \
    divideIntoSentencesFromAnnoWithSil
from MusicXmlParser import MusicXMLParser

def readPinYinTest():
    URIrecordingNoExt = '/Users/joro/Documents/Phd/UPF/ariasAnnotated/2-16_伴奏：听兄言不由我花容惊变.TextGrid'
    allSentences = divideIntoSentencesFromAnnoWithSil(URIrecordingNoExt)
    print allSentences
    
def loadLyricsTest():
    URIrecordingNoExt ='/Users/joro/Documents/Phd/UPF/JingjuSingingAnnotation/lyrics2audio/praat/fold2/wangjiangting_dushoukong'
    
    lyricsTextGrid = URIrecordingNoExt + '.TextGrid'
    listSentences = divideIntoSentencesFromAnnoWithSil(lyricsTextGrid, False) #uses TextGrid annotation to derive structure
    whichSentence = 1
    sentence = listSentences[whichSentence]
    

    loadLyrics(URIrecordingNoExt, sentence)

def doitOneChunkTest():
    '''
    test
        '''
    URIrecordingNoExt = os.path.abspath('dan-xipi_01')
    
    URIrecordingNoExt = '/Users/joro/Documents/Phd/UPF/JingjuSingingAnnotation/lyrics2audio/praat/yutangchun_yutangchun'
    URIrecordingNoExt = '/Users/joro/Documents/Phd/UPF/JingjuSingingAnnotation/lyrics2audio/praat/xixiangji_biyuntian'

    URIrecordingNoExt = '/Users/joro/Documents/Phd/UPF/JingjuSingingAnnotation/lyrics2audio/praat/wangjiangting_dushoukong'
    
    URIrecordingNoExt = '/Users/joro/Documents/Phd/UPF/JingjuSingingAnnotation/lyrics2audio/praat/shiwenhui_tingxiongyan'
    URIrecordingNoExt = '/Users/joro/Documents/Phd/UPF/JingjuSingingAnnotation/lyrics2audio/praat/zhuangyuanmei_fudingkui'
    
    URIrecordingNoExt = '/Users/joro/Documents/Phd/UPF/arias_dev_01_t_70/dan-xipi_02'
    URIrecordingNoExt ='/Users/joro/Documents/Phd/UPF/JingjuSingingAnnotation/lyrics2audio/praat/fold2/wangjiangting_dushoukong'
    
    URIrecordingNoExt = '/Users/joro/Documents/Phd/UPF/JingjuSingingAnnotation/lyrics2audio/praat_rules/fold1/xixiangji_biyuntian'

    
    lyricsTextGrid = URIrecordingNoExt + '.TextGrid'

    whichSentence = 7

    ###########################################################
         
    withDurations = 0
    musicXMLParser = None
    musicXmlURI = URIrecordingNoExt + '_score.xml'
    
    # broken
#     musicXMLParser = MusicXMLParser(musicXmlURI, lyricsTextGrid)
    
    
    listSentences = divideIntoSentencesFromAnnoWithSil(lyricsTextGrid, False) #uses TextGrid annotation to derive structure
    sentence = listSentences[whichSentence]
    
        
    withVocalPrediction = 0
    
    withOracle  = 1
    withRules = 1
    
    from ParametersAlgo import ParametersAlgo
    ParametersAlgo.DEVIATION_IN_SEC = 3
    
    currCorrectDuration, currTotalDuration, detectedTokenList, currSentenceBeginTs = doitOneChunkAlign(URIrecordingNoExt, lyricsTextGrid, musicXMLParser, whichSentence, sentence, withOracle, withDurations, withVocalPrediction, withRules)  
    
    currAcc = currCorrectDuration / currTotalDuration
    print "sentence {}: acc ={:.2f}".format(whichSentence, currAcc)
    


    
     
if __name__ == '__main__':
#     readPinYinTest()
    doitOneChunkTest()
#     loadLyricsTest()
