import pandas as pd
import numpy as np
import random

def clean_words_create_grid(size):
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
    

  # # get user input
  # size = int(input("What size would you like the crossword to be? Please pick a number between 6 and 20: "))
  # while size > 20 or size < 4:
  #   size = int(input("This size is out of bounds. What size would you like the crossword to be? Please pick a number between 6 and 20: "))

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

  return grid, clues_dict

def pretty_print(g):
  for row in g:
    print(row)

# return number of intersection the rest of the words have with the current words in the puzzle
def ranked_by_num_intersections(current_words, clues_dict):
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

# # ranking words based off number of intersections with all other words
# ranked_words = ranked_by_num_intersections(clues_dict.keys())

# # sort ranked words (in order of descending number of interesections)
# ranked_words = sorted(ranked_words, key=lambda x: x[0], reverse=True)  

# print(ranked_words)

# find which words a given word intersects with
def contains_intersection(w, current):
  intersection = set()
  for word in current:
    for letter in w:
      if letter in word:
        intersection.add(word)
  return intersection

# check spacing near the word to make sure it is either empty or has matching letters with word on board
def check_spacing(grid, first, second, word_intersection, y, is_horizontal, word):
  # invalid intersection (not enough spaces above word) 
  if first < 0:
    return False
  if first >= len(grid):
    return False
  if second < 0:
    return False
  if second >= len(grid):
    return False

  if not ((grid[first][second] == ' ') or (grid[first][second] == word[word_intersection + y]) or (grid[first][second] == '-')):
    return False
    
  # make sure we are not checking spaces to the left and right if we are at the intersection
  if(y != 0):
    # check spaces to left to make sure they're empty
    if is_horizontal:
      if second > 0 and (grid[first][second - 1] != ' ' and grid[first][second - 1] != '-'):
        return False
      # check spaces to right to make sure they're empty
      if second < len(grid) - 1 and (grid[first][second + 1] != ' ' and grid[first][second + 1] != '-') :
        return False
    else:
      if second > 0 and (grid[first - 1][second] != ' ' and grid[first - 1][second] != '-'):
        return False
      # check spaces to right to make sure they're empty
      if (second < len(grid) - 1) and (grid[first + 1][second] != ' ' and grid[first + 1][second] != '-'):
        return False

  return True


# i = index of intersection of word on board
# j = index of intersection of word we are trying to place
def is_valid_intersection(is_horizontal, x_pos, y_pos, i, j, grid, word):
  if (is_horizontal):
    # find position of j in word on board / on grid
    x_pos_intersection = x_pos + i
    y_pos_intersection = y_pos
    # check if spot directly above and/or below letter are free
    

    # check spacing above the word
    for y in range(j + 1):
      if not check_spacing(grid, y_pos_intersection - y, x_pos_intersection, j, 0-y, True, word):
        return False
    
    # check spacing below the word   
    for y in range(len(word) - j):
      if not check_spacing(grid, y_pos_intersection + y, x_pos_intersection, j, y, True, word):
        return False
    
      # place horizontally
  else:
    x_pos_intersection = x_pos
    y_pos_intersection = y_pos + i

    # check spacing to the left of word 
    for x in range(j+1):
      if not check_spacing(grid, y_pos_intersection, x_pos_intersection - x, j, 0-x, False, word):
        return False
  
    # check spacing to the right of word
    for x in range(len(word) - j):
      if not check_spacing(grid, y_pos_intersection, x_pos_intersection + x, j, x, False, word):
        return False

  return True


# given a valid placement, determine the x and y position of the word to be placed
def determine_position(x_pos, y_pos, i, j, is_horizontal):
  # place word vertically
  start_x = 0
  start_y = 0
  if is_horizontal:
    start_x = x_pos + i
    start_y = y_pos - j
  # word will be placed horizontally
  else:
    start_x = x_pos - j
    start_y = y_pos + i
  
  return (start_x, start_y, not is_horizontal)
  

# return the number of intersections between the word placed on the board and other words
def determine_num_used_intersections(x_pos, y_pos, grid, word, is_horizontal):
  count = 0
  if is_horizontal:
    for x in range(len(word)):
      if grid[y_pos][x_pos + x] != " ":
        count += 1
  else:
    for y in range(len(word)):
      if grid[y_pos + y][x_pos] != " ":
        count += 1 
  return count
  
  
def determine_whitespace_to_remove(grid, x_pos, y_pos, word, is_horizontal):
  used_intersections = determine_num_used_intersections(x_pos, y_pos, grid, word, is_horizontal)
  to_remove = len(word) - used_intersections

  # remove spaces surrounding word where no other word can be placed
  for i in range(len(word)):
    if is_horizontal:
      # check above and below to remove whitespace
      if y_pos + 1 < len(grid) and grid[y_pos + 1][x_pos + i] == ' ':
        to_remove += 1
        grid[y_pos + 1][x_pos + i] = '-'
      if y_pos - 1 >= 0 and grid[y_pos - 1][x_pos + i] == ' ':
        to_remove += 1
        grid[y_pos - 1][x_pos + i] = '-'
    else:
      # check left and right to remove whitespace
      if x_pos + 1 < len(grid) and grid[y_pos + i][x_pos + 1] == ' ':
        to_remove += 1
        grid[y_pos + i][x_pos + 1] = '-'
      if x_pos - 1 >= 0 and grid[y_pos + i][x_pos - 1] == ' ':
        to_remove += 1
        grid[y_pos + i][x_pos - 1] = '-'

  return to_remove


  
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
            return determine_position(x_pos, y_pos, i, j, is_horizontal)
                            
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
  
def place_first_word(size, word, grid):
  x = size//2 - len(word)//2
  y = size//2
  
  for i in range(len(word)):
    grid[y][x] = word[i]
    
    # check above and below to remove whitespace
    if y + 1 < len(grid) and grid[y + 1][x] == ' ':
      grid[y + 1][x] = '-'
    if y - 1 >= 0 and grid[y - 1][x] == ' ':
      grid[y - 1][x] = '-'
    
    x += 1

  return grid, x, y

# placing highest ranked words first, based on number of intersections with other words
def generate_puzzle_highest_ranked_first(size, grid, clues_dict):
  # ranking words based off number of intersections with all other words
  ranked_words = ranked_by_num_intersections(clues_dict.keys(), clues_dict)

  # sort ranked words (in order of descending number of interesections)
  ranked_words = sorted(ranked_words, key=lambda x: x[0], reverse=True)  

  # placing first word
  first_word = ranked_words[0][1]
  grid, x, y = place_first_word(size, first_word, grid)
  whitespace = size * size - len(first_word)
  words_in_puzzle = [first_word]

  # structure to store word positions on crossword, with x and y, and whether the 
  # word is horizontal or vertical
  positioned_words = {first_word: ((x-len(first_word)), y, True)}
  iterations = 0
  
  while whitespace > 0 and iterations < 5000: # and other condition that i havent thought of
    ranked_words = ranked_by_num_intersections(words_in_puzzle, clues_dict)
    ranked_words = sorted(ranked_words, key=lambda x: x[0], reverse=True)
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
          whitespace -= determine_whitespace_to_remove(grid, placement[0], placement[1], word, placement[2])
          grid = place_on_board(grid, word, placement, positioned_words)
          no_word_found = False
      rank += 1
    iterations += 1
  
  pretty_print(grid)
  return grid, positioned_words


def generate_puzzle_highest_ranked_longest_first(size, grid, clues_dict):
  # ranking words based off number of intersections with all other words
  ranked_words = ranked_by_num_intersections(clues_dict.keys(), clues_dict)

  # sort ranked words (in order of descending length and number of interesections)
  ranked_words = sorted(ranked_words, key=lambda x: (len(x), x[0]), reverse=True)  

  word = ranked_words[0][1]
  
  # placing first word
  grid, x, y = place_first_word(size, word, grid)
  whitespace = size * size - len(word)
  words_in_puzzle = [word]

  positioned_words = {word: ((x-len(word)), y, True)}
  iterations = 0
  
  while whitespace > 0 and iterations < 5000:
    ranked_words = ranked_by_num_intersections(words_in_puzzle, clues_dict)
    ranked_words = sorted(ranked_words, key=lambda x: (len(x), x[0]), reverse=True)
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
          whitespace -= determine_whitespace_to_remove(grid, placement[0], placement[1], word, placement[2])
          grid = place_on_board(grid, word, placement, positioned_words)
          no_word_found = False
      rank += 1
    iterations += 1
  
  pretty_print(grid)
  return grid

def generate_puzzle_random_first_word(size, grid, clues_dict):
  word = random.choice(list(clues_dict))

  grid, x, y = place_first_word(size, word, grid)
  whitespace = size * size - len(word)
  words_in_puzzle = [word]

  positioned_words = {word: ((x-len(word)), y, True)}
  iterations = 0

  while whitespace > 0 and iterations < 5000: # and other condition that i havent thought of
    ranked_words = ranked_by_num_intersections(words_in_puzzle, clues_dict)
    ranked_words = sorted(ranked_words, key=lambda x: x[0], reverse=True)
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
          whitespace -= determine_whitespace_to_remove(grid, placement[0], placement[1], word, placement[2])
          grid = place_on_board(grid, word, placement, positioned_words)
          no_word_found = False
      rank += 1
    iterations += 1
  
  pretty_print(grid)
  return grid


def score_generated(grid):
  letters = 0
  for row in grid:
    for letter in row:
      if letter != ' ' and letter != '-':
        letters += 1
  return letters / (len(grid) * len(grid))

# remove a word from positioned words if it has the same x, y and direction as another word
# ex: word1 = SEAS, word2 = SEA (remove word2 because the words start at the same place)
positioned_words = {'ASEA': (0, 2, True), 'EASE': (1, 0, False), 'SEAS': (3, 0, False), 'SEA': (3, 0, False)}
def clean_placed_words(positioned_words):
  cleaned_words = {}
  for word1 in positioned_words:
    overlap_found = False
    for word2 in positioned_words:
      if (word1 != word2 and positioned_words[word1][0] == positioned_words[word2][0] 
        and positioned_words[word1][1] == positioned_words[word2][1] and positioned_words[word1][2] == positioned_words[word2][2]): 
          if len(word1) < len(word2):
            overlap_found = True
    if not overlap_found:
      cleaned_words[word1] = positioned_words[word1]
  
  return cleaned_words

# print("first algo")
# generate_puzzle_highest_ranked_first(grid)
# print("second algo")
# generate_puzzle_highest_ranked_longest_first(grid)
# print ("third algo")
# generate_puzzle_random_first_word(grid)