import os

def ref_paths(lab_dir, audio_dir):
    """
    Return dictionary cross-referencing audio path with annotation path
    e.g. querry audio path to get annotation path and vice versa
    """
    
    # traverse anotation paths
    lab_paths = []
    for root, dir, files in os.walk(lab_dir):
        for name in files:
            if '.lab' in name:
                lab_paths.append(os.path.join(root, name))
    
    # traverse audio paths
    audio_names_paths = []
    for root, dir, files in os.walk(audio_dir):
        for name in files:
            if '.flac' in name:
                audio_names_paths.append([name[4:-5], os.path.join(root, name)]) # parsed name & path

    ref = {}
    # find maching paths
    for audio in audio_names_paths:
        for lab in lab_paths:
            flag = 0 #flag for entries with no match
            if audio[0] in lab:
                ref[audio[1]] = lab
                ref[lab] = audio[1]
                flag = 1
                break
        if flag == 0:
            print("No match for:", audio[0])
        
    return ref

