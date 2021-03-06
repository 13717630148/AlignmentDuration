
# Copyright (C) 2014-2017  Music Technology Group - Universitat Pompeu Fabra
#
# This file is part of AlignmentDuration
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
Created on May 27, 2015

@author: joro
'''
import os
import sys
import numpy as np
import logging

import htkmfc
import subprocess
import essentia.standard
import math
import json

### include src folder
import os
import sys
projDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.pardir))
if projDir not in sys.path:
    sys.path.append(projDir)

import tempfile
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir, os.path.pardir)) 
pathSMS = os.path.join(parentDir, 'sms-tools')
from predominantmelodymakam.predominantmelodymakam import PredominantMelodyMakam

# print '\n sys.path:' + sys.path +  '\n'
# if pathSMS not in sys.path:
#     sys.path.append(pathSMS)

from src.smstools.workspace.harmonicModel_function import extractHarmSpec, resynthesize
# from harmonicModel_function import extractHarmSpec, resynthesize


from src.utilsLyrics.Utilz import readListOfListTextFile_gen, writeCsv
import src.utilsLyrics.UtilzNumpy



projDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)) , os.path.pardir ))



parentParentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir)) 

from ParametersAlgo import ParametersAlgo



class FeatureExtractor(object):
    def __init__(self, path_to_hcopy, sectionLink):
        self.path_to_hcopy = path_to_hcopy
        self.featureVectors = []
         
   
   
    def loadMFCCs(self, URI_recording_noExt, extractedPitchList,    sectionLink): 
        '''
        for now lead extracted with HTK, read in matlab and seriqlized to txt file
        '''
            
        
    
        URI_recording = URI_recording_noExt + '.wav'
        
        URIRecordingChunkResynthesized = sectionLink.URIRecordingChunk + '.wav'
        
        logging.info("working on sectionLink: {}".format(URIRecordingChunkResynthesized))
        
        # resynthesize audio chunk:
        if ParametersAlgo.POLYPHONIC: 
            if not os.path.isfile(URIRecordingChunkResynthesized): # only if resynth file does not exist 
                logging.info("doing harmonic models and resynthesis for segment: {} ...".format(URIRecordingChunkResynthesized))
                
                if extractedPitchList == None:
                    extractedPitchList= extractPredominantPitch( URI_recording_noExt, 2048, 128,  jointAnalysis=True, )
                hfreq, hmag, hphase, fs, hopSizeMelodia, inputAudioFromTsToTs = extractHarmSpec(URI_recording, extractedPitchList, sectionLink.beginTs, sectionLink.endTs, ParametersAlgo.THRESHOLD_PEAKS)
                resynthesize(hfreq, hmag, hphase, fs, hopSizeMelodia, URIRecordingChunkResynthesized)
        else:
            sampleRate = 44100
            loader = essentia.standard.MonoLoader(filename = URI_recording, sampleRate = sampleRate)
            audio = loader()
            audioChunk = audio[sectionLink.beginTs*sampleRate : sectionLink.endTs*sampleRate]
            monoWriter = essentia.standard.MonoWriter(filename=URIRecordingChunkResynthesized)
            monoWriter(audioChunk)
        
        # call htk to extract features
        URImfcFile = self._extractMFCCs( URIRecordingChunkResynthesized)

        # read features form binary htk file
        logging.debug("reading MFCCs from {} ...".format(URImfcFile))
        HTKFeat_reader =  htkmfc.open(URImfcFile, 'rb')
        mfccsFeatrues = HTKFeat_reader.getall()
        
        if ParametersAlgo.FOR_MAKAM and ParametersAlgo.OBS_MODEL == 'GMM': # makam mdoels  are trained with 25-dim features (no energy, no deltadeltas )
            mfccs_no_energy = mfccsFeatrues[:,0:12]
            mfccDeltas = mfccsFeatrues[:,13:26] 
            mfccsFeatrues = np.hstack((mfccs_no_energy, mfccDeltas))
        
        
        return mfccsFeatrues
    
            
    def _extractMFCCs( self, URIRecordingChunk):
            baseNameAudioFile = os.path.splitext(os.path.basename(URIRecordingChunk))[0]
            dir_ = os.path.dirname(URIRecordingChunk)
#             dir_  = tempfile.mkdtemp()
            mfcFileName = os.path.join(dir_, baseNameAudioFile  ) + '.mfc'
            
            if ParametersAlgo.OBS_MODEL == 'MLP' or ParametersAlgo.OBS_MODEL == 'MLP_fuzzy': # only one type of features trained
               PATH_TO_CONFIG_FEATURES = projDir + '/models_makam/input_files/wav_config_default'
            elif  ParametersAlgo.OBS_MODEL == 'GMM':  
                if ParametersAlgo.FOR_JINGJU:
                    PATH_TO_CONFIG_FEATURES = projDir + '/models_makam/input_files/wav_config_singing_yile' # no singal amplitude normalization
    
                elif ParametersAlgo.FOR_MAKAM:
                    PATH_TO_CONFIG_FEATURES = projDir + '/models_makam/input_files/wav_config_singing_makam'
                
            
            HCopyCommand = [self.path_to_hcopy, '-A', '-D', '-T', '1', '-C', PATH_TO_CONFIG_FEATURES, URIRecordingChunk, mfcFileName]
    
            if not os.path.isfile(mfcFileName):
                logging.info(" Extract mfcc with htk command: {}".format( subprocess.list2cmdline(HCopyCommand) ) )
                pipe= subprocess.Popen(HCopyCommand)
                pipe.wait()
            
            return mfcFileName
        
    
def extractPredominantPitch( URI_recording_noExt,  frameSize=None, hopSize=None, jointAnalysis=False, musicbrainzid=None, preload=False):
        '''
        extract pitch using local version of pycompmusic and save as csv as input 
        used as inpu to  note segmentation algo
        preploaded joint analysis has hopsize=256 
        '''
        logging.debug( 'extracting pitch for {}...'.format(URI_recording_noExt))

        extractedPitchList = []
        ####### melodia format
        
        
        URI_recording = URI_recording_noExt + '.wav'
        
        if preload and musicbrainzid != None: ############# load from extractor output on server
    
            try:
                if jointAnalysis:
                    pitch_data = dunya.docserver.get_document_as_json(musicbrainzid, "jointanalysis", "pitch", 1, version="0.1")
                else:
                    pitch_data = dunya.docserver.get_document_as_json(musicbrainzid, "audioanalysis", "pitch_filtered", 1, version="0.1")
                extractedPitchList = pitch_data['pitch']
            except:
                logging.error("no initialmakampitch series could be downloaded. for rec ID  {}".format(musicbrainzid))
        elif not os.path.exists(URI_recording):
            logging.error('The file {} does not exist, nor is Music Brainz ID provided. No pitch extracted  '.format(URI_recording))
        else:
            ########## EXTRACT NOW. dont know how to extract with joint analysis
            logging.warning('extracting predominat pitch contour with audio analysis...')
            if hopSize != None and frameSize!= None:
                extractor = PredominantMelodyMakam(hop_size=hopSize, frame_size=frameSize)
            else:
                extractor = PredominantMelodyMakam()
            results = extractor.run(URI_recording)
            extractedPitchList = results['pitch']
            extractedPitchList = np.array(extractedPitchList)
    


        
        
        return extractedPitchList
