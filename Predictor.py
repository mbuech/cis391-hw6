import time
import glob
import random


class Predictor:
    '''
    Predictor which will do prediction on emails
    '''
    def __init__(self, spamFolder, hamFolder):
        self.__createdAt = time.strftime("%d %b %H:%M:%S", time.gmtime())
        self.__spamFolder = spamFolder
        self.__hamFolder = hamFolder
        # do training on spam and ham
        self.__train__()

    def __train__(self):
        '''train model on spam and ham'''
        # the following code is only an naive example,
        # implement your own training methond here
        spamCount = len(glob.glob(self.__spamFolder+'/*'))
        hamCount = len(glob.glob(self.__hamFolder+'/*'))
        self.__spamFrequency = 1.0*spamCount/(spamCount+hamCount)

    def predict(self, filename):
        '''Take in a filename, return whether this file is spam
        return value:
        True - filename is spam
        False - filename is not spam (is ham)
        '''
        # do prediction on filename
        if random.random() <= self.__spamFrequency:
            return True
        else:
            return False
