import pickle
from klepto.archives import file_archive
import os
import sklearn


class BaseModel(object):
    def __init__(self, classifier, name=None, model_archive=None, model_dir=None):
        self.name = name
        self.model_archive = model_archive
        self.classifier = classifier
        self.model_dir = model_dir
        self._persist_mod()

    def _persist_mod(self):
        try:
            mod_dump = pickle.dumps(self.classifier)
            if self.model_archive is None:
                if self.model_dir is None:
                    self.model_dir = os.path.dirname(os.path.abspath(__file__))

                if not os.path.isdir(self.model_dir):
                    os.makedirs(self.model_dir)

                arch_name = 'model_arch-%s.pkl' % self.name
                print(os.path.join(self.model_dir, arch_name))
                self.model_archive = file_archive(os.path.join(self.model_dir, arch_name))
            else:
                pass
            self.model_archive['ml_model'] = mod_dump
        except Exception as e:
            print(str(e))

    def save(self):
        assert self.model_archive is not None
        self.model_archive.dump()


class SKLearnModel(BaseModel):

    def __init__(self, classifier, data=None, col_list=None, *args, **kwargs):
        super(SKLearnModel, self).__init__(classifier, *args, **kwargs)
        self._get_model_attributes()
        if data is not None:
            self._get_column_info(data)
            self._get_data_shape(data)
        self._get_version()
        self.model_archive['source'] = 'sklearn'

    def __str__(self):
        return ", ".join(['%s: %s' % (i, j) for i, j in
                         self.model_archive.get('model_attributes').items()])

    def _get_model_attributes(self):
        assert self.classifier is not None
        self.model_archive['model_attributes'] = self.classifier.get_params()

    def _get_column_info(self, data, col_list=None):
        if isinstance(X, pd.DataFrame):
            columns_types = []
            for i in self.data.columns:
                columns_types[i] = data[i].dtype
            self.model_archive['column_types'] = columns_types
        elif col_list is not None:
            self.model_archive['columns'] = col_list
        else:
            print('It is recommended to provide a list of columns')

    def _get_data_shape(self, data):
        self.model_archive['data_shape'] = data.shape

    def _get_version(self):
        try:
            self.model_archive['package_version'] = sklearn.__version__
        except:
            pass



if __name__ == '__main__':
    from sklearn import svm, datasets
    import pandas as pd
    clf = svm.SVC()
    iris = datasets.load_iris()
    X, y = iris.data, iris.target
    clf.fit(X, y)
    mod = SKLearnModel(classifier=clf, name='testmod', data=X,
                       model_dir='/Users/baasman/Documents/python-workspace/ml_deploy/models/')
    mod.save()
