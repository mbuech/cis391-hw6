import sys
import os
import glob
import pickle

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'Usage:', sys.argv[0], 'pickleFile, testFileOrFolder'
    else:
        if os.path.isfile(sys.argv[1]):
            # load pickle
            predictor = pickle.load(open(sys.argv[1], 'r'))
            if os.path.isdir(sys.argv[2]):
                # predict all files in folder
                for f in glob.glob(sys.argv[2]+'/*'):
                    print f, 'is', predictor.predict(f)
            elif os.path.isfile(sys.argv[2]):
                # predict this file
                print sys.argv[2], 'is', predictor.predict(sys.argv[2])
            else:
                print 'test file illegal'
        else:
            print 'pickle file illegal'
