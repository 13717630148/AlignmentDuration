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
Created on Mar 4, 2016

@author: joro
'''
import os
import subprocess
import numpy
from src.align.ParametersAlgo import ParametersAlgo
import logging
import sys
import csv
from src.align.FeatureExtractor import extractPredominantPitch
from src.utilsLyrics.Utilz import writeCsv

parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.path.pardir,  os.path.pardir)) 

pathPycomp = os.path.join(parentDir, 'pycompmusic')
if pathPycomp not in sys.path:
    sys.path.append(pathPycomp)
from compmusic import dunya





class VocalNote(object):
    def __init__(self,onsetTime, noteDuration):
        self.onsetTime = onsetTime
        self.noteDuration = noteDuration

class OnsetDetector(object):
    '''
    extract note onsets for one chunk
    '''

    def __init__(self, sectionLink):
        self.vocalNotes = []
        self.sectionLink = sectionLink

    def parseNoteOnsetsGrTruth(self, groundTruthNotesURI):
        
        '''
        from annotated notes for score-following for a segment from given sectionLink.
        
        
        '''
        startTime = self.sectionLink.beginTs
        endTime = self.sectionLink.endTs
        
        wholeRecordingVocalNotes = []
        from csv import reader
        with open(groundTruthNotesURI) as f:
            r = reader(f, delimiter='\t')
            for row in r:
                try:
                    
                    onset = row[0]
                    duration = row[2]
                except Exception:
                    sys.exit('row {} in file {}  should have at least 3 tokens  '.format( row, groundTruthNotesURI))

                wholeRecordingVocalNotes.append(  VocalNote(float(onset), duration ) ) # 
    
        
        ######## select part of onset times corresponding to segment
        i = 0
        while i< len(wholeRecordingVocalNotes) and startTime > wholeRecordingVocalNotes[i].onsetTime:
            i+=1
            
        while i< len(wholeRecordingVocalNotes) and endTime >= wholeRecordingVocalNotes[i].onsetTime :
            self.vocalNotes.append(  VocalNote( wholeRecordingVocalNotes[i].onsetTime - startTime, wholeRecordingVocalNotes[i].noteDuration )  )
            i+=1
        
        if len(self.vocalNotes) == 0:
            logging.warning("in section from {} to {} there are no annotated onsets. No implemented".format(startTime, endTime))
        
        
        outFileURI = self.sectionLink.URIRecordingChunk + '.gr_truth.csv'
        writeCsv(outFileURI, self.vocalNotes, 0)
        return outFileURI
    
    def extractNoteOnsets(self, audioFileURI):
        '''
        with automatic note segmenter cante. 
        extract note onsets for whole audio
        '''
        
        onsetsURI = os.path.splitext(audioFileURI)[0] + '.notes.csv'
        pitchURI = os.path.splitext(audioFileURI)[0] + '.pitch.csv'
        if not os.path.isfile(onsetsURI):
            
            if not os.path.isfile(pitchURI):
                extractedPitchList = extractPredominantPitch(audioFileURI)
                #         ######## SERIALIZE
                # ignore last entry (probability)
                for i, row in enumerate(extractedPitchList):
                    row = row[:-1]
                    extractedPitchList[i]=row
                 
                writeCsv(pitchURI, extractedPitchList)

            print 'extracting note onsets for {}...'.format(audioFileURI)
            cante = '/Users/joro/Downloads/cante-beta-csv/DerivedData/cante-static/Build/Products/Debug/cante-static'
            canteCommand = [cante, pitchURI, audioFileURI ]
            pipe= subprocess.Popen(canteCommand)
            pipe.wait()
            
            
        from csv import reader
        
        with open(onsetsURI) as f:
            r = reader(f)
            for row in r:
                currTs = float( "{0:.2f}".format(float(row[0].strip())) )
    #             currTs = round(float(row[0][0]),2)
                durationDummy = 1
                self.vocalNotes.append(VocalNote(currTs, durationDummy))
        return onsetsURI
    
                
    def onsetTsToOnsetFrames(self,  lenObservations):
        '''
        for each timestamp of array  self.vocalNotes sets a the corresponding frame number to 1
        sets one to more than one frame using ParametersAlgo.ONSET_TOLERANCE_WINDOW
        '''
        noteOnsets = numpy.zeros((lenObservations,)) # init note onsets as all zeros: e.g. with normal transMatrices
        if self.vocalNotes != None:
        
            
            for vocalNote in self.vocalNotes:
                frameNum = tsToFrameNumber(vocalNote.onsetTime)
                if frameNum >= lenObservations or frameNum < 0:
                    logging.warning("onset has ts {} < first frame or > totalnumFrames {}".format(vocalNote.onsetTime, lenObservations))
                    continue
                onsetTolInFrames = ParametersAlgo.NUMFRAMESPERSECOND * ParametersAlgo.ONSET_TOLERANCE_WINDOW
                fromFrame = max(0, frameNum - onsetTolInFrames)
                toFrame = min(lenObservations, frameNum + onsetTolInFrames)
                noteOnsets[fromFrame:toFrame + 1] = 1  
        
        return noteOnsets  
    

def getDistFromEvent(noteOnsets, t):
        '''
        get distance in frames from time t to closest onset
        start at onset and keep looking right and left simultanously while it finds a 1
        
        
        Parameters
        -------------------------
        noteOnsets: list of size equal to timeframes
            1-s at timeframes with onsets, all other frames = 0
        
        Returns
        --------------------------
        dist
        iFrame: int
            index of frame with closest 
         
        '''
#        ##### DEBUG: 
#         for idx, onset in  enumerate(noteOnsets):
#             print idx, ": ", onset
        
        #### find closest onset 
        dist = 0
        rightIdx = t
        leftIdx = t
        while  noteOnsets[rightIdx] == 0 and  noteOnsets[leftIdx] == 0:
            dist += 1
            rightIdx =  min(t + dist, noteOnsets.shape[0]-1)
            leftIdx = max(t - dist, 0) 
        if noteOnsets[rightIdx] == 1:
            iFrame = rightIdx
        else:
            iFrame = leftIdx
        return dist, iFrame

def tsToFrameNumber(ts):
    '''
    get which frame is for a given ts, according to htk's feature extraction  
    '''
    return   max (0, int(math.floor( (ts - ParametersAlgo.WINDOW_SIZE/2.0) * ParametersAlgo.NUMFRAMESPERSECOND)) )
 
 
def frameNumberToTs(frameNum):
    '''
    get which ts is for a given frame, according to htk's feature extraction  
    '''
    return float(frameNum) /    float(ParametersAlgo.NUMFRAMESPERSECOND) + ParametersAlgo.WINDOW_SIZE/2.0
  

def remove4thRow(annotationFileURI):
    '''
    convert from 4 rows annotation to 3 rows (without last textual one)
    used for annotations in turkish_makam_audio_score_alignment_dataset to prepare them for matlab evaluation script of Nadine
    '''

#     annotationFileURI = '/Users/joro/Documents/Phd/UPF/turkish_makam_audio_score_alignment_dataset/data/nihavent--sarki--kapali_curcuna--kimseye_etmem--kemani_sarkis_efendi/567b6a3c-0f08-42f8-b844-e9affdc9d215/alignedNotes.txt'
    with open(annotationFileURI, 'rb') as csvfile:
            score = csv.reader(csvfile, delimiter='\t')
            for idx, row in enumerate(score):
                
                print row[0] + '\t' + row[1] + '\t' + row[2] 

    
if __name__ == '__main__':
    
#     audioFileURI = '/Users/joro/Documents/Phd/UPF/voxforge/myScripts/HMMDuration/hmm/examples/KiseyeZeminPhoneLevel_2_zemin.wav'
    audioFileURI = '/Users/joro/Downloads/ISTANBULSymbTr2/567b6a3c-0f08-42f8-b844-e9affdc9d215/567b6a3c-0f08-42f8-b844-e9affdc9d215.wav'
    extractPredominantPitch(audioFileURI) 
     
    od = OnsetDetector() 
    od.extractNoteOnsets(audioFileURI)
    
#     noteOnsets = numpy.zeros((8,))
#     noteOnsets[2] = 1
#     noteOnsets[7] = 1
#     n = getDistFromEvent(noteOnsets, 7)
#     print n
