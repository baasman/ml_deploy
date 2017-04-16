import numpy as np


def read_data(file, skip_header, delimiter):
    print(skip_header)
    return np.genfromtxt(file, skip_header=skip_header, delimiter=delimiter)
