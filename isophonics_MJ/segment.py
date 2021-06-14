#
# Code from https://librosa.org/librosa_gallery/auto_examples/plot_segmentation.html
#

import librosa
import numpy as np
import scipy
from scipy.spatial.distance import pdist, squareform
from scipy.sparse.csgraph import laplacian
from scipy.spatial.distance import directed_hausdorff
from scipy.linalg import eigh
from scipy.ndimage import median_filter
from sklearn.cluster import KMeans
import cv2

def segment(y, sr, kmin, kmax):
    """structurally segment audio

        [kmin, kmax]: min and maximum approximation ranks

    returns (segment_ids, [formatted_times, formatted_frames, formatted_beats]),"""

    #compute cqt
    C = librosa.amplitude_to_db(np.abs(librosa.cqt(y=y, sr=sr, 
                                        hop_length=512,
                                        bins_per_octave=12*3,
                                        n_bins=7*12*3)),
                                        ref=np.max)

    #beat tracking
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr, trim=False)
    beat_times = librosa.frames_to_time(librosa.util.fix_frames(beats, x_min=0, x_max=C.shape[1]), sr=sr)

    #beat synch cqt
    Csync = librosa.util.sync(C, beats, aggregate=np.median)

    #stack memory
    Csync = librosa.feature.stack_memory(Csync, 4)

    #Affinity matrix
    R = librosa.segment.recurrence_matrix(Csync, width=3, mode='affinity', sym=True)

    #Filtering
    df = librosa.segment.timelag_filter(scipy.ndimage.median_filter)
    R = df(R, size=(1, 7))
    R = librosa.segment.path_enhance(R, 15)

    #mfccs
    mfcc = librosa.feature.mfcc(y=y, sr=sr)

    #beat sync mfccs
    Msync = librosa.util.sync(mfcc, beats)

    #weighted sequence
    path_distance = np.sum(np.diff(Msync, axis=1)**2, axis=0)
    sigma = np.median(path_distance)
    path_sim = np.exp(-path_distance / sigma)
    R_path = np.diag(path_sim, k=1) + np.diag(path_sim, k=-1)

    #weighted combination of affinity matrix and mfcc diagonal
    deg_path = np.sum(R_path, axis=1)
    deg_rec = np.sum(R, axis=1)

    mu = deg_path.dot(deg_path + deg_rec) / np.sum((deg_path + deg_rec)**2)

    A = mu * R + (1 - mu) * R_path

    #resampling
    A_d = cv2.resize(A, (128, 128))

    #laplacian
    L = scipy.sparse.csgraph.laplacian(A_d, normed=True)

    #eigendecomposition
    evals, evecs = scipy.linalg.eigh(L)
    #eigenvector filtering
    evecs = scipy.ndimage.median_filter(evecs, size=(9, 1))

    #normalization
    Cnorm = np.cumsum(evecs**2, axis=1)**0.5

    #approximations
    all_seg_ids = []
    for k in range(kmin, kmax):
        seg_ids_set = []
        Xs = evecs[:, :k] / Cnorm[:, k-1:k]
        #debug
        if np.isnan(np.sum(Xs)):
            print('woops')
        KM = KMeans(n_clusters=k, n_init=50, max_iter=500)
        all_seg_ids.append(KM.fit_predict(Xs))
    
    #Formatting as [start position, length]
    formatted_beats = []
    formatted_times = []
    formatted_frames = []
    #traverse hierarchies
    for i in range(kmax-kmin):
        formatted_beats.append([])
        formatted_times.append([])
        formatted_frames.append([])
        # Locate segment boundaries from the label sequence
        bound_beats = 1 + np.flatnonzero(all_seg_ids[i][:-1] != all_seg_ids[i][1:])
        # Count beats 0 as a boundary
        bound_beats = librosa.util.fix_frames(bound_beats, x_min=0)
        
        # Convert beat indices to frames
        bound_times = beat_times[bound_beats]
        # Tack on the end-time
        bound_times = list(np.append(bound_times, beat_times[-1]))

        # format as [beat_start_position, segment_length_in_beats]
        beat_poslen = []
        # format as [time_start_position, segment_length_in_time]
        time_poslen = []

        #traverse beats
        for idx in range(len(bound_beats)-1):
            beat_poslen.append([ bound_beats[idx], bound_beats[idx+1]-bound_beats[idx] ])
            time_poslen.append([ bound_times[idx], bound_times[idx+1]-bound_times[idx] ])

        formatted_beats[i] = beat_poslen
        formatted_times[i] = time_poslen
        formatted_frames[i] = librosa.time_to_frames(time_poslen,hop_length=1)

    #return
    return((np.asarray(all_seg_ids), [formatted_times, formatted_frames, formatted_beats]))