import pandas as pd
import numpy as np


clues = pd.read_csv('clues.csv')
all_words = {}

# clean data and add to dictionary
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

# return number of intersection the rest of the words have with the current words in the puzzle
def numIntersections(current_words):
  ranked_words = []
  for word1 in clues_dict.keys():
    # count = number of intersections between current words in puzzle and all other words
    count = 0
    for word2 in current_words:
      if(not(word1 == word2)):
        for l in word1:
          if l in word2:
            count +=1
    
    if(count != 0):
      ranked_words.append((count, word1))

  if (ranked_words[0].count == 0):
    return None
    
  return ranked_words

# ranking words based off number of intersections with all other words
ranked_words = numIntersections(clues_dict.keys())

# sort ranked words (in order of descending number of interesections)
ranked_words = sorted(ranked_words, key=lambda x: x[0], reverse=True)  

# print(ranked_words)

# find which words a given word intersects with
def contains_intersection(w, current):
  intersection = set()
  for word in current:
    for letter in w:
      if letter in word:
        intersection.add(word)
  return intersection
  

def is_valid_intersection(is_horizontal, x_pos, y_pos, i, j, grid, word):
  if (is_horizontal):
    # find position of j in word on board / on grid
    x_pos_intersection = x_pos + i
    y_pos_intersection = y_pos
    # check if spot directly above and/or below letter are free

    # check spacing above the word
    for y in range(j+1):
      # invalid intersection (not enough spaces above word) 
      if y_pos_intersection - y < 0:
        return False
      if not ((grid[y_pos_intersection - y][x_pos] == ' ') or (grid[y_pos_intersection - y][x_pos] == word[j - y])):
        return False
    
    # check spacing below the word   
    for y in range(len(word) - j):
      # invalid intersection (not enough spaces below word)
      if y_pos_intersection + y >= len(grid):
        return False
      if not ((grid[y_pos_intersection + y][x_pos] == ' ') or (grid[y_pos_intersection + y][x_pos] == word[j + y])):
        return False
    
      # check below
      # place horizontally
  else:
    x_pos_intersection = x_pos
    y_pos_intersection = y_pos + i

    #check spacing to the left of word 
    for x in range(j+1):
      
      #invalid intersection (not enough spaces to the left of word)
      if x_pos_intersection - x < 0:
        return False
      if not((grid[y_pos][x_pos_intersection - x] == ' ') or (grid[y_pos][x_pos_intersection - x] == word[j - x])):
        return False
  
  #check spacing to the right of word
    for y in range(len(word) - j):

      #invalid intersection (not enough spaces to the right of word)
      if x_pos_intersection + x >= len(grid):
        return False
      if not((grid[y_pos][x_pos_intersection + x] == ' ') or (grid[y_pos][x_pos_intersection + x] == word[j + x])):
        return False
  return True


# given a valid placement, determine the x and y position of the word to be placed
def determine_position(x_pos, y_pos, j, is_horizontal):
  #place word vertically
  start_x = 0
  start_y = 0
  if is_horizontal:
    start_x = x_pos
    start_y = y_pos - j
  # word will be placed horizontally
  else:
    start_y = y_pos
    start_x = x_pos - j
  
  return (start_x, start_y, not is_horizontal)
  

# return the number of intersections between the word placed on the board and other words
def determine_num_used_intersections(x_pos, y_pos, grid, word, is_horizontal):
  count = 0
  if is_horizontal:
    for y in range(len(word)):
      if grid[y_pos + y][x_pos] != " ":
        count += 1
  else:
    for x in range(len(word)):
      if grid[y_pos][x_pos + x] != " ":
        count += 1 
  return count
  
  
# return a tuple of position and orientation
# grid: the puzzle grid
# word: the word to be added to the grid (not currently on it)
# intersection_words : all words on the grid that have at least one intersection with word
# positioned_words : all words on the grid and their position tuples (x, y, orientation)
def find_placement(grid, word, intersection_words, positioned_words):
  
  for word_on_board in intersection_words:
    
    # get x and y positions for word on the board
    x_pos = positioned_words[word_on_board][0]
    y_pos = positioned_words[word_on_board][1]

    # find intersecting letters between word on board and given word
    word_on_board_set = set(word_on_board)
    word_set = set(word)
    intersections = word_on_board_set.union(word_set)

    # go through word on board and intersecting letters, find the first intersecting letter that we can place a word at
    # BALLOON (0 to 6)
    # JAIL

    for i in range(len(word_on_board)):
      if word_on_board[i] in intersections:
        # find all intersections in the word to be placed
        

        # PROBLEM PROBABLY HERE! I DON'T THINK IT IS CHECKING ALL POSSIBLE INTERSECTIONS WITH THE WORD ON THE BOARD
        word_intersections = []
        for j in range(len(word)):
          if word[j] == word_on_board[i]:
            word_intersections.append(j)

        # check to see if we can intersect a word here
        is_horizontal = positioned_words[word_on_board][2] == True
        for j in word_intersections:
          if (is_valid_intersection(is_horizontal, x_pos, y_pos, i, j, grid, word)):
            return determine_position(x_pos, y_pos, j, is_horizontal)
                            
  return None
          

# place the grid on the board and return the new grid
def place_on_board(grid, word, placement, positioned_words):
  
  # add placement of word found in find_placement function to positioned_words
  positioned_words[word] = placement
  x = placement[0]
  y = placement[1]
  orientation = placement[2]

  for letter in word:
    if(orientation == True):
      grid[y][x] = letter
      x+=1
    else:
      grid[y][x] = letter
      y+=1

  return grid
  

# placing highest ranked words first, based on number of intersections with other words
def generate_puzzle_highest_ranked_first(grid):
  # ranking words based off number of intersections with all other words
  ranked_words = numIntersections(clues_dict.keys())

  # sort ranked words (in order of descending number of interesections)
  ranked_words = sorted(ranked_words, key=lambda x: x[0], reverse=True)  

  # placing first word
  first_word = ranked_words[0][1]
  x = size//2 - len(first_word)//2
  y = size//2
  whitespace = size * size - len(first_word)
  words_in_puzzle = [first_word]
  
  for letter in first_word:
    grid[y][x] = letter
    x += 1
    
  # structure to store word positions on crossword, with x and y, and whether the 
  # word is horizontal or vertical
  positioned_words = {first_word: ((x-len(first_word)), y, True)}
  iterations = 0
  
  while whitespace > 0 and iterations < 10000: # and other condition that i havent thought of
    ranked_words = numIntersections(words_in_puzzle)
    if ranked_words == None:
      break

    rank = 0
    no_word_found = True
    while rank < len(ranked_words) and no_word_found:
      word = ranked_words[rank][1]

      if word not in positioned_words:
        intersection_words = contains_intersection(word, words_in_puzzle)

        # find ideal placement of word on grid
        placement = find_placement(grid, word, intersection_words, positioned_words)
        if placement != None:
          # place word on grid
          grid = place_on_board(grid, word, placement, positioned_words)
          print(positioned_words)
          
          # decrease whitespace
          # whitespace - length of word - number of intersections being used
          whitespace = whitespace - len(word) + determine_num_used_intersections(placement[0], placement[1], grid, word, placement[2])
          pretty_print(grid)
          print(word)
          print(whitespace)
          no_word_found = False
      rank += 1
    iterations += 1
  
  pretty_print(grid)
  return grid
  
generate_puzzle_highest_ranked_first(grid)