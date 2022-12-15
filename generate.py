import pandas as pd
import numpy as np
import random

# Cleans words in dataset and adds to a dictionary
# `size` is the length and width of the crossword which was inputted by the user
# Returns: the cleaned clues dictionary, dictionary of letters ranked by their 
# frequency in the dataset
def clean_words(size):
  clues = pd.read_csv('custom_clues.csv')
  all_words = {}

  # clean data and add to dictionary
  # for i in range(len(clues)):

  clues = clues.dropna()
  for index, row in clues.iterrows():
    all_words[row['answer']] = row['clue']

  # remove words longer than size of puzzle and remove 1 and 2-letter words
  clues_dict = {}

  # dictionary to keep track of letters based on how many times they are used
  # in words in the puzzle
  ranked_letters = {}
  
  for word in all_words.keys():
    if len(word) <= size:
      if(not len(word) <= 2):

        # remove spaces in clues
        word_new = word.replace(" ", "")
        
        # remove numbers in the clue
        num_index = all_words[word].rfind("(")
        clue = all_words[word]
        # "(" found - if it's not found, no number so don't want to change clue
        if (num_index != -1):
          clue = clue[0:num_index]
        clues_dict[word_new] = clue
      
        # keep track of counts of letters in each word
        for c in word_new:
          if(c not in ranked_letters.keys()):
            ranked_letters[c] = 0
          ranked_letters[c] += 1
            
  return clues_dict, ranked_letters


# Creates the starting grid based on user-inputted size
# `size` is the length and width of the crossword which was inputted by the user
# Returns: an empty crossword grid
def create_grid(size):
  # create grid to match inputted size
  grid = []
  for i in range(size):
    g = []
    for j in range(size):
      g.append(' ')
    grid.append(g)
  return grid


# Prints a given grid
# `grid` is an inputted crossword grid
def pretty_print(grid):
  for row in grid:
    print(row)


# Ranks words based on number of intersections the rest of the words have with 
# the words passed in
# `words_to_rank` is the array of words to be ranked against words in `clues_dict`
# `clues_dict` is the cleaned dictionary of words to clues
# Returns: a sorted (descending) list of tuples of words and counts of number of 
# intersections the word has with other words 
def ranked_by_num_intersections(words_to_rank, clues_dict):
  ranked_words = []
  for word1 in clues_dict.keys():
    # count = number of intersections between current words in puzzle and all other words
    count = 0
    for word2 in words_to_rank:
      if(not(word1 == word2)):
        for l in word1:
          if l in word2:
            count +=1
    
    if(count != 0):
      ranked_words.append((count, word1))

  if ranked_words == []:
    return None
    
  return sorted(ranked_words, key=lambda x: x[0], reverse=True)


# Ranks words by having letters in common with the letters on the board
# `grid` is the current crossword grid
# `clues_dict` is the cleaned dictionary of words to clues
# Returns: a sorted (descending) list of tuples of words and counts of common 
# letters the word has with letters on the board
def ranked_by_common_letters(grid, clues_dict):
  ranked_words = []
  letters_in_puzzle = []
  for row in grid:
    for char in row:
      if char != ' ' and char != '-':
        letters_in_puzzle.append(char)
  for word in clues_dict.keys():
    count = 0
    for letter in letters_in_puzzle:
      if letter in word:
        count += 1
    
    if count != 0:
      ranked_words.append((count, word))

  if ranked_words == []:
    return None

  return sorted(ranked_words, key=lambda x: x[0], reverse=True)

# Determines if the given coordinates of a cell are an intersection on the puzzle
# `y` is the y position of the cell to be to be checked
# `x` is the x position of the cell to be to be checked
# `grid` is the current crossword grid
# Returns: True if the given coordinates are an intersection, False if not
def is_intersection(y, x, grid):
  left = False
  right = False
  up = False
  down = False
  if y > 0:
    if grid[y - 1][x] != ' ' and grid[y - 1][x] != '-': 
      up = True
  if x > 0:
    if grid[y][x - 1] != ' ' and grid[y][x - 1] != '-':
      left = True
  if y < len(grid) - 1:
    if grid[y + 1][x] != ' ' and grid[y + 1][x] != '-':
      down = True
  if x < len(grid) - 1:
    if grid[y][x + 1] != ' ' and grid[y][x + 1] != '-':
      right = True
  return (up and right) or (right and down) or (down and left) or (left and up)


# Ranks words by how frequent their letters appear in all of the words in the dataset
# `clues_dict` is the cleaned dictionary of words to clues
# `ranked_letters` is the dictionary of letters ranked by their frequency in the dataset
# Returns: a sorted (descending) list of tuples of words and scores based on 
# the letters making up the word and their frequencies
def ranked_by_letter_score(clues_dict, ranked_letters):
  # sort ranked_letters by count of letters & convert back to dictionary w values
  sorted_ranked_letters = sorted(ranked_letters.items(), key=lambda x:x[1], reverse = True)
  ranked_letters = dict(sorted_ranked_letters)

  total_letters = len(ranked_letters)
  points = 6
  count = 1

  letter_scores = {}
  # dictionary of scores for each letter based on the ranked letters
  for letter in ranked_letters:
    # split up into 6 sections (first section letters = 6 points, second = 5 points, etc.)
    if (count <= total_letters//6):
      # increase to keep track of position in section
      count += 1
    # if count > total_letters//6, then reset it to 1, and reduce points by 1 
    # for the next group of letters
    else:
      points -= 1
      count = 1
    # assign each letter its determined score
    letter_scores[letter] = points

  # rank words based on scores of letters they contain
  ranked_words = []
  for word in clues_dict.keys():
    word_score = 0
    for c in word:
      # add the score of each letter in the word to the dict at key = word 
      word_score += letter_scores[c]
    ranked_words.append((word_score, word))
  
  return sorted(ranked_words, key=lambda x: x[0], reverse=True)


# Ranks words in the dictionary which have letters in common with the letters on 
# the board that are not yet an intersection point
# `grid` is the current crossword grid
# `clues_dict` is the cleaned dictionary of words to clues
# Returns: a sorted (descending) list of tuples of words and counts of common 
# letters the word has with letters on the board that are not intersection points
def ranked_without_intersections(grid, clues_dict):
  intersectable_letters = []
  ranked_words = []
  
  for y in range(len(grid)):
    for x in range(len(grid)):
      if not is_intersection(y, x, grid) and grid[y][x] != ' ' and grid[y][x] != '-':
        intersectable_letters.append(grid[y][x])
        
  for word in clues_dict.keys():
    count = 0
    for letter in intersectable_letters:
      if letter in word:
        count += 1
    
    if count != 0:
      ranked_words.append((count, word))

  if ranked_words == []:
    return None

  return sorted(ranked_words, key=lambda x: x[0], reverse=True)


# Ranks words in the dictionary by the number of common letters they have with the 
# letters on the board that are not yet an intersection point first, and by the 
# number of unique letters they introduce to the the puzzle
# `grid` is the current crossword grid
# `clues_dict` is the cleaned dictionary of words to clues
# Returns: a sorted (descending) list of tuples of words and counts of common 
# letters the word has with letters on the board that are not intersection points
# and a score determined by the number of unique letters the word introduces to 
# the the puzzle
def ranked_without_intersections_and_unique_letters(grid, clues_dict):
  intersectable_letters = []
  letters_in_grid = set()
  ranked_words = []

  for y in range(len(grid)):
    for x in range(len(grid)):
      if not is_intersection(y, x, grid) and grid[y][x] != ' ' and grid[y][x] != '-':
        intersectable_letters.append(grid[y][x])
      letters_in_grid.add(grid[y][x])
  
  for word in clues_dict.keys():
    count = 0
    unique_score = 0

    for letter in intersectable_letters:
      if letter in word:
        count += 1
    
    for letter in word:
      if letter not in letters_in_grid:
        unique_score += 1

    if count != 0:
      ranked_words.append((count, unique_score, word))

  if ranked_words == []:
    return None

  ranked_words = sorted(ranked_words, lambda x: (x[0], x[1]), reverse=True)
  return ranked_words


# Determines which words in the puzzle a given word intersects with
# `w` is a given word to find intersecting words with
# `current_words` is the current words in the puzzle
# Returns: a list of words in the puzzle with which a given word intersects
# with
def contains_intersection(w, current_words):
  intersecting_words = set()
  for word in current_words:
    for letter in w:
      if letter in word:
        intersecting_words.add(word)
  return intersecting_words

# Checks spacing around a word to be placed to make sure it is either empty or 
# has matching letters with the word on the board that will possibly intersect 
# the word to be placed
# `grid` is the current crossword grid
# `y_pos` is the y position to be checked in the grid
# `x_pos` is the x position to be checked in the grid
# `word_intersection` is the index of the intersection of word we are trying to 
#                     place with the word on the board it intersects with
# `y` is the current x/y position in the word
# `is_horizontal` is the horizontal/vertical alignment of the word on the board 
#                 we want to intersect with (True if horizontal)
# `word` is the word to be placed on the board
# Returns: True if the spaces near the word are either empty or contain the 
# intersection between the word to be placed and word on the board to be 
# intersected with, and False if not
def check_spacing(grid, y_pos, x_pos, word_intersection, y, is_horizontal, word):
  # invalid intersection (not enough spaces above word) 
  if y_pos < 0:
    return False
  if y_pos >= len(grid):
    return False
  if x_pos < 0:
    return False
  if x_pos >= len(grid):
    return False

  if not ((grid[y_pos][x_pos] == ' ') or (grid[y_pos][x_pos] == word[word_intersection + y]) 
  or (grid[y_pos][x_pos] == '-')):
    return False
    
  # make sure we are not checking spaces to the left and right if we are at the intersection
  if(y != 0):
    # check spaces to left to make sure they're empty
    if is_horizontal:
      if x_pos > 0 and (grid[y_pos][x_pos - 1] != ' ' and grid[y_pos][x_pos - 1] != '-'):
        return False
      # check spaces to right to make sure they're empty
      if x_pos < len(grid) - 1 and (grid[y_pos][x_pos + 1] != ' ' and grid[y_pos][x_pos + 1] != '-') :
        return False
    else:
      if y_pos > 0 and (grid[y_pos - 1][x_pos] != ' ' and grid[y_pos - 1][x_pos] != '-'):
        return False
      # check spaces to right to make sure they're empty
      if (y_pos < len(grid) - 1) and (grid[y_pos + 1][x_pos] != ' ' and grid[y_pos + 1][x_pos] != '-'):
        return False

  return True


# Determines if a word can be placed, intersecting with a current word on the 
# board
# `is_horizontal` is the horizontal/vertical alignment of the word on the board 
#                 we want to intersect with (True if horizontal)
# `x_pos` is the x position for the word on the board to be intersected with
# `y_pos` is the y position for the word on the board to be intersected with
# `word_intersection` is the index of the intersection of word we are trying to 
#                     place with the word on the board it intersects with
# `word_on_board_intersection` is the index of the intersection of the word on 
#                              with the word we are trying to place
#                     place with the word on the board it intersects with
# `grid` is the current crossword grid
# `word` is the word to be placed on the board
# Returns: True if a word can be placed intersecting with a given word on the
# board, False if not
def is_valid_intersection(is_horizontal, x_pos, y_pos, word_on_board_intersection, 
word_intersection, grid, word):
  if (is_horizontal):
    # find position of j in word on board / on grid
    x_pos_intersection = x_pos + word_on_board_intersection
    y_pos_intersection = y_pos
    # check if spot directly above and/or below letter are free
    
    # check spacing above the word
    for y in range(word_intersection + 1):
      if not check_spacing(grid, y_pos_intersection - y, x_pos_intersection, 
      word_intersection, 0-y, True, word):
        return False
    
    # check spacing below the word   
    for y in range(len(word) - word_intersection):
      if not check_spacing(grid, y_pos_intersection + y, x_pos_intersection, 
      word_intersection, y, True, word):
        return False
    
    # check spot above and below of the word to be placed to make sure no letter is there:
    y_above_word = y_pos_intersection  - word_intersection - 1
    y_below_word = y_pos_intersection + (len(word) - word_intersection)

    if y_above_word >= 0 and not (grid[y_above_word][x_pos_intersection] == ' ' or grid[y_above_word][x_pos_intersection] == '-'):
        return False
    if (y_below_word < len(grid)) and not (grid[y_below_word][x_pos_intersection] == ' ' or grid[y_below_word][x_pos_intersection] == '-'):
        return False
        
  # place horizontally
  else:
    x_pos_intersection = x_pos
    y_pos_intersection = y_pos + word_on_board_intersection

    # check spacing to the left of word 
    for x in range(word_intersection+1):
      if not check_spacing(grid, y_pos_intersection, x_pos_intersection - x, 
      word_intersection, 0-x, False, word):
        return False
  
    # check spacing to the right of word
    for x in range(len(word) - word_intersection):
      if not check_spacing(grid, y_pos_intersection, x_pos_intersection + x, 
      word_intersection, x, False, word):
        return False

    # check spot to the left and right of the word to be placed to make sure no letter is there:
    x_left_of_word = x_pos_intersection  - word_intersection - 1
    x_right_of_word = x_pos_intersection + (len(word) - word_intersection)

    if x_left_of_word >= 0 and not (grid[y_pos_intersection][x_left_of_word] == ' ' or grid[y_pos_intersection][x_left_of_word] == '-'):
        return False
    if (x_right_of_word < len(grid)) and not (grid[y_pos_intersection][x_right_of_word] == ' ' or grid[y_pos_intersection][x_right_of_word] == '-'):
        return False
  return True


# Determines the starting position for a word to be placed on the board given
# a valid placement
# `x_pos` is the x position for the word on the board to be intersected with
# `y_pos` is the y position for the word on the board to be intersected with
# `word_intersection` is the index of the intersection of word we are trying to 
#                     place with the word on the board it intersects with
# `word_on_board_intersection` is the index of the intersection of the word on 
#                              with the word we are trying to place
# `is_horizontal` is the horizontal/vertical alignment of the word on the board 
#                 we want to intersect with (True if horizontal)

# Returns: a triple of the x and y positions of the word to be placed on the 
# board, as well as its horizontal/vertical alignment (True for horizontal, 
# False for vertical)
def determine_position(x_pos, y_pos, word_intersection, word_on_board_intersection, 
is_horizontal):
  # place word vertically
  start_x = 0
  start_y = 0
  if is_horizontal:
    start_x = x_pos + word_intersection
    start_y = y_pos - word_on_board_intersection
  # word will be placed horizontally
  else:
    start_x = x_pos - word_on_board_intersection
    start_y = y_pos + word_intersection
  
  return (start_x, start_y, not is_horizontal)
  

# Determines the number of intersections number between the word placed on the 
# board and other words on the board
# `x_pos` is the x position for the word that was just placed on the board
# `y_pos` is the y position for the word that was just placed on the board
# `grid` is the current crossword grid
# `word` is the word that was just placed on the board
# `is_horizontal` is the horizontal/vertical alignment of the word that was just 
#                 placed on the board (True if horizontal)
# Returns: the number of intersections between the word placed on the board and 
# other words on the board
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
  

# Determines the whitespace to remove once a word has just been placed on the 
# board 
# `grid` is the current crossword grid
# `x_pos` is the x position for the word that was just placed on the board
# `y_pos` is the y position for the word that was just placed on the board
# `word` is the word that was just placed on the board
# `is_horizontal` is the horizontal/vertical alignment of the word that was just 
#                 placed on the board (True if horizontal)
# Returns: the count of whitespace to remove once a word has just been placed on 
# the board
def determine_whitespace_to_remove(grid, x_pos, y_pos, word, is_horizontal):
  used_intersections = determine_num_used_intersections(x_pos, y_pos, grid, word, 
  is_horizontal)
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
    
  if is_horizontal:
    # check left and right to remove whitespace
    if x_pos > 0 and grid[y_pos][x_pos - 1] == ' ':
      to_remove += 1
      grid[y_pos][x_pos - 1] = '-'
    if x_pos < len(grid) - 1 and grid[y_pos][x_pos + 1] == ' ':
      to_remove += 1
      grid[y_pos][x_pos + 1] = '-'

  else:
    # check above and below to remove whitespace
      if y_pos > 0 and grid[y_pos-1][x_pos] == ' ':
        to_remove += 1
        grid[y_pos-1][x_pos] = '-'
      if y_pos < len(grid) - 1 and grid[y_pos+1][x_pos] == ' ':
        to_remove += 1
        grid[y_pos+1][x_pos] = '-'
    
  return to_remove


# Determines if a word attempting to be placed on the board overlaps with any 
# current words on the board (in the same direction). If so, the word attempting 
# to be placed will not be placed.
# `position` is a triple of the x and y positions of the word to be placed on the 
#            board, as well as its horizontal/vertical alignment (True for 
#            horizontal, False for vertical)
# `positioned_words` is a dictionary of each word on the board mapped to a 
#                    triple of its x and y positions, as well as its horizontal/
#                    vertical alignment (True for horizontal, False for vertical)
# `word` is the word that is to be placed on the board

# Returns: True if a word to be placed on the board does not overlap with another 
# word already on the board, and False if words do overlap
def check_layering(position, positioned_words, word):
  word_x = position[0]
  word_y = position[1]
  
  # direction of word about to be placed
  horizontal = position[2]

  # get the row
  if horizontal:
    for word_on_board in positioned_words:
      if positioned_words[word_on_board][2] == True:
        word_on_board_x = positioned_words[word_on_board][0]
        word_on_board_y = positioned_words[word_on_board][1]

        # possible overlap
        if (word_y == word_on_board_y):
          # check that there are no spaces in between
          # loop from end of word 1 to beginning of word 2
          if(word_on_board_x < word_x):
            start = word_on_board_x + len(word_on_board)-1
            end = word_x
          else:
            start = word_x + len(word)-1
            end = word_on_board_x
          if(start >= end + 1):
              return False
  else:
    for word_on_board in positioned_words:
      if positioned_words[word_on_board][2] == False:
        word_on_board_x = positioned_words[word_on_board][0]
        word_on_board_y = positioned_words[word_on_board][1]
        # possible overlap
        if (word_x == word_on_board_x):
          # check that there are no spaces in between
          # loop from end of word 1 to beginning of word 2
          if(word_on_board_y < word_y):
            start = word_on_board_y + len(word_on_board)-1
            end = word_y
          else:
            start = word_y + len(word)-1
            end = word_on_board_y
          if (start >= end + 1):
            return False
  return True


# Determines a position to place a word on the board
# `grid` is the current crossword grid
# `word` is the word to be placed on the board
# `intersection_words` is the list of words in the puzzle with which the word to
#                      be placed intersects
# `positioned_words` is a dictionary of each word on the board mapped to a 
#                    triple of its x and y positions, as well as its horizontal/
#                    vertical alignment (True for horizontal, False for vertical)
# Returns: a triple of the x and y positions of the word to be placed on the 
# board, as well as its horizontal/vertical alignment (True for horizontal, 
# False for vertical) and None if no valid placement was found
def find_placement(grid, word, intersection_words, positioned_words):
  for word_on_board in intersection_words:
    
    # get x and y positions for word on the board
    x_pos = positioned_words[word_on_board][0]
    y_pos = positioned_words[word_on_board][1]

    # find intersecting letters between word on board and given word
    word_on_board_set = set(word_on_board)
    word_set = set(word)
    intersections = word_on_board_set.union(word_set)
    # go through word on board and intersecting letters, find the first 
    # intersecting letter that we can place a word at
    for i in range(len(word_on_board)):
      if word_on_board[i] in intersections:

        # find all intersections in the word to be placed
        word_intersections = []
        for j in range(len(word)):
          if word[j] == word_on_board[i]:
            word_intersections.append(j)

        # check to see if we can intersect a word here
        is_horizontal = positioned_words[word_on_board][2]
        for j in word_intersections:
          if (is_valid_intersection(is_horizontal, x_pos, y_pos, i, j, grid, word)):
            position = determine_position(x_pos, y_pos, i, j, is_horizontal)
            if check_layering(position, positioned_words, word):
              return position
  return None


# Places a given word on the board
# `grid` is the current crossword grid
# `word` is the word to be placed on the board
# `placement` is a triple of the x and y positions of the word to be placed on the 
#             board, as well as its horizontal/vertical alignment (True for 
#             horizontal, False for vertical)
# `positioned_words` is a dictionary of each word on the board mapped to a 
#                    triple of its x and y positions, as well as its horizontal/
#                    vertical alignment (True for horizontal, False for vertical)
# Returns: the updated crossword grid (now including the word that was just placed)
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
  

# Places the first word on the board
# `size` is the length and width of the crossword which was inputted by the user
# `word` is the first word to be placed on the board
# `grid` is the current crossword grid
# Returns: the updated crossword grid now containing the first word, the x 
# position of the end of the first word on the grid, and the y position of the 
# first word on the grid
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

def find_placement_direction_constrained(grid, word, intersection_words, positioned_words, next_word_horizontal):
  for word_on_board in intersection_words:
    
    # get x and y positions for word on the board
    x_pos = positioned_words[word_on_board][0]
    y_pos = positioned_words[word_on_board][1]

    # find intersecting letters between word on board and given word
    word_on_board_set = set(word_on_board)
    word_set = set(word)
    intersections = word_on_board_set.union(word_set)
    # go through word on board and intersecting letters, find the first 
    # intersecting letter that we can place a word at
    for i in range(len(word_on_board)):
      if word_on_board[i] in intersections:

        # find all intersections in the word to be placed
        word_intersections = []
        for j in range(len(word)):
          if word[j] == word_on_board[i]:
            word_intersections.append(j)

        # check to see if we can intersect a word here
        is_horizontal = positioned_words[word_on_board][2]
        if is_horizontal != next_word_horizontal:
          for j in word_intersections:
            if (is_valid_intersection(is_horizontal, x_pos, y_pos, i, j, grid, word)):
              position = determine_position(x_pos, y_pos, i, j, is_horizontal)
              if check_layering(position, positioned_words, word):
                return position
  return None

# CROSSWORD-GENERATING ALGORITHMS

# ALGORITHM 1

# This is the first algorithm generating a crossword puzzle. With this algorithm, 
# words are placed on the grid based on rank (number of intersections the word has
# with other words on the board), starting with the highest ranked word, and 
# continuing on to the next highest ranked word and so on until the 
# completion of the generation of the puzzle.
# `size` is the length and width of the crossword which was inputted by the user
# `grid` is the current crossword grid
# `clues_dict` is the cleaned dictionary of words to clues

# Returns: a generated crossword (the updated grid) of size inputted by the user as well as a 
# dictionary of each word on the board mapped to a triple of its x and y positions, 
# as well as its horizontal/vertical alignment (True for horizontal, False for vertical)
def generate_puzzle_highest_ranked_first(size, grid, clues_dict):
  # ranking words based off number of intersections with all other words
  ranked_words = ranked_by_num_intersections(clues_dict.keys(), clues_dict)

  # # sort ranked words (in order of descending number of interesections)
  # ranked_words = sorted(ranked_words, key=lambda x: x[0], reverse=True)  

  # placing first word
  first_word = ranked_words[0][1]
  grid, x, y = place_first_word(size, first_word, grid)
  whitespace = size * size - 3*len(first_word)
  words_in_puzzle = [first_word]

  # structure to store word positions on crossword, with x and y, and whether the 
  # word is horizontal or vertical
  positioned_words = {first_word: ((x-len(first_word)), y, True)}
  iterations = 0
  
  while whitespace > 0 and iterations < 5000: 
    ranked_words = ranked_without_intersections(grid, clues_dict)

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
          words_in_puzzle.append(word)
          no_word_found = False
      rank += 1
    if no_word_found:
      break
    iterations += 1
  
  return grid, positioned_words


# ALGORITHM 2

# This is the second algorithm generating a crossword puzzle. With this algorithm, 
# we make a slight distinction in which words are placed on the board: instead of 
# choosing the word with the most number of intersections, we choose the highest 
# ranked (most number of intersections) word of maximum length. The maximum length 
# is the longest word in the list of words. 
# `size` is the length and width of the crossword which was inputted by the user
# `grid` is the current crossword grid
# `clues_dict` is the cleaned dictionary of words to clues
# Returns: a generated crossword (the updated grid) of size inputted by the user as well as a 
# dictionary of each word on the board mapped to a triple of its x and y positions, 
# as well as its horizontal/vertical alignment (True for horizontal, False for vertical)
def generate_puzzle_highest_ranked_longest_first(size, grid, clues_dict):
  # ranking words based off number of intersections with all other words
  ranked_words = ranked_by_num_intersections(clues_dict.keys(), clues_dict)

  # sort ranked words (in order of descending length and number of interesections)
  ranked_words = sorted(ranked_words, key=lambda x: (len(x), x[0]), reverse=True)  

  word = ranked_words[0][1]
  
  # placing first word
  grid, x, y = place_first_word(size, word, grid)
  whitespace = size * size - 3*len(word)
  words_in_puzzle = [word]

  positioned_words = {word: ((x-len(word)), y, True)}
  iterations = 0
  
  while whitespace > 0 and iterations < 5000:
    ranked_words = ranked_without_intersections(grid, clues_dict)
    
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
          words_in_puzzle.append(word)
          no_word_found = False
      rank += 1
    if no_word_found:
      break
    iterations += 1
  
  return grid, positioned_words

# ALGORITHM 3

# This is the third algorithm generating a crossword puzzle. With this algorithm, 
# we choose a random word to be placed first. Then, words are placed on the grid 
# based on rank (number of intersections the word has with other words on the board), 
# starting with the highest ranked word, and continuing on to the next highest 
# ranked word and so on until the completion of the generation of the puzzle.
# `size` is the length and width of the crossword which was inputted by the user
# `grid` is the current crossword grid
# `clues_dict` is the cleaned dictionary of words to clues
# Returns: a generated crossword (the updated grid) of size inputted by the user as well as a 
# dictionary of each word on the board mapped to a triple of its x and y positions, 
# as well as its horizontal/vertical alignment (True for horizontal, False for vertical)
def generate_puzzle_random_first_word(size, grid, clues_dict):
  word = random.choice(list(clues_dict))

  grid, x, y = place_first_word(size, word, grid)
  whitespace = size * size - 3*len(word)
  words_in_puzzle = [word]

  positioned_words = {word: ((x-len(word)), y, True)}
  iterations = 0

  while whitespace > 0 and iterations < 5000: 
    ranked_words = ranked_without_intersections(grid, clues_dict)
    
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
          whitespace -= determine_whitespace_to_remove(grid, placement[0], 
          placement[1], word, placement[2])
          grid = place_on_board(grid, word, placement, positioned_words)
          words_in_puzzle.append(word)
          no_word_found = False
      rank += 1
    if no_word_found:
      break
    iterations += 1
  return grid, positioned_words
  
# ALGORITHM 4

# This is the fourth algorithm generating a crossword puzzle. With this algorithm, 
# we choose a the highest ranked word to be placed first horizontally. The next word to be
# placed on the grid will then be the next highest ranked word, but will be placed
# vertically. Words are placed on the grid based on rank (number of intersections 
# the word has with other words on the board), starting with the highest ranked 
# word, and continuing on to the next highest ranked word while alternating placement
# alignment and so on until the completion of the generation of the puzzle.
# `size` is the length and width of the crossword which was inputted by the user
# `grid` is the current crossword grid
# `clues_dict` is the cleaned dictionary of words to clues
# Returns: a generated crossword (the updated grid) of size inputted by the user as well as a 
# dictionary of each word on the board mapped to a triple of its x and y positions, 
# as well as its horizontal/vertical alignment (True for horizontal, False for vertical)
def generate_puzzle_require_alternation(size, grid, clues_dict):
  # ranking words based off number of intersections with all other words
  ranked_words = ranked_by_num_intersections(clues_dict.keys(), clues_dict)

  # placing first word
  first_word = ranked_words[0][1]
  grid, x, y = place_first_word(size, first_word, grid)
  whitespace = size * size - 3*len(first_word)
  words_in_puzzle = [first_word]

  # structure to store word positions on crossword, with x and y, and whether the 
  # word is horizontal or vertical
  positioned_words = {first_word: ((x-len(first_word)), y, True)}
  iterations = 0

  next_placement_horizontal = False

  while whitespace > 0 and iterations < 5000:
    ranked_words = ranked_without_intersections(grid, clues_dict)
    
    if ranked_words == None:
      break

    rank = 0
    no_word_found = True
    while rank < len(ranked_words) and no_word_found:
      word = ranked_words[rank][1]
      if word not in positioned_words:
        intersection_words = contains_intersection(word, words_in_puzzle)
        # find ideal placement of word on grid
        placement = find_placement_direction_constrained(grid, word, intersection_words, positioned_words, next_placement_horizontal)
        if placement != None:
          # place word on grid
          whitespace -= determine_whitespace_to_remove(grid, placement[0], 
          placement[1], word, placement[2])
          grid = place_on_board(grid, word, placement, positioned_words)
          words_in_puzzle.append(word)
          next_placement_horizontal = not next_placement_horizontal
          no_word_found = False
      rank += 1
    if no_word_found:
      break
    iterations += 1
  return grid, positioned_words

# ALGORITHM 5

# This is the fifth algorithm generating a crossword puzzle. With this algorithm, 
# we choose a random word to be placed first horizontally. The next word to be
# placed on the grid will then be the highest ranked word, but will be placed
# vertically. The following words placed on the grid based on rank (number of intersections 
# the word has with other words on the board), starting with the highest ranked 
# word, and continuing on to the next highest ranked word while alternating placement
# alignment and so on until the completion of the generation of the puzzle.
# `size` is the length and width of the crossword which was inputted by the user
# `grid` is the current crossword grid
# `clues_dict` is the cleaned dictionary of words to clues
# Returns: a generated crossword (the updated grid) of size inputted by the user as well as a 
# dictionary of each word on the board mapped to a triple of its x and y positions, 
# as well as its horizontal/vertical alignment (True for horizontal, False for vertical)

def generate_puzzle_require_alternation_random_first_word(size, grid, clues_dict):
  # placing first word
  first_word = random.choice(list(clues_dict))
  grid, x, y = place_first_word(size, first_word, grid)
  whitespace = size * size - 3*len(first_word)
  words_in_puzzle = [first_word]

  # structure to store word positions on crossword, with x and y, and whether the 
  # word is horizontal or vertical
  positioned_words = {first_word: ((x-len(first_word)), y, True)}
  iterations = 0

  next_placement_horizontal = False

  while whitespace > 0 and iterations < 5000: 
    ranked_words = ranked_without_intersections(grid, clues_dict)
    
    if ranked_words == None:
      break

    rank = 0
    no_word_found = True
    while rank < len(ranked_words) and no_word_found:
      word = ranked_words[rank][1]
      if word not in positioned_words:
        intersection_words = contains_intersection(word, words_in_puzzle)
        # find ideal placement of word on grid
        placement = find_placement_direction_constrained(grid, word, intersection_words, positioned_words, next_placement_horizontal)
        if placement != None:
          # place word on grid
          whitespace -= determine_whitespace_to_remove(grid, placement[0], placement[1], word, placement[2])
          grid = place_on_board(grid, word, placement, positioned_words)
          next_placement_horizontal = not next_placement_horizontal
          words_in_puzzle.append(word)
          no_word_found = False
      rank += 1
    if no_word_found:
      break
    iterations += 1
  return grid, positioned_words


# SCORE GENERATION

# METHOD 1

# Scores a given crossword puzzle (grid) based on how many letters are on the 
# grid in comparison to its size
# `grid` is the inputted crossword grid
# Returns: the proportion of letters on the grid to the size of the grid
def score_generated_minimize_whitespace(grid):
  letters = 0
  for row in grid:
    for letter in row:
      if letter != ' ' and letter != '-':
        letters += 1
  return letters / (len(grid) * len(grid))
  

# METHOD 2

# Scores a given crossword puzzle (grid) based on how many intersections are in 
# the grid in comparison to its size
# `grid` is the inputted crossword grid
# Returns: the proportion of number of intersections in the grid to the size of the grid
def score_generated_maximize_intersections(grid):
  num_intersections = 0
  for y in range(len(grid)):
    for x in range(len(grid)):
      if is_intersection(y, x, grid):
        num_intersections += 1
  return num_intersections / (len(grid) * len(grid))
  

# METHOD 3

# Scores a given crossword puzzle (grid) based on how many unique letters are on 
# the grid in comparison to its size
# `grid` is the inputted crossword grid
# Returns: the proportion of unique letters on the grid to the size of the grid
def score_generated_unique_letters(grid):
  letters = set()
  for row in grid:
    for char in row:
      if char != ' ' and char != '-':
        letters.add(char)
  return len(letters) / (len(grid) * len(grid))



# Removes a word from positioned words if it has the same x, y and direction as 
# another word in the grid
# `positioned_words` is a dictionary of each word on the board mapped to a 
#                    triple of its x and y positions, as well as its horizontal/
#                    vertical alignment (True for horizontal, False for vertical)
# Returns: a dictionary of each word on the board mapped to a triple of its x and 
# y positions, as well as its horizontal/vertical alignment (True for horizontal, 
# False for vertical) that does not include overlapped words
# ex: word1 = SEAS, word2 = SEA (remove word2 because the words start at the 
# same place)
def clean_placed_words(positioned_words):
  cleaned_words = {}
  for word1 in positioned_words:
    overlap_found = False
    for word2 in positioned_words:
      if (word1 != word2 and positioned_words[word1][0] == positioned_words[word2][0] 
        and positioned_words[word1][1] == positioned_words[word2][1] and 
        positioned_words[word1][2] == positioned_words[word2][2]): 
          if len(word1) < len(word2):
            overlap_found = True
    if not overlap_found:
      cleaned_words[word1] = positioned_words[word1]
  
  return cleaned_words

# TEST_GRID = [['B', ' ', ' ', ' '], ['E', ' ', ' ', ' '], ['A', 'S', 'E', 'A'], ['N', ' ', ' ', ' ']]
# TEST_INTERSECTION_SET = set()
# TEST_INTERSECTION_SET.add('ASEA')
# TEST_INTERSECTION_SET.add('BEAN')

# pretty_print(TEST_GRID)
# print(find_placement_direction_constrained(TEST_GRID, 'BED', TEST_INTERSECTION_SET, {'ASEA':(0, 2, True), 'BEAN':(0, 0, False)}, True))

# clues_dict, ranked_letters = clean_words(3)
# grid, p = generate_puzzle_random_first_word(3, create_grid(3), clues_dict)
# pretty_print(grid)
