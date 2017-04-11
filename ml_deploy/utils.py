from klepto.archives import file_archive
import numpy as np


def load_archive(archive):
    arch = file_archive(archive)
    arch.load()
    print(arch.keys())
    if 'ml_model' in arch.keys():
        return arch
    else:
        return {'error': 'No model found'}


def read_data(file, skip_header, delimiter):
    print(skip_header)
    return np.genfromtxt(file, skip_header=skip_header, delimiter=delimiter)


if __name__ == '__main__':
    d = read_data('xd.csv')
    print(d)
