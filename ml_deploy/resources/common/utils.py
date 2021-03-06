import numpy as np


def read_data(file, skip_header, delimiter):
    '''Will read data from disk'''
    return np.genfromtxt(file, skip_header=skip_header, delimiter=delimiter)
