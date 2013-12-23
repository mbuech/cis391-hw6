import time
import glob
import random

import math
import os
import sys
import re
import pickle
import nltk
from collections import defaultdict
from email.parser import Parser

class TreebankWordTokenizer():
    # List of contractions adapted from Robert MacIntyre's tokenizer.
    CONTRACTIONS2 = [re.compile(r"(?i)(.)('ll|'re|'ve|n't|'s|'m|'d)\b"),
                     re.compile(r"(?i)\b(can)(not)\b"),
                     re.compile(r"(?i)\b(D)('ye)\b"),
                     re.compile(r"(?i)\b(Gim)(me)\b"),
                     re.compile(r"(?i)\b(Gon)(na)\b"),
                     re.compile(r"(?i)\b(Got)(ta)\b"),
                     re.compile(r"(?i)\b(Lem)(me)\b"),
                     re.compile(r"(?i)\b(Mor)('n)\b"),
                     re.compile(r"(?i)\b(T)(is)\b"),
                     re.compile(r"(?i)\b(T)(was)\b"),
                     re.compile(r"(?i)\b(Wan)(na)\b")]
    CONTRACTIONS3 = [re.compile(r"(?i)\b(Whad)(dd)(ya)\b"),
                     re.compile(r"(?i)\b(Wha)(t)(cha)\b")]

    def tokenize(self, text):
        for regexp in self.CONTRACTIONS2:
            text = regexp.sub(r'\1 \2', text)
        for regexp in self.CONTRACTIONS3:
            text = regexp.sub(r'\1 \2 \3', text)

        # Separate most punctuation
        text = re.sub(r"([^\w\.\'\-\/,&])", r' \1 ', text)

        # Separate commas if they're followed by space.
        # (E.g., don't separate 2,500)
        text = re.sub(r"(,\s)", r' \1', text)

        # Separate single quotes if they're followed by a space.
        text = re.sub(r"('\s)", r' \1', text)

        # Separate periods that come before newline or end of string.
        text = re.sub('\. *(\n|$)', ' . ', text)

        return text.split()

    def strip_email_header(self, filestring):
        email_dict = Parser().parsestr(filestring)
        body = ''
        if email_dict.is_multipart():
            for part in email_dict.get_payload():
                body += part.get_payload()
        else:
                body += email_dict.get_payload()
        relevant_headers = ['To', 'From', 'Subject']
        for h in relevant_headers: d[h + "*" + header[h]]['total']+=1
        s = email_body
        s = re.sub('\d[.,]\d')
        s = re.sub('([.,;!?()])', r' \1 ', s)
        s = re.sub('\s{2,}', ' ', s)
        return s

    def tokenize_links(self, text):
        new_text = self.tokenize(text)
        d = []
        for w in new_text:
            w = w.lower()
            if w not in d:
                if 'www' in w or 'http' in w:
                    d.append(w)

    def tokenize_uppercase(self, text):
        new_text = self.tokenize(text)
        d = []
        for w in new_text:
            if w.upper() == word:
                d.append(w)
        return d


class Predictor:
    '''
    Predictor which will do prediction on emails
    '''
    def __init__(self, spamFolder, hamFolder):
        self.__createdAt = time.strftime("%d %b %H:%M:%S", time.gmtime())
        self.__spamFolder = spamFolder
        self.__hamFolder = hamFolder
        self.__classes = [spamFolder: None, hamFolder: None]
        # do training on spam and ham
        self.__train__()

    def __train__(self):
        '''train model on spam and ham'''
        # Set up the vocabulary for all files in the training set
        vocab = defaultdict(int)
        for dir in self.__classes:
            vocab.update(files2countdict(glob.glob(dir+"/*")))
        # Set all counts to 0
        vocab = defaultdict(int, zip(vocab.iterkeys(), [0 for i in vocab.values()]))

        for dir in self.__classes:
             # Initialize to zero counts
            countdict = defaultdict(int, vocab)
            # Add in counts from this class
            countdict.update(files2countdict(glob.glob(dir+"/*")))
            #***
            # Here turn the "countdict" dictionary of word counts into
            # into a dictionary of smoothed word probabilities
            #**
            num_words = 0
            num_uppercase = 0
            for key in countdict:
                num_words += countdict[key]['count']
                num_uppercase += countdict[key]['upper']
            unique_labels = float(len(countdict.keys()))
            for key, value in countdict.iteritems():
            #capitalization
            countdict[key]['upper'] = (float(value['upper']) + 1.0) / \
                (num_uppercase + unique_labels)
            #word count
            countdict[key]['count'] = (float(value['count']) + 1.0) / \
                (num_words + unique_labels)
        self.__classes[dir] = countdict

    def predict(self, filename):
        '''Take in a filename, return whether this file is spam
        return value:
        True - filename is spam
        False - filename is not spam (is ham)
        '''
        answers = []
        print 'Classifying', filename
        # do prediction on filename
        for c in self.__classes:
            score = 0.0
            training_dic = self.__classes[c]
            #look at each word in the input (test) file
            answer.append((score, c))
        answers.sort()
        if answers[1][1] == self.__spamFolder:
            return True
        else:
            return False

    def files2countdict (files):
    """Given an array of filenames, return a dictionary with keys
    being the space-separated, lower-cased words, and the values being
    the number of times that word occurred in the files."""
    d = defaultdict(int)
    for file in files:
        file_string = open(file).read()
        email_dic = strip_email(file_string)
        #todo: tokenize using clara's method
        #((\d*[\,.]\d*)+)
        for word in nltk.word_tokenize(file_string):
            #urls
            if 'www' in word.lower() or 'http' in word.lower():
                if d['(www)'] != None:
                    d['(www)']['count'] += 1
                else:
                    d['(www)']['count'] = 1
            #capitalization
            if word = word.upper():
                if d[word.lower()]['upper'] != None:
                    d[word.lower()]['upper'] += 1
                else:
                    d[word.lower()]['upper'] = 1
            #word count
            if d[word.lower()] != None:
                d[word.lower()]['count'] += 1
            else:
                d[word.lower()]['count'] = 1
    return d

if __name__ == '__main__':
    print 'argv', sys.argv
    print "Usage:", sys.argv[0], "classdir1 classdir2 [classdir3...] testdir1"
    dirs = sys.argv[1:3]
    predictor = Predictor(dirs[0], dirs[1])
    ham_count, spam_count = 0, 0
    for testfile in os.listdir(dirs[-1]):
        result = predictor.predict(testfile)
        if result:
            spam_count += 1
        else:
            ham_count += 1
    print spam_count, ham_count
