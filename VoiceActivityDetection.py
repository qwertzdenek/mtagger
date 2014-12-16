# coding=utf-8
import numpy as np

def simpleVAD(frames, sig, threshold=0.01):
    """
    :param frames: numpy array of [NumFrames][SamplesPerFrame] of all the speech frames
    :param sig: The entire signal [signLen]
    :param threshold: above what level of average power must the frame be to be considered to have activity
    :return: the subset of frames where there is voiced activity detected

    Note that the variance of frame/signal represents the average power of the frame/signal
    so this is a power threshold activity detector applied along the frames
    """

    frameVars = np.var(frames, 1)
    reducedFrames = frames[np.where(frameVars > sig.var() * threshold)]
    return reducedFrames

