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
Created on Jan 13, 2016

@author: joro
'''
import os
import sys
import json
import urllib2
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../for_makam'))



from src.for_makam.MakamRecording import parseSectionLinks
from src.align.ScoreSection import ScoreSection
from src.for_makam.MakamScore import loadMakamScore2

from src.align.LyricsAligner import LyricsAligner, extendSectionLinksSelectedSections,\
    stereoToMono, loadMakamRecording

currDir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) )


WITH_SECTION_ANNOTATIONS = 1

from src.align.ParametersAlgo import ParametersAlgo

        

def prepare_for_makam_recording(sectionMetadataURI, sectionLinksSourceURI, audioFileURI):
    '''
    convenience method
    '''
    with open(sectionLinksSourceURI) as f:
        sectionLinksDict = json.load(f)
    with open(sectionMetadataURI) as f2:
        sectionMetadataDict = json.load(f2)
           
        
###  for Juanjos pitch
#     extractedPitch = os.path.splitext(audioFileURI)[0] + '.pitch'
#     with open(extractedPitch) as f:
#         extractedPitchList = json.load(f)
    extractedPitchList = None
    audioFileURI = stereoToMono(audioFileURI)
    
    return audioFileURI, sectionMetadataDict, sectionLinksDict, extractedPitchList

def testLyricsAlign():
    
    ParametersAlgo.FOR_MAKAM = 1
    
    # test with section links. polyphonic

    symbtrtxtURI = os.path.join( currDir, '../example/nihavent--sarki--aksak--gel_guzelim--faiz_kapanci/nihavent--sarki--aksak--gel_guzelim--faiz_kapanci.txt')
    sectionMetadataURI =  os.path.join( currDir, '../example/nihavent--sarki--aksak--gel_guzelim--faiz_kapanci/nihavent--sarki--aksak--gel_guzelim--faiz_kapanci.sectionsMetadata.json' )
    sectionLinksSourceURI = os.path.join( currDir, '../example/nihavent--sarki--aksak--gel_guzelim--faiz_kapanci/18_Munir_Nurettin_Selcuk_-_Gel_Guzelim_Camlicaya/18_Munir_Nurettin_Selcuk_-_Gel_Guzelim_Camlicaya.sectionLinks.json' )
    sectionAnnosSourceURI = os.path.join( currDir, '../example/nihavent--sarki--aksak--gel_guzelim--faiz_kapanci/18_Munir_Nurettin_Selcuk_-_Gel_Guzelim_Camlicaya/727cff89-392f-4d15-926d-63b2697d7f3f.json')
    audioFileURI =  os.path.join( currDir, '../example/nihavent--sarki--aksak--gel_guzelim--faiz_kapanci/18_Munir_Nurettin_Selcuk_-_Gel_Guzelim_Camlicaya/18_Munir_Nurettin_Selcuk_-_Gel_Guzelim_Camlicaya.wav')
    
#     # test of audio working 
#     URL = 'http://dunya.compmusic.upf.edu/document/by-id/727cff89-392f-4d15-926d-63b2697d7f3f/wav?v=0.5&subtype=wave'
#     fetchFileFromURL(URL, audioFileURI)
    musicbrainzid = '727cff89-392f-4d15-926d-63b2697d7f3f'
    ParametersAlgo.POLYPHONIC = 1
    ParametersAlgo.WITH_ORACLE_ONSETS = -1
    ParametersAlgo.WITH_ORACLE_PHONEMES = 0
    ParametersAlgo.WITH_DURATIONS = 1

#####################################################  test with section anno and acapella
    # On kora.s.upf.edu
#     ParametersAlgo.PATH_TO_HCOPY = '/homedtic/georgid/htkBuilt/bin/HCopy'
   
    symbtrtxtURI = os.path.join( currDir,'../example/nihavent--sarki--kapali_curcuna--kimseye_etmem--kemani_sarkis_efendi/nihavent--sarki--kapali_curcuna--kimseye_etmem--kemani_sarkis_efendi.txt')
    sectionMetadataURI =  os.path.join( currDir, '../example/nihavent--sarki--kapali_curcuna--kimseye_etmem--kemani_sarkis_efendi/nihavent--sarki--kapali_curcuna--kimseye_etmem--kemani_sarkis_efendi.sectionsMetadata.json' )
    sectionAnnosSourceURI = os.path.join( currDir, '../example/nihavent--sarki--kapali_curcuna--kimseye_etmem--kemani_sarkis_efendi/567b6a3c-0f08-42f8-b844-e9affdc9d215.json' )
    audioFileURI =  os.path.join( currDir, '../example/nihavent--sarki--kapali_curcuna--kimseye_etmem--kemani_sarkis_efendi/02_Kimseye.wav')
    musicbrainzid = '567b6a3c-0f08-42f8-b844-e9affdc9d215'
     
    ParametersAlgo.POLYPHONIC = 0
    ParametersAlgo.WITH_ORACLE_ONSETS = -1
    ParametersAlgo.DETECTION_TOKEN_LEVEL= 'phonemes'
    ParametersAlgo.DETECTION_TOKEN_LEVEL= 'words'
    ParametersAlgo.WITH_ORACLE_PHONEMES = 0
    ParametersAlgo.WITH_DURATIONS = 0
    
    if WITH_SECTION_ANNOTATIONS:
        sectionLinksSourceURI = sectionAnnosSourceURI
    
    audioFileURI, sectionMetadataDict, sectionLinksDict, extractedPitchList = prepare_for_makam_recording(sectionMetadataURI, sectionLinksSourceURI, audioFileURI)               
    
    recording = loadMakamRecording(musicbrainzid, audioFileURI, symbtrtxtURI, sectionMetadataDict, sectionLinksDict,  WITH_SECTION_ANNOTATIONS)
    

    la = LyricsAligner(recording, WITH_SECTION_ANNOTATIONS, ParametersAlgo.PATH_TO_HCOPY)
    
    outputDir = os.path.join(currDir, '../example/output/')
    noteOnsetAnnotationDir = '/Users/joro/Downloads/ISTANBULSymbTr2/'
    
    la.alignRecording( extractedPitchList, outputDir)
    
    #### results
    sectionDetectedList = []
    if WITH_SECTION_ANNOTATIONS:
        sectionLinks = la.recording.sectionAnnos
    else:
        sectionLinks = la.recording.sectionLinks
    
    for sectionLink in sectionLinks:
        if hasattr(sectionLink, 'detectedTokenList'):
            sectionDetectedList.append(sectionLink.detectedTokenList)
      
    ret = {'alignedLyricsSyllables':{}, 'sectionlinks':{} }
    ret['alignedLyricsSyllables'] = sectionDetectedList
    ret['sectionlinks'] = sectionLinksDict
    print ret
    
    la.evalAccuracy(ParametersAlgo.EVAL_LEVEL)



    

def testExtendSectionLinksSelectedSections():
    '''
    test if extending a sections Links file works well
    extendSectionLinksSelectedSections(sectionLinksDict, sectionLinks)
    '''
    sectionLinks = parseSectionLinks(sectionLinksDict)
  
    makamScore = loadMakamScore2(symbtrtxtURI, sectionMetadataDict )
    
    # changes one test section link as if it were aligned 
    testSectionLink = sectionLinks[1]
    probabaleSections = makamScore.getProbableSectionsForMelodicStructure(testSectionLink)
    selectedSection = ScoreSection('blah', 1, 20, 'B2', 'B1')
    selectedSectionsSameLyrics =  makamScore.getSectionsSameLyrics( selectedSection, probabaleSections)
    testSectionLink.setSelectedSections(selectedSectionsSameLyrics)
    
    extendSectionLinksSelectedSections(sectionLinksDict, sectionLinks)
    print sectionLinksDict
    


    

# def testDecoding():
#     
#     lyricsWithModels = LyricsWithModels(lyrics, htkParser,  ParametersAlgo.DEVIATION_IN_SEC, ParametersAlgo.WITH_PADDED_SILENCE)
#     decoder = Decoder(lyricsWithModels, URIRecordingChunkResynthesizedNoExt, alpha)



def fetchFileFromURL(URL, outputFileURI):
        print "fetching file from URL {} ...  ".format(URL) 
        try:
            response = urllib2.urlopen(URL)
            a = response.read()
        except Exception:
            "...maybe URL has changed"
        
        with open(outputFileURI,'w') as f:
            f.write(a)

if __name__ == '__main__':
    testLyricsAlign()
#     testLyricsAlignOracle()
#     testExtendSectionLinksSelectedSections()
#     testMakamRecording()