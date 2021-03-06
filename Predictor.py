import time
import glob
import random

import math
import os
import sys
import re
import pickle
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
                body += str(part.get_payload())
        else:
                body += str(email_dict.get_payload())
        relevant_headers = ['To', 'From', 'Subject']
        d = {}
        for h in relevant_headers:
            key = h + "*" + str(email_dict[h])
            if key in d:
                d[key] +=1
            else:
                d[key] = 1
        s = body
        return d, s

    def tokenize_links(self, text):
        new_text = self.tokenize(text)
        d = []
        for w in new_text:
            w = w.lower()
            if w not in d:
                if 'www' in w or 'http' in w:
                    d.append(w)
        return d

    def tokenize_cash(self, text):
        new_text = self.tokenize(text)
        d = []
        for w in new_text:
            w = w.lower()
            if w not in d:
                if '$' in w or '%' in w:
                    d.append(w)
        return d

    def tokenize_uppercase(self, text):
        new_text = self.tokenize(text)
        d = []
        for w in new_text:
            if w.upper() == w:
                d.append(w)
        return d

    def tokenize_html(self, text):
        new_text = self.tokenize(text)
        d = []
        x = 0
        while x < len(new_text):
            if new_text[x] == "<" and new_text[x+2] == ">":
                d.append(new_text[x+1])
            x += 1
        return d

    def tokenize_bigrams(self, text):
        new_text = self.tokenize(text)
        d = []
        x = 0
        while x < len(new_text) - 1:
            d.append(new_text[x].lower() + " " + new_text[x+1].lower())
            x += 1
        return d

class Predictor:
    '''
    Predictor which will do prediction on emails
    '''
    def __init__(self, spamFolder, hamFolder):
        self.__createdAt = time.strftime("%d %b %H:%M:%S", time.gmtime())
        self.__spamFolder = spamFolder
        self.__hamFolder = hamFolder
        self.__classes = {spamFolder: None, hamFolder: None}
        # do training on spam and ham
        self.__train__()

    # probability
    def __train__(self):
        '''train model on spam and ham'''
        # Set up the vocabulary for all files in the training set
        vocab = defaultdict(int)
        for dir in self.__classes:
            vocab.update(self.files2countdict(glob.glob(dir+"/*")))
        # Set all counts to 0
        vocab = defaultdict(int, zip(vocab.iterkeys(), [0 for i in vocab.values()]))

        for dir in self.__classes:
             # Initialize to zero counts
            countdict = defaultdict(int, vocab)
            # Add in counts from this class
            countdict.update(self.files2countdict(glob.glob(dir+"/*")))
            #***
            # Here turn the "countdict" dictionary of word counts into
            # into a dictionary of smoothed word probabilities
            #**
            num_words = 0
            for key in countdict:
                num_words += countdict[key]
            unique_labels = float(len(countdict.keys()))
            m = 1000.0
            for key, value in countdict.iteritems():
                #word count
                countdict[key] = (float(value) + (1.0/m)) / \
                    ((unique_labels/m))
            print len(countdict.keys())
            self.__classes[dir] = countdict

    def predict(self, filename):
        '''Take in a filename, return whether this file is spam
        return value:
        True - filename is spam
        False - filename is not spam (is ham)
        '''
        answers = []
        #print 'Classifying', filename
        # do prediction on filename
        for c in self.__classes:
            score = 0.0
            training_dic = self.__classes[c]
            test_vocab = defaultdict(int)
            test_vocab.update(self.files2countdict([filename]))
            for word in test_vocab:
                word = word.lower()
                if word in training_dic:
                    score += math.log(training_dic[word])
            answers.append((score, c))
        answers.sort()
        if answers[1][1] == self.__spamFolder:
            fout.write("Spam" + "\n")
            return True
        else:
            fout.write("Ham" + "\n")
            return False

    def files2countdict(self, files):
        """Given an array of filenames, return a dictionary with keys
        being the space-separated, lower-cased words, and the values being
        the number of times that word occurred in the files."""
        d = defaultdict(int)
        directory = {}
        directory['number_uppercase'] = 0
        directory['number_links'] = 0
        directory['number_cash'] = 0
        directory['num_html_tags'] = 0
        for file in files:
            file_string = open(file).read()
            tree = TreebankWordTokenizer()
            header, s = tree.strip_email_header(file_string)
            all_words = tree.tokenize(s)
            links = tree.tokenize_links(s)
            cash = tree.tokenize_cash(s)
            bigrams = tree.tokenize_bigrams(s)
            uppercase = tree.tokenize_uppercase(s)
            html_tags = tree.tokenize_html(s)
            directory['num_html_tags'] += len(html_tags)
            directory['number_uppercase'] += len(uppercase)
            directory['number_links'] += len(links)
            directory['number_cash'] += len(cash)
            for b in bigrams:
                b = b.lower()
                if b in directory:
                    directory[b] += 1
                else:
                    directory[b] = 1

            for word in all_words:
                word = word.lower()
                if word in directory:
                    directory[word] += 1
                else:
                    directory[word] = 1

            directory.update(header)
        return directory

if __name__ == '__main__':
    print 'argv', sys.argv
    print "Usage:", sys.argv[0], "classdir1 classdir2 [classdir3...] testdir1"
    fout = open("results.txt", "w")
    dirs = sys.argv[1:4]
    predictor = Predictor(dirs[0], dirs[1])
    spam_count, ham_count = 0, 0
    for testfile in os.listdir(dirs[-1]):
        filename = dirs[-1] + testfile
        result = predictor.predict(filename)
        if result:
            spam_count += 1
        else:
            ham_count += 1
    print spam_count, ham_count
    fout.close()
