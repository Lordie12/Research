import nltk
import os
import re
import string
import sys
from collections import Counter

folder = 'Parsed/'
totalwordcounts = Counter()

# This function takes in a film script and splits it into scenes. Each scene is written into a
# separate file in the ./Parsed/ folder.
def split_files(filename):
  f_read = open(filename, 'r')
  fname_split = filename.split('.')
  scene_num = 0
  # create the initial garbage file
  f_write = open(fname_split[0] + '_' + str(scene_num) + '.txt', 'w')

  for line in f_read:
    # a lot of scripts are in Latin-1 encoding
    # TODO not sure if they all are Latin-1, so this should be conditional
    line = line.lower().decode('iso-8859-1').encode('utf8')
    line_match = re.match(r"[0-9 \t]+(int.|ext.|fade in|int --|ext --)+", line.strip())
    # if reach ext/int, finish writing and open new file
    # not sure if this encompasses all variations of int/ext
    if (line.strip().startswith('ext.') or
        line.strip().startswith('int.') or
        line.strip().startswith('internal') or
        line.strip().startswith('external') or
        line.strip().startswith('fade in:') or
        line_match != None):
      # close the previous file
      f_write.close()
      scene_num += 1
      # open a new file
      f_write = open(folder + fname_split[0] + '_' + str(scene_num).rjust(3, '0') + '.txt', 'w')
      f_write.write(line)
      continue
    # if reach the end, stop
    if (line.strip().startswith('the end') or
        line.strip().startswith('fade out') or
        line.strip().startswith('fade to black')):
      break
    # only update the vocabulary if we're not at scene 0 (beginning garbage)
    if scene_num != 0:
      # remove punctuation and tokenize (TODO check if punctuation removal is correct)
      tokenized = nltk.word_tokenize(line.translate(None, string.punctuation))
      # remove (scene) numbers and single letter words
      tokenized = [w for w in tokenized if not w.isdigit() and len(w) > 1]
      # create counter dictionary from this scene and add to the total 
      totalwordcounts.update(Counter(tokenized))
    # write the line
    f_write.write(line)

  f_write.close()
  f_read.close()
  # returned for debugging purposes
  return totalwordcounts

# This function reads in the parsed scenes and writes their corresponding count matrices
# to ./Parsed/xtab.txt.
def write_xtab():
  xtab = open(folder + 'xtab.txt', 'w')
  # write totalwordcounts to xtab in descending value order
  for w in sorted(totalwordcounts, key=totalwordcounts.get, reverse=True):
    xtab.write(w + ' ')
  # for each txt file in parsed folder, write the vector
  for item in sorted(os.listdir(folder)): 
    if os.path.isfile(os.path.join(folder, item)): 
      fileName, fileExtension = os.path.splitext(item)
      # make sure we're only reading the scene files
      if fileExtension.lower() == '.txt' and not fileName == 'xtab':
        xtab.write('\n' + item + ' ')
        cur_read = open(os.path.join(folder, item), 'r')
        # skip the first line that has the ext/int setting
        cur_read.readline()
        # create a counter dictionary for just this scene
        tokenized = nltk.word_tokenize(cur_read.read().translate(None, string.punctuation))
        cur_words = Counter(tokenized)
        # write out all values as sparse matrix of counts
        for w in sorted(totalwordcounts, key=totalwordcounts.get, reverse=True):
          xtab.write(str(cur_words[w]) + ' ')
          
  xtab.write('\n')
  xtab.close()
  
def write_allwords():
  allwords = open(folder + 'allwords.txt', 'w')
  # write totalwordcounts to xtab in descending value order
  for w in sorted(totalwordcounts, key=totalwordcounts.get, reverse=True):
    allwords.write(w + ' ' + str(totalwordcounts[w]) + '\n')
  allwords.close()
    
def main(argv):
  if not len(argv) == 1:
    print 'Usage: python script_parser.py [filename]'
    return
  # if Parsed folder doesn't exist, create it
  if not os.path.exists(folder):
    os.makedirs(folder)
  split_files(argv[0])
  write_xtab()
  write_allwords()

if __name__ == '__main__':
  main(sys.argv[1:])
