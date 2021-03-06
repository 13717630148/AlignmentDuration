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
Created on Dec 28, 2015

@author: joro
'''
import sys
from ParametersAlgo import ParametersAlgo
from LyricsWithModelsGMM import LyricsWithModelsGMM
from LyricsWithModelsHTK import LyricsWithModelsHTK
import logging
from LyricsParsing import loadOraclePhonemes
import tempfile
import os
import numpy
import pickle
audioTmpDir = tempfile.mkdtemp()

class _SectionLinkBase():

    
    def __init__(self, URIWholeRecording, beginTs, endTs):
        '''
        Constructor
        '''
        basename = os.path.basename(URIWholeRecording)
        dirname_ = os.path.dirname(URIWholeRecording)
#         self.URIRecordingChunk = os.path.join(audioTmpDir, basename + "_" + "{}".format(beginTs) + '_' + "{}".format(endTs))
        self.URIRecordingChunk = os.path.join(dirname_, basename + "_" + "{}".format(beginTs) + '_' + "{}".format(endTs))
        
        self.beginTs = beginTs
        self.endTs = endTs
        # composition section. could be LyricsSection or ScoreSection
        self.section = None
        
        
    def setSection(self, section):
        '''
        could be LyricsSection or ScoreSection
        '''
        self.section = section
        
      
    def setSelectedSections(self, sections):
        '''
        selected sections after alignment with lyrics refinent 
        '''
        self.selectedSections = sections
    
    def set_begin_end_indices(self, token_begin_idx, token_end_idx):
        '''
        the indices in the annotation TextGrid
        '''
        self.token_begin_idx = token_begin_idx
        self.token_end_idx = token_end_idx
    
    def loadSmallAudioFragment( self, featureExtractor, extractedPitchList,  URIrecordingNoExt, htkParserOrFold):
        '''
        test duration-explicit HMM with audio features from real recording and htk-loaded htkParserOrFold
        asserts it works. no results provided 
        '''
        
        featureVectors = featureExtractor.loadMFCCs(URIrecordingNoExt, extractedPitchList,  self) #     featureVectors = featureVectors[0:1000]
        
#         tmp_obs_file = self.URIRecordingChunk + '.MFCCs.pkl'
#         labels = numpy.zeros( len(featureVectors), dtype = 'float32')
#          
#         with open(tmp_obs_file,'w') as f:
#             pickle.dump((featureVectors,labels),f)     
        
#         htkParserOrFold  = 1
#         self.lyricsWithModels = LyricsWithModelsGMM( self.section.lyrics, htkParserOrFold,  ParametersAlgo.DEVIATION_IN_SEC, ParametersAlgo.WITH_PADDED_SILENCE)
        
        if ParametersAlgo.FOR_JINGJU: # they are one-state
            self.lyricsWithModels = LyricsWithModelsGMM( self.section.lyrics, htkParserOrFold,  ParametersAlgo.DEVIATION_IN_SEC, ParametersAlgo.WITH_PADDED_SILENCE)
        elif ParametersAlgo.FOR_MAKAM:
            self.lyricsWithModels = LyricsWithModelsHTK( self.section.lyrics, htkParserOrFold,  ParametersAlgo.DEVIATION_IN_SEC, ParametersAlgo.WITH_PADDED_SILENCE)
        else:
            sys.exit('neither JINGJU nor MAKAM.')
    
        if self.lyricsWithModels.getTotalDuration() == 0:
            logging.warning("total duration of segment {} = 0".format(self.URIRecordingChunk))
            return None, None, None
        
        
        # needed only with duration htkParserOrFold
        self.lyricsWithModels.duration2numFrameDuration(featureVectors, URIrecordingNoExt)
#         self.lyricsWithModels.printPhonemeNetwork()

        return featureVectors
    
    
    
    def loadSmallAudioFragmentOracle(self):
        raise NotImplementedError('loadSmallAudioFragmentOracle not implemeted')    
        
    
    def __repr__(self):
        return "Section from  {}  to {}".format( self.beginTs, self.endTs)
        
        

class SectionLinkMakam(_SectionLinkBase):
    '''
    classdocs
    '''
    

    def __init__(self, URIWholeRecording, melodicStructure, beginTs, endTs):
        '''
        Constructor
        '''
        _SectionLinkBase.__init__(self, URIWholeRecording, beginTs, endTs)
        self.melodicStructure = melodicStructure
  
        
    def loadSmallAudioFragmentOracle( self, htkParser, fromSyllableIdx = 0, toSyllableIdx = 9):
        '''
        
        '''
        
        # lyricsWithModelsORacle used only as helper to get its stateNetwork with durs, but not functionally - e.g. their models are not used
        withPaddedSilence = False # dont model silence at end and beginnning. this away we dont need to do annotatation of sp at end and beginning 
        self.lyricsWithModels = LyricsWithModelsHTK(self.section.lyrics,  htkParser,  ParametersAlgo.DEVIATION_IN_SEC, withPaddedSilence)
        
        
        URIrecordingTextGrid  = self.URIRecordingChunk  + '.TextGrid'
        
        phonemeAnnotaions = loadOraclePhonemes(URIrecordingTextGrid, fromSyllableIdx, toSyllableIdx)   
    
        
        self.lyricsWithModels.setPhonemeNumFrameDurs( phonemeAnnotaions)
        
        
        
        

        


          
              
        
        
class SectionAnnoMakam(SectionLinkMakam):
    '''
    unlike a like that has only match to melodicStrcuture, sectionAnno has link to exactSetion through tuple (melodicStructure, lyricsStucture)
    SO it can be matched unambigously to a particular ScoreSection
    '''
    
    def __init__(self, URIWholeRecording, melodicStructure, lyricStructure, beginTs, endTs):
        SectionLinkMakam.__init__(self, URIWholeRecording, melodicStructure, beginTs, endTs)
        self.lyricStructure = lyricStructure
        
    
    def matchToSection(self,  scoreSections):
        if self.lyricStructure == None:
           sys.exit('cannot match link to section. No lyricStructure defined')
        
        for scoreSection in scoreSections:
            if self.melodicStructure == scoreSection.melodicStructure and self.lyricStructure == scoreSection.lyricStructure:
                self.setSection(scoreSection)
                break  