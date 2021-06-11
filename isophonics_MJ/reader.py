import os

def ref_paths(lab_dir, audio_dir):
    """
    Return dictionary cross-referencing audio path with annotation path
    e.g. querry audio path to get annotation path and vice versa
    """
    
    # get anotation paths
    lab_paths = paths(lab_dir, '.lab')
    
    # traverse audio paths
    audio_paths = paths(audio_dir, '.flac')

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

def paths(filedir, file_extension):

    paths = []
    for root, dir, files in os.walk(filedir):
        for name in files:
            if file_extension in name:
                paths.append(os.path.join(root, name))

    return paths