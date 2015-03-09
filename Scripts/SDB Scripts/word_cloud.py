# -*- coding: utf-8 -*-
"""
Created on Sun Oct  5 09:08:33 2014

@author: Lanfear

"""

import re
import matplotlib.pyplot as plt

from wordcloud import WordCloud


baseURL = '/Users/Lanfear/Desktop/Research/CLuuData/Results/'
top = baseURL + '100T1990-2000/'
bot = baseURL + '100B1990-2000/'


def main():
    f = open(bot + 'Components.txt', 'r')
    wordList = []
    for line in f:
        if line.startswith('START') or line.startswith('Genre') or\
                line.startswith('/-'):
            continue

        if line.rstrip() is not '':
            wordList.append(tuple(re.split('\s+', line.rstrip())))
    f.close()
    f = open('100B1990-2000wc.txt', 'w')
    for w in wordList:
        k = int(round(float(w[1]), 0))
        if k < 0:
            continue
        wl = [w[0]] * k
        for word in wl:
            f.write(word + ' ')
    f.close()

    text = open('100B1990-2000wc.txt', 'r').read()
    wordcloud = WordCloud().generate(text)
    # Open a plot of the generated image.
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.show()

if __name__ == '__main__':
    main()
