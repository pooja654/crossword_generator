import PySimpleGUI as sg
import generate
import textwrap
import time

sg.theme('DarkAmber')

# Dummy Crossword Values Created for testing the GUI implementation
TEST_GRID = [['-','E','-','S'], [' ','A',' ','E'],['A','S','E','A'],[' ','E',' ','S']]
TEST_POSITIONED_WORDS = {'ASEA':(0, 2, True), 'EASE':(1, 0, False), 'SEAS':(3, 0, False)}
TEST_CLUES_DICT = {'ASEA':'this is the clue for asea', 'EASE':'this is the clue for ease', 'SEAS':'this is the clue for seas'}

# Static size of a singular square on crossword
BLOCK_SIZE = 25

# Create the layout for the home screen with an introduction greeting and a query for crossword size
# This returns the home window layout
def make_home_layout():
    return [
        [sg.Text("Hello from AI Crossword!", font=("Courier 25", 30), pad=(20, 20))],
        [sg.Text('Enter the size of your crossword (4 to 15):', font=("Courier 25", 20)), sg.InputText()],
        [sg.Button("Close", font=("Courier 25", 16), key='-CLOSE HOME-'), sg.Button("Make Crossword", font=("Courier 25", 16), key='-PLAY BUTTON-')],
        [sg.Text("INVALID SIZE, TRY AGAIN", key='-INVALID SIZE-', visible=False)]
    ]


# Create the layout for the play screen with a graph element as the crossword grid 
# Generate clues in a list format with text inputs to insert answers to the crossword
# This returns the play window layout with the Crossword
def make_play_layout():
    return [
        [sg.Text("Let's Play!", key='-START-')],
        [sg.Button("Close", key='-CLOSE PLAY-', visible=True), sg.Button("Back to Home", key='-BACK TO HOME-', visible=True)],
        [sg.Graph((500, 500), (0, 400), (400, 0), key='-CROSSWORD-',
                change_submits=True, drag_submits=False)]
    ]


# Create the layout for the end screen 
# Include the time the player took to complete the crossword
# This returns the end_window layout to be displayed
def make_end_window(time_took, word_numbers, grid, positioned_words):
    end_layout = [
            [sg.Text("Congratulations!")],
            [sg.Text("Time: " + time_took)],
            [sg.Graph((500, 500), (0, 400), (400, 0), key='-CROSSWORD-',
                    change_submits=True, drag_submits=False)],
            [sg.Button("Close", key='-CLOSE END OF GAME-', visible=True), sg.Button("Back to Home", key='-BACK TO HOME-', visible=True)]
    ]
    end_window = sg.Window("End", end_layout, size=(1000,1000), margins=(50, 50), element_justification='c')
    end_window.Finalize()
    generate_correct_grid(len(grid), grid, positioned_words, end_window['-CROSSWORD-'], word_numbers)
    return end_window


# Generate the clues for the selected words on the puzzle
# `clues_dict` is the cleaned dictionary of words to clues
# `word_numbers` is a dictionary mapping the number for the word and clue to the word itself
# `positioned_words` is a dictionary mapping the words that were placed on the board to a tuple (x, y, is_horizontal)
# which specifies the starting position of the word and the direction it was placed
# This returns a dictionary mapping the 'Horizontal' to (word number, clue) and 'Vertical' to (word number, clue) for 
# each clue
def generate_clues(clues_dict, word_numbers, positioned_words):
    clues = {'Horizontal' : [], 'Vertical' : []}
    for word in word_numbers:
        clue = clues_dict[word]
        if positioned_words[word][2]:
            clues['Horizontal'].append((word_numbers[word], clue))
        else:
            clues['Vertical'].append((word_numbers[word], clue))
    return clues


# Format the clues in the play screen layout
# `clues` is a dictionary where 'Horizontal' is mapped to a list of (clue number, clue) for all horizontal clues and
# 'Vertical' is mapped to a list of (clue number, clue) for all vertical clues
# This returns a mapping of the clue to the word number
def format_clues(clues, play_layout):
    horizontal = [[sg.Text('Across')]]
    vertical = [[sg.Text('Down')]]
    clue_number_to_word_number = {}
    clue_number = 0

    # iterate over the horizontal clues
    for i in range(len(clues['Horizontal'])):
        text = textwrap.wrap(str(clues['Horizontal'][i][0]) + '. ' + clues['Horizontal'][i][1], 40)
        text_box = True
        for t in text:
            if text_box:
                horizontal += [[sg.Text(t, justification='r', pad=(5,1)), sg.InputText()]]
                text_box = False
            else:
                horizontal += [[sg.Text(t, justification='r', pad=(5,1))]]
            clue_number_to_word_number[clue_number] = clues['Horizontal'][i][0]
        clue_number += 1

    # iterate over vertical clues
    for i in range(len(clues['Vertical'])):
        text = textwrap.wrap(str(clues['Vertical'][i][0]) + '. ' + clues['Vertical'][i][1], 40)
        text_box = True
        for t in text:
            if text_box:
                vertical += [[sg.Text(t, justification='r', pad=(5,1)), sg.InputText()]]
                text_box = False
            else:
                vertical += [[sg.Text(t, justification='r', pad=(5,1))]]
            clue_number_to_word_number[clue_number] = clues['Vertical'][i][0]
        clue_number += 1

    play_layout.append([sg.Column(horizontal, element_justification='l'), sg.Column(vertical, element_justification='l')])
    play_layout.append([sg.Button("Check", key='-CHECK PUZZLE-')])
    return clue_number_to_word_number


# Gives each placed word a number
# `size` is the length and width of the crossword which was inputted by the user
# `grid` is the completed crossword with the words placed
# `positioned_words` is a dictionary mapping the word to (x, y, is_horizontal) which specifies the starting position
# of the word and the direction it was placed
def create_word_numbers(size, grid, positioned_words):
    word_numbers = {}
    number = 1
    for y in range(size):
        for x in range(size):
            if grid[y][x] != ' ' and grid[y][x] != '-':
                for key in positioned_words.keys():
                    if positioned_words[key] == (x, y, True) or positioned_words[key] == (x, y, False):
                        if key not in word_numbers:
                            word_numbers[key] = number
                            number += 1
    return word_numbers


# Create the crossword grid to be drawn on the Graph element in the play layout
# `size` is the length and width of the crossword which was inputted by the user
# `grid` is the completed crossword with the words placed
# `positioned_words` is a dictionary mapping the word to (x, y, is_horizontal) which specifies the starting position
# of the word and the direction it was placed
# `crossword` is the graph element in the play_screen layout
# `word_numbers` is a dictionary mapping the number the word was assigned to the word
def generate_grid(size, grid, positioned_words, crossword, word_numbers):
    for y in range(size):
        for x in range(size):
            # for each square in the crossword grid
            if grid[y][x] != ' ' and grid[y][x] != '-':
                # create white text box
                crossword.draw_rectangle((x * BLOCK_SIZE + 5, y * BLOCK_SIZE + 3), (x * BLOCK_SIZE + BLOCK_SIZE + 5, y * BLOCK_SIZE + BLOCK_SIZE + 3), line_color='black', fill_color='white')
                
                # add numbers to top left of block for the first letter of the word
                for word in word_numbers:
                    if positioned_words[word][0] == x and positioned_words[word][1] == y:
                        crossword.draw_text('{}'.format(word_numbers[word]),(x * BLOCK_SIZE + 10, y * BLOCK_SIZE + 8))
    
            else:
                # create black text box
                crossword.draw_rectangle((x * BLOCK_SIZE + 5, y * BLOCK_SIZE + 3), (x * BLOCK_SIZE + BLOCK_SIZE + 5, y * BLOCK_SIZE + BLOCK_SIZE + 3), line_color='black', fill_color='black')


# Generate the crossword to be displayed in the GUI including the clues and the grid itself
# This runs each of the algorithms outlined in generate.py for creating crosswords and scores the resultant crosswords
# by minimizing white space
# `size` is the length and width of the crossword which was inputted by the user
# `numIter` is the amount of iterations of the random crossword generator to perform
# `play_layout` is the current layout to be displayed in the play_window with the graph element for the puzzle
# This function returns grid, positioned_words, word_numbers, clue_number_to_word_number, play_window:
# `grid` is the completed crossword with the words placed
# `positioned_words` is a dictionary mapping the word to (x, y, is_horizontal) which specifies the starting position
# of the word and the direction it was placed
# `word_numbers` is a dictionary mapping the number the word was assigned to the word
# `clue_number_to_word_number` is a mapping of the clue number which is determined by the play layout and the word number
# `play_window` is the window which includes the grid and the clues
def generate_crossword(size, numIter, play_layout):
    # clean words and create grid
    clues_dict, ranked_letters = generate.clean_words(size)
    grid = generate.create_grid(size)
    positioned_words = {}

    # run each algorithm and select one with the highest score
    grid1, positioned_words1 = generate.generate_puzzle_highest_ranked_first(size, generate.create_grid(size), clues_dict)
    positioned_words1 = generate.clean_placed_words(positioned_words1)
    grid1_score = generate.score_generated_minimize_whitespace(grid1)

    grid2, positioned_words2 = generate.generate_puzzle_highest_ranked_longest_first(size, generate.create_grid(size), clues_dict)
    positioned_words2 = generate.clean_placed_words(positioned_words2)
    grid2_score = generate.score_generated_minimize_whitespace(grid2)

    grid3 = [[]]
    positioned_words3 = {}
    highest_score = 0
    # create `numIter` random crosswords and select the highest scoring crossword
    for i in range(numIter):
        random_grid_temp, positioned_words_random_temp = generate.generate_puzzle_random_first_word(size, generate.create_grid(size), clues_dict)
        positioned_words_random_temp = generate.clean_placed_words(positioned_words_random_temp)
        score = generate.score_generated_minimize_whitespace(random_grid_temp)
        if score > highest_score:
            highest_score = score
            grid3 = random_grid_temp
            positioned_words3 = positioned_words_random_temp
    positioned_words3 = generate.clean_placed_words(positioned_words3)
    grid3_score = generate.score_generated_minimize_whitespace(grid3)

    grid4, positioned_words4 = generate.generate_puzzle_require_alternation(size, generate.create_grid(size), clues_dict)
    positioned_words4 = generate.clean_placed_words(positioned_words4)
    grid4_score = generate.score_generated_minimize_whitespace(grid4)

    grid5 = [[]]
    positioned_words5 = {}
    highest_score = 0
    # create `numIter` random crosswords and select the highest scoring crossword
    for i in range(numIter):
        random_grid_temp, positioned_words_random_temp = generate.generate_puzzle_require_alternation_random_first_word(size, generate.create_grid(size), clues_dict)
        positioned_words_random_temp = generate.clean_placed_words(positioned_words_random_temp)
        score = generate.score_generated_minimize_whitespace(random_grid_temp)
        if score > highest_score:
            highest_score = score
            grid5 = random_grid_temp
            positioned_words5 = positioned_words_random_temp
    positioned_words5 = generate.clean_placed_words(positioned_words5)
    grid5_score = generate.score_generated_minimize_whitespace(grid5)
    
    max_score = max(grid1_score, grid2_score, grid3_score, grid4_score, grid5_score)
    if grid5_score == max_score:
        grid = grid5
        positioned_words = positioned_words5
    elif grid3_score == max_score:
        grid = grid3
        positioned_words = positioned_words3
    elif grid4_score == max_score:
        grid = grid4
        positioned_words = positioned_words4
    elif grid1_score == max_score:
        grid = grid1
        positioned_words = positioned_words1
    else:
        grid = grid2
        positioned_words = positioned_words2
    # # if the grid created by selecting the highest ranked word had a higher score than the grid created by selecting 
    # # the highest ranked word of the words of maximum length
    # if (generate.score_generated_minimize_whitespace(grid1) > generate.score_generated_minimize_whitespace(grid2)): 
    #     # if the grid created by selecting the highest ranked word had a higher score than the random grid
    #     if (generate.score_generated_minimize_whitespace(grid1) > generate.score_generated_minimize_whitespace(random_grid)):
    #         grid = grid1
    #         positioned_words = positioned_words1
    #     else: 
    #         grid = random_grid
    #         positioned_words = positioned_words_random

    # # if the grid created by selecting the highest ranked word of the words of maximum length had a higher score than the grid 
    # # created by selecting the highest ranked word 
    # else: 
    #     # if the grid created by selecting the highest ranked word of the words of maximum length had a higher score than 
    #     # the random grid
    #     if (generate.score_generated_minimize_whitespace(grid2) > generate.score_generated_minimize_whitespace(random_grid)):
    #         grid = grid2
    #         positioned_words = positioned_words2
    #     else:
    #         grid = random_grid
    #         positioned_words = positioned_words_random

    # assign numbers to each word on the board
    word_numbers = create_word_numbers(size, grid, positioned_words)

    # generate and format clues on the play screen 
    clues = generate_clues(clues_dict, word_numbers, positioned_words)
    clue_number_to_word_number = format_clues(clues, play_layout)

    # create a new window for the play screen 
    play_window = sg.Window("Crossword", play_layout, size=(1000,1000), margins=(50, 50))
    play_window.Finalize()
    crossword = play_window['-CROSSWORD-']

    # draw the crossword on the new play window
    generate_grid(size, grid, positioned_words, crossword, word_numbers)
    generate.pretty_print(grid)
    print(positioned_words)

    return grid, positioned_words, word_numbers, clue_number_to_word_number, play_window
    

# Check the inputs of the user against the correct puzzle generated by the AI
# `positioned_words` is a dictionary mapping the word to (x, y, is_horizontal) which specifies the starting position
# of the word and the direction it was placed
# `correct_grid` is the completed crossword with the words placed
# `values` are the user's inputs to be checked
# `word_numbers` is a dictionary mapping the number the word was assigned to the word
# `clue_number_to_word_number` is a mapping of the clue number which is determined by the play layout and the word number
# `play_window` is the window which includes the grid and the clues
def check_puzzle(positioned_words, correct_grid, values, word_numbers, clue_number_to_word_number, play_window):
    crossword = play_window['-CROSSWORD-']
    generate_grid(len(correct_grid), correct_grid, positioned_words, crossword, word_numbers)
    del values['-CROSSWORD-']
    
    new_ids = []
    correct = True

    # has the grid been modified by user input
    modified = []
    for i in range(len(correct_grid)):
        row = []
        for j in range(len(correct_grid)):
            row.append(False)
        modified.append(row)

    # iterate over each user input
    for i in range(len(values)):
        word_number = clue_number_to_word_number[i] 
        for key in word_numbers:
            if word_numbers[key] == word_number:
                answer_word = key
        input_word = values[i].upper().replace(" ", "")
        x = positioned_words[answer_word][0]
        y = positioned_words[answer_word][1]
        horizontal = positioned_words[answer_word][2]

        # determine if the user inputted the answer
        if input_word != answer_word:
            correct = False

        # iterate over the letters in the shorter of the answer and the input word
        for j in range(min(len(answer_word), len(input_word))):
            # if the letter is incorrect, redraw rectange with red border otherwise draw a rectangle with black border
            if answer_word[j] != input_word[j]:
                crossword.draw_rectangle((x * BLOCK_SIZE + 5, y * BLOCK_SIZE + 3), (x * BLOCK_SIZE + BLOCK_SIZE + 5, y * BLOCK_SIZE + BLOCK_SIZE + 3), line_color='red', fill_color='white')
            else:
                crossword.draw_rectangle((x * BLOCK_SIZE + 5, y * BLOCK_SIZE + 3), (x * BLOCK_SIZE + BLOCK_SIZE + 5, y * BLOCK_SIZE + BLOCK_SIZE + 3), line_color='black', fill_color='white')

            # iterate over words in word numbers
            for word in word_numbers:
                # if current position is the start of a word, draw the word number
                if positioned_words[word][0] == x and positioned_words[word][1] == y:
                    crossword.draw_text('{}'.format(word_numbers[word]),(x * BLOCK_SIZE + 10, y * BLOCK_SIZE + 8))

            # place the letter and append the id of the draw_text to `new_ids`
            letter_loc = (x * BLOCK_SIZE + 18, y * BLOCK_SIZE + 17)
            new_ids.append(crossword.draw_text('{}'.format(input_word[j]), letter_loc, font='Courier 25'))
            modified[y][x] = True

            # if horizontal move right, else move down
            if horizontal:
                x += 1
            else:
                y += 1
        
        # if the user input was too short, mark all squares beyond the input red and make them blank
        if len(input_word) < len(answer_word):
            for j in range(len(answer_word) - len(input_word)):
                if horizontal and not modified[y][x+j]:
                    crossword.draw_rectangle(((x+j) * BLOCK_SIZE + 5, y * BLOCK_SIZE + 3), ((x+j) * BLOCK_SIZE + BLOCK_SIZE + 5, y * BLOCK_SIZE + BLOCK_SIZE + 3), line_color='red', fill_color='white')
                elif not horizontal and not modified[y+j][x]:
                    crossword.draw_rectangle((x * BLOCK_SIZE + 5, (y+j) * BLOCK_SIZE + 3), (x * BLOCK_SIZE + BLOCK_SIZE + 5, (y+j) * BLOCK_SIZE + BLOCK_SIZE + 3), line_color='red', fill_color='white')

            # redraw the word number if the grid square being redrawn has a word number
            for word in word_numbers:
                if positioned_words[word][0] == x and positioned_words[word][1] == y:
                    crossword.draw_text('{}'.format(word_numbers[word]),(x * BLOCK_SIZE + 10, y * BLOCK_SIZE + 8))

    # update the grid on the window
    play_window['-CROSSWORD-'].update()
    play_window.refresh()

    return new_ids, correct

# Remove all letters on the graph element of the crossword
# `ids` are the id of the draw_text elements currently on the crossword
def clear_puzzle(ids):
    crossword = play_window['-CROSSWORD-']
    for id in ids:
        crossword.delete_figure(id)

# Create the answer grid with all the correct letters to be shown on the end screen
# `size` is the length and width of the crossword which was inputted by the user
# `grid` is the completed crossword with the words placed
# `positioned_words` is a dictionary mapping the word to (x, y, is_horizontal) which specifies the starting position
# of the word and the direction it was placed
# `crossword` is the graph element to place the crossword on the window
# `word_numbers` is a dictionary mapping the number the word was assigned to the word
def generate_correct_grid(size, grid, positioned_words, crossword, word_numbers):
    # iterate over every block in the grid
    for y in range(size):
        for x in range(size):
            
            # if the block should have a letter
            if grid[y][x] != ' ' and grid[y][x] != '-':
                # create white text box and draw letter
                crossword.draw_rectangle((x * BLOCK_SIZE + 5, y * BLOCK_SIZE + 3), (x * BLOCK_SIZE + BLOCK_SIZE + 5, y * BLOCK_SIZE + BLOCK_SIZE + 3), line_color='black', fill_color='white')
                letter_loc = (x * BLOCK_SIZE + 18, y * BLOCK_SIZE + 17)
                crossword.draw_text('{}'.format(grid[y][x]), letter_loc, font='Courier 25')
                
                # add numbers to top left of block
                for word in word_numbers:
                    if positioned_words[word][0] == x and positioned_words[word][1] == y:
                        crossword.draw_text('{}'.format(word_numbers[word]),(x * BLOCK_SIZE + 10, y * BLOCK_SIZE + 8))
            
            # if the block should not have a letter
            else:
                # create black text box
                crossword.draw_rectangle((x * BLOCK_SIZE + 5, y * BLOCK_SIZE + 3), (x * BLOCK_SIZE + BLOCK_SIZE + 5, y * BLOCK_SIZE + BLOCK_SIZE + 3), line_color='black', fill_color='black')

def display_time(seconds):
    if seconds > 60:
        minutes, seconds = divmod(seconds, 60)
        return str(minutes) + ' minutes and ' + str(seconds) + ' seconds'
    else:
        return str(seconds) + ' seconds'

# start on the home screen
home_screen = True
end_screen = False
play_screen = False
exit_game = False
clue_number_to_word_number = {}
end_window = None

while True:
    window = sg.Window("Crossword", make_home_layout(), size=(1000,1000), margins=(50, 50), element_justification='c')

    while home_screen:
        event, values = window.read()
        if end_window != None:
            end_window.close()
        if event == sg.WIN_CLOSED or event == "-CLOSE HOME-" or event == '-CLOSE PLAY-':
            exit_game = True
            home_screen = False
            end_screen = False
            play_screen = False

        elif event == '-PLAY AGAIN-':
            window['-PLAY-'].update(visible=False)
            window['-INVALID SIZE-'].update(visible=False)
            window['-HOME-'].update(visible=True)
        elif event == '-PLAY BUTTON-':
            if not values[0].isnumeric():
                window["-INVALID SIZE-"].update(visible=True)
            elif values[0] == '':
                window["-INVALID SIZE-"].update(visible=True)
            else:
                size = int(values[0])
                if size < 4 or size > 15:
                    window["-INVALID SIZE-"].update(visible=True)
                else:
                    play_layout = make_play_layout()

                    # generate crossword with AI
                    grid, positioned_words, word_numbers, clue_number_to_word_number, play_window = generate_crossword(size, 5, play_layout)
                    
                    start_time = time.time()
                    window.close()
                    home_screen = False
                    play_screen = True
                    break

    ids = []

    while play_screen:
        event, values = play_window.read()
        if end_window != None:
            end_window.close()
        if event == sg.WIN_CLOSED or event == '-CLOSE PLAY-':
            exit_game = True
            home_screen = False
            end_screen = False
            play_screen = False
        elif event == '-CHECK PUZZLE-':
            clear_puzzle(ids)
            ids, correct = check_puzzle(positioned_words, grid, values, word_numbers, clue_number_to_word_number, play_window)

            # if puzzle was correct
            if correct:
                end_time = time.time()
                end_window = make_end_window(display_time(round(end_time - start_time)), word_numbers, grid, positioned_words)
                end_screen = True
                play_screen = False
                play_window.close()

        elif event == '-BACK TO HOME-':
            home_screen = True
            play_screen = False
            play_window.close()

    # end screen
    while end_screen:
        event, values = end_window.read()

        if event == sg.WIN_CLOSED or event == '-CLOSE END OF GAME-':
            exit_game = True
            home_screen = False
            end_screen = False
            play_screen = False
        elif event == '-BACK TO HOME-':
            end_screen = False
            play_screen = True
            home_screen = True
            break
    
    if exit_game:
        break