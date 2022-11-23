import pandas as pd
import numpy as np


clues = pd.read_csv('clues.csv')
all_words = {}

#clean data and add to dictionary
# for i in range(len(clues)):

clues = clues.dropna()
for index, row in clues.iterrows():
  # if (not (row['clue']).isna() and not row['answer'].isna()):
  # if row['clue']
  all_words[row['answer']] = row['clue']

# print(clues_dict)
  

# get user input
size = int(input("What size would you like the crossword to be? Please pick a number between 6 and 20: "))
while size > 20 or size < 4:
  size = int(input("This size is out of bounds. What size would you like the crossword to be? Please pick a number between 6 and 20: "))

# remove words longer than size of puzzle and remove 1 and 2-letter words
clues_dict = {}
for word in all_words.keys():
  if len(word) <= size:
    if(not len(word) <= 2):
      clues_dict[word] = all_words[word]

# ranking words based off number of intersections with all other words
ranked_words = []
for word1 in clues_dict.keys():
  #count = number of intersections between a word and all other words
  count = 0
  for word2 in clues_dict.keys():
    if(not(word1 == word2)):
      for l in word1:
        if l in word2:
          count +=1
  ranked_words.append((count, word1))

# sort ranked words (in order of descending number of interesections)
ranked_words = sorted(ranked_words, key=lambda x: x[0], reverse=True)    
# print(ranked_words)


# create grid to match inputted size
grid = []
for i in range(size):
  g = []
  for j in range(size):
    g.append(' ')
  grid.append(g)

def pretty_print(g):
  for row in g:
    print(row)

def generate_puzzle_highest_ranked_first():
  # placing first word
  first_word = ranked_words[0][1]
  x = size//2 - len(first_word)//2
  y = size//2
  for letter in first_word:
    grid[y][x] = letter
    x += 1
  pretty_print(grid)
  
generate_puzzle_highest_ranked_first()
