# Copyright (C) 2014-2018  Music Technology Group - Universitat Pompeu Fabra
#
# This file is part of AlignmentDuration:  tool for Lyrics-to-audio alignment with syllable duration modeling
# and is modified from https://github.com/guyz/HMM

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
Created on Jun 10, 2015

@author: joro
'''
import numpy
from src.hmm.continuous.DurationGMHMM import DurationGMHMM
from hmm.discrete import DiscreteHMM
from main import decode, loadSmallAudioFragment
import os
import sys
from hmm.examples.main import  getDecoder
from src.utilsLyrics.Utilz import tokenList2TabFile
from src.align.LyricsAligner import HMM_LIST_URI, MODEL_URI
from hmm.Path import Path, visualizeMatrix

# file parsing tools as external lib 
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.path.pardir,os.path.pardir )) 
print parentDir

pathJingjuAlignment = os.path.join(parentDir, 'AlignmentDuration')
if not pathJingjuAlignment in sys.path:
    sys.path.append(pathJingjuAlignment)

from src.align.MakamScore import  loadMakamScore2


# parser of htk-build speech models_makam
pathHtkModelParser = os.path.join(parentDir, 'pathHtkModelParser')
sys.path.append(pathHtkModelParser)
from htkparser.htk_converter import HtkConverter

from src.utilsLyrics.Utilz import readListOfListTextFile

pathToComposition = '/Users/joro/Documents/Phd/UPF/turkish-for_makam-lyrics-2-audio-test-data-synthesis/nihavent--sarki--aksak--bakmiyor_cesm-i--haci_arif_bey/'
URIrecordingNoExt = '/Users/joro/Documents/Phd/UPF/ISTANBUL/safiye/01_Bakmiyor_1_zemin'
whichSection = 1

# # test with synthesis
# pathToComposition = '/Users/joro/Documents/Phd/UPF/turkish-for_makam-lyrics-2-audio-test-data-synthesis/nihavent--sarki--aksak--bakmiyor_cesm-i--haci_arif_bey/'
# URIrecordingNoExt = '/Users/joro/Documents/Phd/UPF/turkish-for_makam-lyrics-2-audio-test-data-synthesis/nihavent--sarki--aksak--bakmiyor_cesm-i--haci_arif_bey/04_Hamiyet_Yuceses_-_Bakmiyor_Cesm-i_Siyah_Feryade/04_Hamiyet_Yuceses_-_Bakmiyor_Cesm-i_Siyah_Feryade'
# whichSection = 1


pathToComposition ='/Users/joro/Documents/Phd/UPF/turkish-for_makam-lyrics-2-audio-test-data-synthesis/segah--sarki--curcuna--olmaz_ilac--haci_arif_bey/'
URIrecordingNoExt = '/Users/joro/Documents/Phd/UPF/ISTANBUL/guelen/01_Olmaz_2_zemin'
whichSection = 2

pathToComposition ='/Users/joro/Documents/Phd/UPF/turkish-for_makam-lyrics-2-audio-test-data-synthesis/nihavent--sarki--curcuna--kimseye_etmem--kemani_sarkis_efendi/'
symbTr =  pathToComposition + ''
URIrecordingNoExt = '/Users/joro/Documents/Phd/UPF/voxforge/myScripts/HMMDuration/hmm/examples/KiseyeZeminPhoneLevel_2_zemin'
whichSection = 2

import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

pathEvaluation = os.path.join(parentDir, 'AlignmentEvaluation')
sys.path.append(pathEvaluation)
from AccuracyEvaluator import _evalAccuracy


pathJingjuAlignment = os.path.join(parentDir, 'JingjuAlignment')
if not pathJingjuAlignment in sys.path:
    sys.path.append(pathJingjuAlignment)


def test_simple():
    n = 2
    m = 2
    d = 2
    pi = numpy.array([0.5, 0.5])
    A = numpy.ones((n,n),dtype=numpy.double)/float(n)
    
    w = numpy.ones((n,m),dtype=numpy.double)
    means = numpy.ones((n,m,d),dtype=numpy.double)
    covars = [[ numpy.matrix(numpy.eye(d,d)) for j in xrange(m)] for i in xrange(n)]
    
    w[0][0] = 0.5
    w[0][1] = 0.5
    w[1][0] = 0.5
    w[1][1] = 0.5    
    means[0][0][0] = 0.5
    means[0][0][1] = 0.5
    means[0][1][0] = 0.5    
    means[0][1][1] = 0.5
    means[1][0][0] = 0.5
    means[1][0][1] = 0.5
    means[1][1][0] = 0.5    
    means[1][1][1] = 0.5    

    gmmhmm = DurationGMHMM(n,m,d,A,means,covars,w,pi,init_type='user',verbose=True)
    GMHMM
    
    obs = numpy.array([ [0.3,0.3], [0.1,0.1], [0.2,0.2]])
    
    print "Doing Baum-welch"
    gmmhmm.train(obs,10)
    print
    print "Pi",gmmhmm.pi
    print "transMatrix",gmmhmm.transMatrix
    print "weights", gmmhmm.w
    print "means", gmmhmm.means
    print "covars", gmmhmm.covars
    
def test_rand():
    gmmhmm,d = makeTestDurationHMM()
    obs = numpy.array((0.6 * numpy.random.random_sample((40,d)) - 0.3), dtype=numpy.double)
    
    print "Doing Baum-welch"
    gmmhmm.train(obs,1000)
    print
    print "Pi",gmmhmm.pi
    print "transMatrix",gmmhmm.transMatrix
    print "weights", gmmhmm.w
    print "means", gmmhmm.means
    print "covars", gmmhmm.covars
    
def test_discrete():

    ob5 = (3,1,2,1,0,1,2,3,1,2,0,0,0,1,1,2,1,3,0)
    print "Doing Baum-welch"
    
    atmp = numpy.random.random_sample((4, 4))
    row_sums = atmp.sum(axis=1)
    a = atmp / row_sums[:, numpy.newaxis]    

    btmp = numpy.random.random_sample((4, 4))
    row_sums = btmp.sum(axis=1)
    b = btmp / row_sums[:, numpy.newaxis]
    
    pitmp = numpy.random.random_sample((4))
    pi = pitmp / sum(pitmp)
    
    hmm2 = DiscreteHMM(4,4,a,b,pi,init_type='user',precision=numpy.longdouble,verbose=True)
    hmm2.train(numpy.array(ob5*10),100)
    print "Pi",hmm2.pi
    print "transMatrix",hmm2.transMatrix
    print "B", hmm2.B


def makeTestDurationHMM():
    '''
    generate some random models_makam. 
    '''
    n = 5
    d = 2
    m = 3
    atmp = numpy.random.random_sample((n, n))
    row_sums = atmp.sum(axis=1)
    a = numpy.array(atmp / row_sums[:, numpy.newaxis], dtype=numpy.double)    

    wtmp = numpy.random.random_sample((n, m))
    row_sums = wtmp.sum(axis=1)
    w = numpy.array(wtmp / row_sums[:, numpy.newaxis], dtype=numpy.double)
    
    means = numpy.array((0.6 * numpy.random.random_sample((n, m, d)) - 0.3), dtype=numpy.double)
    covars = numpy.zeros( (n,m,d,d) )
    
    for i in xrange(n):
        for j in xrange(m):
            for k in xrange(d):
                covars[i][j][k][k] = 1    
    
    pitmp = numpy.random.random_sample((n))
    pi = numpy.array(pitmp / sum(pitmp), dtype=numpy.double)

    gmmhmm = DurationGMHMM(n,m,d,a,means,covars,w,pi,init_type='user',verbose=True)
    return    gmmhmm, d  


def testRand_DurationHMM():
    '''
    test with audio features from real recording, but some random models_makam, not trained models_makam 
    TODO: this might not work. rewrite
    '''
    durGMMhmm,d = makeTestDurationHMM()
    
    durGMMhmm.setALPHA(0.97)
    
    listDurations = [70,30,20,10,20];
    durGMMhmm.setDurForStates(listDurations)
    
    
    observationFeatures = numpy.array((0.6 * numpy.random.random_sample((2,d)) - 0.3), dtype=numpy.double)
#     observationFeatures = loadMFCCs(URIrecordingNoExt)

    decode(lyricsWithModels, observationFeatures, 'testRecording')
    
        
#     # test computePhiStar
#     currState = 1
#     currTime = 25
#     phiStar, fromState, maxDurIndex = durGMMhmm.computePhiStar(currTime, currState)
#     print "phiStar={}, maxDurIndex={}".format(phiStar, maxDurIndex)

def test_backtrackWithLyrics(lyricsWithModels, URIrecordingNoExt):

    decoder = getDecoder(lyricsWithModels, URIrecordingNoExt)
    absPathPsi = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'psi' )
    psi = numpy.loadtxt(absPathPsi)
    
    absPathChi = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'chi' )
    chi = numpy.loadtxt(absPathChi)
    decoder. backtrack( chi, psi)
    

def testBackTrack():  
    
    chiBackPointer = None
    absPathPsi = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_psi' )
    psiBackPointer = numpy.loadtxt(absPathPsi)

    absPathPhi = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_phi' )
    phi = numpy.loadtxt(absPathPhi)
    
    class HmmStub():
        def __init__(self,psi, phi):
            self.phi = phi
            self.psi = psi
    
    hmmStub = HmmStub(psiBackPointer, phi)
    phiDummy = psiBackPointer
    
    
    path =  Path(chiBackPointer, psiBackPointer, phiDummy, hmmStub)
#     set BACKTRACK_MARGIN_PERCENT to 0 to make backtracking only once from last state 
    print "path is {}".format(path.pathRaw)
    # shoud be 01222455 # 
    
    

def test_decoding(pathToComposition, whichSection):
    '''
    read initialized matrix from file. useful to test getMaxPhi with vector
    '''
    
    withSynthesis = True
    
    makamScore = loadMakamScore2(pathToComposition)
    
    lyrics = makamScore.getLyricsForSection(whichSection)
    
    
    lyricsWithModels, observationFeatures, URIRecordingChunk = loadSmallAudioFragment(lyrics, 'dummyExtractedPitchList',   URIrecordingNoExt,  fromTs=-1, toTs=-1)
    
    decoder = getDecoder(lyricsWithModels, URIRecordingChunk)
    
    decoder.hmmNetwork.phi = numpy.loadtxt('phi_init')
    chiBackPointer, psiBackPointer = decoder.hmmNetwork._viterbiForcedDur()


def test_initialization(lyricsWithModels, URIrecordingNoExt, observationFeatures):
    '''
    just initialilzation step.
    '''
    decoder = getDecoder(lyricsWithModels, URIrecordingNoExt)
    #  init
    decoder.hmmNetwork.initDecodingParameters(observationFeatures)


# def test_oracle(URIrecordingNoExt, pathToComposition, whichSection):
#     '''
#     read phoneme-level ground truth and test.
#     !!! not sure where this is used
#     '''
#     withSynthesis = False
#     
#     makamScore = loadMakamScore2(pathToComposition)
#     lyrics = makamScore.getLyricsForSection(whichSection)
#     
#     
#     if logger.level == logging.DEBUG:
#         lyrics.printPhonemeNetwork()
#     
#     # consider only part of audio
#     fromTs = 0; toTs = 20.88
#     # since not all TextGrid might be on phoneme level
#     fromPhonemeIdx  = 1; toPhonemeIdx = 42
#     tokenLevelAlignedSuffix = '.syllables_oracle'
#     
#     detectedAlignedfileName = URIrecordingNoExt + tokenLevelAlignedSuffix
#     if os.path.isfile(detectedAlignedfileName):
#         print "{} already exists. No decoding".format(detectedAlignedfileName)
#         detectedTokenList  = readListOfListTextFile(detectedAlignedfileName)
#         
#     else:
#         detectedTokenList = decodeWithOracle(lyrics, URIrecordingNoExt, fromTs, toTs, fromPhonemeIdx, toPhonemeIdx)
#           
#         detectedAlignedfileName = URIrecordingNoExt + tokenLevelAlignedSuffix
#         if not os.path.isfile(detectedAlignedfileName):
#             detectedAlignedfileName =  tokenList2TabFile(detectedTokenList, URIrecordingNoExt, tokenLevelAlignedSuffix)
#             
#         
#     ANNOTATION_EXT = '.TextGrid'
#     # eval on phrase level
#     evalLevel = 2
#     correctDuration, totalDuration = _evalAccuracy(URIrecordingNoExt + ANNOTATION_EXT, detectedTokenList, evalLevel, -1, -1 )
#     print "accuracy= {}".format(correctDuration / totalDuration)
#     
#     return detectedTokenList


def test_vocalPrediction():
    '''
    vocal prediction used in Jingju
    not sure if this works
    '''
    #     inputFile = '/Users/joro/Documents/Phd/UPF/voxforge/myScripts/segmentation/data/laoshengxipi02.wav'
#     detectedSegments, outputFile, windowSize = doitSegmentVJP(inputFile)
    
    VJPpredictionFile = '/Users/joro/Documents/Phd/UPF/voxforge/myScripts/segmentationShuo/data/output_VJP_laoshengxipi02/predictionVJP.txt'
    smoothedPred = parsePrediction(VJPpredictionFile)
    windowLen = 0.25
    segStart, segDuration, segPred = prepareAnnotation(smoothedPred,  windowLen)
    for i in range(len(segStart)):
        print "start: " + str(segStart[i]) + "\tend: " + str((segStart[i] + segDuration[i])) + "\t" + str(segPred[i]) 




    

if __name__ == '__main__':    
    #test_simple()
    # test_rand()
    #test_discrete()
    # testRand_DurationHMM()
    
#     test_oracle(URIrecordingNoExt, pathToComposition, whichSection)

#     testBackTrack()
    phi = numpy.loadtxt('/Users/joro/Downloads/phi')
#     print psi[-4:-1, :]
    visualizeMatrix(phi[-1000:-1, :])

#####################     for all tetst below include these 3 lines for lyrics:
    withSynthesis = True
    makamScore = loadMakamScore2(pathToComposition) # loadMakamScore2  is deprecated
    lyrics = makamScore.getLyricsForSection(whichSection)
    htkParser = HtkConverter()
    htkParser.load(MODEL_URI, HMM_LIST_URI)
    
    lyricsWithModels, observationFeatures, URIrecordingChunk = loadSmallAudioFragment(lyrics, 'dummyExtractedPitchList',    URIrecordingNoExt,  fromTs=-1, toTs=-1)
#     
#     decode(lyricsWithModels, observationFeatures, URIrecordingNoExt)
#   
    
    test_backtrackWithLyrics(lyricsWithModels, URIrecordingNoExt)
#     test_initialization(lyricsWithModels, URIrecordingNoExt, observationFeatures)

   
#     test_decoding(pathToComposition, whichSection)