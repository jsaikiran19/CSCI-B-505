#!/usr/bin/python
#
# Perform optical character recognition, usage:
#     python3 ./image2text.py train-image-file.png train-text.txt test-image-file.png
# 
# Authors: (insert names here)
# (based on skeleton code by D. Crandall, Oct 2020)
#

from PIL import Image, ImageDraw, ImageFont
import sys
from collections import Counter
import numpy as np
import math


CHARACTER_WIDTH=14
CHARACTER_HEIGHT=25
TRAIN_LETTERS="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789(),.-!?\"' "
len_states = len(TRAIN_LETTERS)


def load_letters(fname):
    im = Image.open(fname)
    px = im.load()
    (x_size, y_size) = im.size
    print(im.size)
    print(int(x_size / CHARACTER_WIDTH) * CHARACTER_WIDTH)
    result = []
    for x_beg in range(0, int(x_size / CHARACTER_WIDTH) * CHARACTER_WIDTH, CHARACTER_WIDTH):
        result += [ [ "".join([ '*' if px[x, y] < 1 else ' ' for x in range(x_beg, x_beg+CHARACTER_WIDTH) ]) for y in range(0, CHARACTER_HEIGHT) ], ]
    return result

def load_training_letters(fname):
    letter_images = load_letters(fname)
    return { TRAIN_LETTERS[i]: letter_images[i] for i in range(0, len_states ) }

#####
# main program
if len(sys.argv) != 4:
    raise Exception("Usage: python3 ./image2text.py train-image-file.png train-text.txt test-image-file.png")

(train_img_fname, train_txt_fname, test_img_fname) = sys.argv[1:]
train_letters = load_training_letters(train_img_fname)
test_letters = load_letters(test_img_fname)


#######################################################################################

## Below is just some sample code to show you how the functions above work. 
# You can delete this and put your own code here!


# Each training letter is now stored as a list of characters, where black
#  dots are represented by *'s and white dots are spaces. For example,
#  here's what "a" looks like:
# print("\n".join([ r for r in train_letters['a'] ]))

# Same with test letters. Here's what the third letter of the test data
#  looks like:
# print("\n".join([ r for r in test_letters[2] ]))

#######################################################################################

def calculate_init_trans(words_file_name):
    training_words = open(words_file_name, 'r')

    init_prob = Counter()
    trans_prob = np.zeros(shape=(len_states, len_states))
    words = []
    letters = ''

    for line in training_words.readlines():
        for word in line.split():
            words.append(word)
            for letter in TRAIN_LETTERS:
                if word[0] == letter:
                    init_prob.update(letter)
        letters += line

    training_words.close()
    
    total_words = len(words)
    for key in init_prob:
        init_prob[key] = math.log(init_prob[key]+1 / total_words+2)

    for i in range(len(letters)-1):
        if letters[i] in TRAIN_LETTERS and letters[i+1] in TRAIN_LETTERS:
            trans_prob[TRAIN_LETTERS.index(letters[i]), TRAIN_LETTERS.index(letters[i+1])] += 1

    for row in trans_prob:
        total = sum(row)
        if total > 0:
            row[:] = [math.log(r+1/total+2) for r in row]

    return init_prob, trans_prob


def calculate_emission():
    m = 0.35
    emission_prob = np.zeros(shape=(len_states, len_states))
    for key, value in train_letters.items():
        for j in range(len(test_letters)):
            hit = 0
            miss = 0
            letter = test_letters[j]
            for x in range(CHARACTER_WIDTH):
                for y in range(CHARACTER_HEIGHT):
                    if letter[y][x] == value[y][x]:
                        hit += 1
                    else:
                        miss += 1

            hit_prob = hit / (hit + miss)
            miss_prob = 1 - hit_prob

            prob = (hit_prob ** hit) * (miss_prob ** miss)

            i = TRAIN_LETTERS.index(key)
            emission_prob[i][j] = math.log(10**(-6)) if prob == 0 else math.log(prob)

    return emission_prob
                
def simple(letters, emission):
    N = len(letters)
    emission_mtx = np.zeros(shape=(len_states, N))
    
    for i in range(0, N):
        for j in range(0, len_states):
            emission_mtx[j,i] = emission[j,i]
    indices = np.argmax(emission_mtx, axis=0)
    output_str = ''
    for i in indices:
        output_str += TRAIN_LETTERS[i]
    return output_str

def hmm(letters, init_p, trans_p, emission_p):
    N = len(letters)

    v_table = np.zeros(shape=(len_states, N))
    which_table = np.empty(shape=(len_states, N), dtype=int)

    for i in range(len_states):
        v_table[i,0] = init_p[i] + emission_p[i,0]
    
    for i in range(1, N):
        for s in range(len_states):
            max_val = -math.inf
            max_index = -1
            for s0 in range(len_states):
                val = v_table[s0,i-1] + trans_p[s0,s]
                if val > max_val:
                    max_val = val
                    max_index = s0
            max_val += emission_p[s,i]
            v_table[s,i] = max_val
            which_table[s,i] = max_index

    most_likely = np.zeros(N, dtype=int)
    most_likely[-1] = np.argmax(v_table[:,-1])

    for i in range(1, N)[::-1]:
        most_likely[i-1] = which_table[most_likely[i], i]

    output_str = ''
    for i in most_likely:
        output_str += TRAIN_LETTERS[i]
    return output_str


#######################################################################################

init_prob, trans_prob = calculate_init_trans(train_txt_fname)
emission_prob = calculate_emission()

simple_result = simple(test_letters, emission_prob)
hmm_result = hmm(test_letters, init_prob, trans_prob, emission_prob)
# The final two lines of your output should look something like this:
print("Simple: " + simple_result)
print("   HMM: " + hmm_result)


