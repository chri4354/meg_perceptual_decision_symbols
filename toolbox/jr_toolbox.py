class struct(list):
    """Mimmic indexable matlab structure

    Parameters
    ----------
    dicts : list
        list of dictionaries. All keys must match

    Functions
    ---------
    get(str) : get all instances with key str
    get(int) : get all keys in instance int
    keys() : get keys
    shape() : get number of instances
    matrix : get np.array n_instance x n_key unique code
    """

    def __init__(self, dicts):
        self.dicts = dicts
        self._check()

    def _check(self):
        keys = self.keys()
        n = self.shape()
        for key in keys:
            if len(self.get(key)) != n:
                raise('%s does not have all instances')

    def get(self, key):
        import numpy as np
        if type(key) == str:
            out = np.array([x[key] for x in self.dicts])
        elif type(key) == int:
            out = self.dicts[key]
        return out

    def keys(self):
        return self.dicts[0].keys()

    def shape(self):
        return len(self.dicts)

    def matrix(self, keys=None):
        """Return numerical array with all values
        Parameters
        ----------
        keys : str | list
            Selected keys
        Returns
        -------
        matrix : np.array(n_instance, n_keys)
            Array containing all values"""
        from sklearn.preprocessing import LabelEncoder
        import numpy as np

        if keys is None:
            keys = self.keys()
        elif type(keys) == str:
            keys = [keys]
        for key in keys:
            column = self.get(key)
            try:
                column = [float(ii) for ii in column]
            except:
                le = LabelEncoder()
                column = le.fit_transform(column)
            if 'matrix' in locals():
                matrix = np.vstack((matrix, column))
            else:
                matrix = column
        return matrix.transpose()

    def __repr__(self):
        s = ('<Struct | n = %i, keys = ' % len(self.dicts) +
             str(self.dicts[0].keys()) + '>')
        return s
