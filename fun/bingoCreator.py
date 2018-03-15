#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bingo creator version 0.2
Jens Dede, mail@jdede.de

Bingo is a famous game - especially for (boring) meetings. Collect some typical
words wich are used in (more or less) every meeting. Place them in a textfile
(one word per line) and start this script. It will create several
game sheets.

You will have a lot of fun during the next meeting!

CHANGELOG:
    * 0.2   Migrated to Python 3
    * 0.1   Initial version

TODO:
    * --
"""

import random
import sys
import copy
import argparse
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

parser = argparse.ArgumentParser(description='Create a bingo sheet')
parser.add_argument('wordfile', help='The wordfile. One word per line. Lines starting with a hash (#) will be ignored')
parser.add_argument('--title', '-t', dest='title', default=None, help='Set a title printed on top of the sheet')
parser.add_argument('--prefix', '-p', dest='prefix', default='bingo-', help='Set a prefix for the generated output files. Default: "bingo-"')
parser.add_argument('--number', '-n', dest='numberFiles', default=5, type=int, help='Number of created sheets. Default: 5')
parser.add_argument('--rows', '-r', dest='rows', default=5, type=int, help='Number of rows')
parser.add_argument('--columns', '-c', dest='columns', default=5, type=int, help='Number of columns')
args = parser.parse_args()

# Read in words from file. One word - one line
wordlist = []
f = open(args.wordfile);
for line in f:
    l = line[:-1];
    # Ignore lines starting with a hash
    if l[0] == '#':
        continue
    wordlist.append(l)
f.close()


# Check if we have enough words for the requested structure
if len(wordlist) < (args.rows*args.columns):
    print("Not enough elements to create bingo. Exiting")
    sys.exit(0)
# Okay, lets start generating some independent games
for loop in range(args.numberFiles):
    wordlistLoop = copy.copy(wordlist)
    # Randomize elements and limit to requested number of elements
    randomElements = []
    for i in range(args.rows*args.columns):
        element = int(random.uniform(0, len(wordlistLoop)))
        randomElements.append(wordlistLoop[element])
        del wordlistLoop[element]

    # Create matrix of random words
    outputStructure = []
    for row in range(0, args.rows):
        outputStructure.append(randomElements[row*args.columns:row*args.columns+args.columns])

    # Create PDF

    # 11.696 inches =^= 297 mm, 8.268 inches =^= 210 mm --> DIN A4
    fig = plt.figure(figsize=(11.693, 8.268))
    ax = fig.add_subplot(111)
    # Use only integer values for grid and disable axis labels
    ax.xaxis.set_major_locator(ticker.MultipleLocator(base=1))
    ax.xaxis.set_major_formatter(ticker.NullFormatter())
    ax.yaxis.set_major_locator(ticker.MultipleLocator(base=1))
    ax.yaxis.set_major_formatter(ticker.NullFormatter())

    if args.title:
        plt.title(args.title)

    plt.tight_layout()
    plt.axis([0, args.columns, 0, args.rows])
    plt.grid(linestyle='-', linewidth=2)

    # Print the data
    for r in range(args.rows):
        for c in range(args.columns):
            plt.text(c+.5, r+.5, outputStructure[r][c], ha='center', va='center')

    plt.savefig(args.prefix + str(loop+1) + ".pdf")

