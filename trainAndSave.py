import sys
import os
import pickle
from Predictor import Predictor

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'Usage:', sys.argv[0], 'spamFolder, hamFolder'
    else:
        if os.path.isdir(sys.argv[1]) and os.path.isdir(sys.argv[2]):
            print 'training...'
            predictor = Predictor(sys.argv[1], sys.argv[2])
            print predictor.predict('bla')
            # save to pickle
            print 'saving predictor to pickle'
            pickle.dump(predictor, open('predictor.pickle', 'w'))
        else:
            print 'training folders illegal'
