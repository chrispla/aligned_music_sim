import os
import numpy as np
from librosa import time_to_frames

def ref_paths(lab_dir, audio_dir):
    """
    Return dictionary cross-referencing audio path with annotation path
    e.g. querry audio path to get annotation path and vice versa
    """
    
    # get anotation paths
    lab_paths = read_paths(lab_dir, '.lab')
    
    # traverse audio paths
    audio_paths = read_paths(audio_dir, '.flac')

    ref = {}
    # find maching paths
    for audio in audio_paths:
        for lab in lab_paths:
            flag = 0 #flag for entries with no match
            if os.path.basename(audio)[4:-5] in lab:
                ref[os.path.basename(audio)] = lab
                ref[lab] = os.path.basename(audio)
                flag = 1
                break
        if flag == 0:
            print("No match for:", os.path.basename(audio))
        
    return ref

def read_paths(filedir, file_extension):

    paths = []
    for root, dir, files in os.walk(filedir):
        for name in files:
            if file_extension in name:
                paths.append(os.path.join(root, name))

    return paths

def load_lab(dirs):

    lab_data = {}
    for lab in dirs:

        with open(lab, "r") as f:
            data = []
            while True:

                line = f.readline()
                if not line: #if EOF
                    break

                line = line.split()

                # convert start and end time string to float
                line[0] = float(line[0])
                line[1] = float(line[1])

                # merge labels
                if 'silence' in line[2]:
                    line[2] = 'silence'
                elif 'intro' in line[2]:
                    line[2] = 'intro'
                elif 'verse' in line[2]:
                    line[2] = 'verse'
                elif 'refrain' in line[2]:
                    line[2] = 'refrain'
                elif 'instrumental' in line[2]:
                    line[2] = 'instrumental'
                elif ('bridge' in line[2]) or ('birdge' in line[2]):
                    line[2] = 'bridge'
                elif 'outro' in line[2]:
                    line[2] = 'outro'
                elif 'break' in line[2]:
                    line[2] = 'break'
                elif 'build' in line[2]:
                    line[2] = 'build'
                elif 'ad-lib' in line[2]:
                    line[2] = 'ad-lib'
                elif 'middle' in line[2]:
                    line[2] = 'middle'
                else:
                    line[2] = 'OTHER'

                data.append(line)

        lab_data[os.path.basename(lab)[:-4]] = data
    
    return lab_data

def vectorize(lab, sr, start_f, end_f):
    """
    lab: formatted lab data ([start, end, label])
    sr: sampling rate
    start_f: desired starting frame
    end_f: desired ending frame (can be larger than total frames, in which case zero-paddin is done)

    Returns vector of labels at each frame for the desired frame interval
    """

    #create empty array with length given by max value in annotations file
    len_f = time_to_frames(lab[-1][1], sr=sr, hop_length=1) #get length in frames
    v = np.empty((len_f), dtype=object) #None entries

    #for every segment
    for seg in lab:

        #get segment data
        seg_start_f = time_to_frames(seg[0], sr=sr, hop_length=1)
        seg_end_f = time_to_frames(seg[1], sr=sr, hop_length=1)
        label = seg[2]

        #for every frame within that segment
        for i in range(seg_end_f-seg_start_f):
            #insert label
            v[seg_start_f+i] = label

    print("None values at:", np.argwhere(v==None))

    #if frame interval larger than song
    """note: this assumes that if you're padding you're doing it 
    on the entire audio file, so start_f = 0"""
    if end_f > len_f:
        v_pad = np.empty((end_f), dtype=object)
        v_pad[:len_f] = v
        return v_pad

    #if equal or smaller
    else:
        v_trunc = v[start_f:end_f]
        return v_trunc