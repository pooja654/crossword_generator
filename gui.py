import PySimpleGUI as sg
import generate
import textwrap
import time

sg.theme('DarkAmber')

# Dummy Crossword Values Created for testing the GUI implementation
TEST_GRID = [['-','E','-','S'], [' ','A',' ','E'],['A','S','E','A'],[' ','E',' ','S']]
TEST_POSITIONED_WORDS = {'ASEA':(0, 2, True), 'EASE':(1, 0, False), 'SEAS':(3, 0, False)}
TEST_CLUES_DICT = {'ASEA':'this is the clue for asea', 'EASE':'this is the clue for ease', 'SEAS':'this is the clue for seas'}

# Static size of a singular squuare on crossword
BLOCK_SIZE = 25

# create the layout for the home screen with an introduction greetingn and a query for crossword size
def make_home_layout():
    return [
        [sg.Text("Hello from AI Crossword!", font=("Courier 25", 30), pad=(20, 20))],
        [sg.Text('Enter the size of your crossword (6 to 20):', font=("Courier 25", 20)), sg.InputText()],
        [sg.Button("Close", font=("Courier 25", 16), key='-CLOSE HOME-'), sg.Button("Make Crossword", font=("Courier 25", 16), key='-PLAY BUTTON-')],
        [sg.Text("INVALID SIZE, TRY AGAIN", key='-INVALID SIZE-', visible=False)]
    ]

# create the layout for the play screen with a graph element as the crossword grid. generate clues in a list format with
# text inputs to insert answers to the crossword
def make_play_layout():
    return [
        [sg.Text("Let's Play!", key='-START-')],
        [sg.Button("Close", key='-CLOSE PLAY-', visible=True), sg.Button("Back to Home", key='-BACK TO HOME-', visible=True)],
        [sg.Graph((500, 500), (0, 400), (400, 0), key='-CROSSWORD-',
                change_submits=True, drag_submits=False)]
    ]

# create the layout for the end screen 
def make_end_window(time_took, word_numbers):
    end_layout = [
            [sg.Text("Congratulations!")],
            [sg.Text("Time: " + time_took + " seconds")],
            [sg.Graph((500, 500), (0, 400), (400, 0), key='-CROSSWORD-',
                    change_submits=True, drag_submits=False)],
            [sg.Button("Close", key='-CLOSE END OF GAME-', visible=True), sg.Button("Back to Home", key='-BACK TO HOME-', visible=True)]
    ]
    end_window = sg.Window("End", end_layout, size=(1000,1000), margins=(50, 50), element_justification='c')
    end_window.Finalize()
    generate_correct_grid(len(TEST_GRID), TEST_GRID, TEST_POSITIONED_WORDS, end_window['-CROSSWORD-'], word_numbers)
    return end_window

clue_number_to_word_number = {}


def generate_clues(clues_dict, word_numbers, positioned_words):
    clues = {'Horizontal' : [], 'Vertical' : []}
    for word in word_numbers:
        clue = clues_dict[word]
        if positioned_words[word][2]:
            clues['Horizontal'].append((word_numbers[word], clue))
        else:
            clues['Vertical'].append((word_numbers[word], clue))
    return clues

def format_clues(clues, play_layout):
    horizontal = [[sg.Text('Across')]]
    vertical = [[sg.Text('Down')]]
    clue_number_to_word_number = {}
    clue_number = 0
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


def generate_grid(size, grid, positioned_words, crossword, word_numbers):
    for y in range(size):
        for x in range(size):
            # text box
            if grid[y][x] != ' ' and grid[y][x] != '-':
                # create white text box
                crossword.draw_rectangle((x * BLOCK_SIZE + 5, y * BLOCK_SIZE + 3), (x * BLOCK_SIZE + BLOCK_SIZE + 5, y * BLOCK_SIZE + BLOCK_SIZE + 3), line_color='black', fill_color='white')
                
                # add numbers to top left of block
                for word in word_numbers:
                    if positioned_words[word][0] == x and positioned_words[word][1] == y:
                        crossword.draw_text('{}'.format(word_numbers[word]),(x * BLOCK_SIZE + 10, y * BLOCK_SIZE + 8))
            # black space (no letter here)
            else:
                # create black text box
                crossword.draw_rectangle((x * BLOCK_SIZE + 5, y * BLOCK_SIZE + 3), (x * BLOCK_SIZE + BLOCK_SIZE + 5, y * BLOCK_SIZE + BLOCK_SIZE + 3), line_color='black', fill_color='black')


def generate_crossword(size, numIter, play_layout):
    clues_dict = generate.clean_words(size)
    grid = generate.create_grid(size)

    positioned_words = {}

    # run each algorithm and select one with the highest score
    grid1, positioned_words1 = generate.generate_puzzle_highest_ranked_first(size, generate.create_grid(size), clues_dict)
    positioned_words1 = generate.clean_placed_words(positioned_words1)

    grid2, positioned_words2 = generate.generate_puzzle_highest_ranked_longest_first(size, generate.create_grid(size), clues_dict)
    positioned_words2 = generate.clean_placed_words(positioned_words2)

    random_grid = [[]]
    positioned_words_random = {}
    highest_score = 0
    for i in range(numIter):
        random_grid_temp, positioned_words_random_temp = generate.generate_puzzle_random_first_word(size, generate.create_grid(size), clues_dict)
        positioned_words_random_temp = generate.clean_placed_words(positioned_words_random_temp)
        score = generate.score_generated(random_grid)
        if score > highest_score:
            highest_score = score
            random_grid = random_grid_temp
            positioned_words_random = positioned_words_random_temp

    if generate.score_generated(grid1) > generate.score_generated(grid2) and generate.score_generated(grid1) > generate.score_generated(random_grid):
        grid = grid1
        positioned_words = positioned_words1
    elif generate.score_generated(grid2) > generate.score_generated(grid1) and generate.score_generated(grid2) > generate.score_generated(random_grid):
        grid = grid2
        positioned_words = positioned_words2
    else:
        grid = random_grid
        positioned_words = positioned_words_random

    play_window = sg.Window("Crossword", play_layout, size=(1000,1000), margins=(50, 50))
    play_window.Finalize()
    crossword = play_window['-CROSSWORD-']

    word_numbers = create_word_numbers(size, grid, positioned_words)
    generate_grid(size, grid, positioned_words, crossword, word_numbers)
    clues = generate_clues(clues_dict, word_numbers, positioned_words)
    clue_number_to_word_number = format_clues(clues, play_layout)

    return grid, positioned_words, word_numbers, clue_number_to_word_number, play_window
    


def check_puzzle(positioned_words, correct_grid, values, word_numbers, clue_number_to_word_number, play_window):
    crossword = play_window['-CROSSWORD-']
    generate_grid(len(correct_grid), correct_grid, positioned_words, crossword, word_numbers)
    del values['-CROSSWORD-']
    new_ids = []
    correct = True
    for i in range(len(values)):
        # change name of the dictionary
        word_number = clue_number_to_word_number[i] 
        for key in word_numbers:
            if word_numbers[key] == word_number:
                answer_word = key
        input_word = values[i].upper()
        x = positioned_words[answer_word][0]
        y = positioned_words[answer_word][1]
        horizontal = positioned_words[answer_word][2]
        
        if input_word != answer_word:
            correct = False

        for j in range(min(len(answer_word), len(input_word))):
            if answer_word[j] != input_word[j]:
                # letter is incorrect, redraw rectange with red border
                crossword.draw_rectangle((x * BLOCK_SIZE + 5, y * BLOCK_SIZE + 3), (x * BLOCK_SIZE + BLOCK_SIZE + 5, y * BLOCK_SIZE + BLOCK_SIZE + 3), line_color='red', fill_color='white')
            else:
                crossword.draw_rectangle((x * BLOCK_SIZE + 5, y * BLOCK_SIZE + 3), (x * BLOCK_SIZE + BLOCK_SIZE + 5, y * BLOCK_SIZE + BLOCK_SIZE + 3), line_color='black', fill_color='white')

            for word in word_numbers:
                if positioned_words[word][0] == x and positioned_words[word][1] == y:
                    crossword.draw_text('{}'.format(word_numbers[word]),(x * BLOCK_SIZE + 10, y * BLOCK_SIZE + 8))

            letter_loc = (x * BLOCK_SIZE + 18, y * BLOCK_SIZE + 17)
            new_ids.append(crossword.draw_text('{}'.format(input_word[j]), letter_loc, font='Courier 25'))

            # if horizontal move right, else move down
            if horizontal:
                x += 1
            else:
                y += 1
        
        if len(input_word) < len(answer_word):
            for j in range(len(answer_word) - len(input_word)):
                crossword.draw_rectangle((x * BLOCK_SIZE + 5, y * BLOCK_SIZE + 3), (x * BLOCK_SIZE + BLOCK_SIZE + 5, y * BLOCK_SIZE + BLOCK_SIZE + 3), line_color='red', fill_color='white')

            for word in word_numbers:
                if positioned_words[word][0] == x and positioned_words[word][1] == y:
                    crossword.draw_text('{}'.format(word_numbers[word]),(x * BLOCK_SIZE + 10, y * BLOCK_SIZE + 8))


    play_window['-CROSSWORD-'].update()
    play_window.refresh()
    return new_ids, correct

def clear_puzzle(ids):
    crossword = play_window['-CROSSWORD-']
    for id in ids:
        crossword.delete_figure(id)


def generate_correct_grid(size, grid, positioned_words, crossword, word_numbers):
    for y in range(size):
        for x in range(size):
            # text box
            if grid[y][x] != ' ' and grid[y][x] != '-':
                # create white text box
                crossword.draw_rectangle((x * BLOCK_SIZE + 5, y * BLOCK_SIZE + 3), (x * BLOCK_SIZE + BLOCK_SIZE + 5, y * BLOCK_SIZE + BLOCK_SIZE + 3), line_color='black', fill_color='white')
                letter_loc = (x * BLOCK_SIZE + 18, y * BLOCK_SIZE + 17)
                crossword.draw_text('{}'.format(grid[y][x]), letter_loc, font='Courier 25')
                
                # add numbers to top left of block
                for word in word_numbers:
                    if positioned_words[word][0] == x and positioned_words[word][1] == y:
                        crossword.draw_text('{}'.format(word_numbers[word]),(x * BLOCK_SIZE + 10, y * BLOCK_SIZE + 8))
            # black space (no letter here)
            else:
                # create black text box
                crossword.draw_rectangle((x * BLOCK_SIZE + 5, y * BLOCK_SIZE + 3), (x * BLOCK_SIZE + BLOCK_SIZE + 5, y * BLOCK_SIZE + BLOCK_SIZE + 3), line_color='black', fill_color='black')

home_screen = True
end_screen = False
play_screen = False
exit_game = False

while True:
    window = sg.Window("Crossword", make_home_layout(), size=(1000,1000), margins=(50, 50), element_justification='c')

    while home_screen:
        event, values = window.read()
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
                if size < 4 or size > 20:
                    window["-INVALID SIZE-"].update(visible=True)
                else:
                    play_layout = make_play_layout()

                    # generate crossword with AI
                    grid, positioned_words, word_numbers, clue_number_to_word_number, play_window = generate_crossword(size, 5, play_layout)
                    # word_numbers = create_word_numbers(size, TEST_GRID, TEST_POSITIONED_WORDS)
                    # clues = generate_clues(TEST_CLUES_DICT, word_numbers, TEST_POSITIONED_WORDS)
                    # clue_number_to_word_number = format_clues(clues, play_layout)
                    
                    # open a new window here
                    # play_window = sg.Window("Crossword", play_layout, size=(1000,1000), margins=(50, 50))
                    # play_window.Finalize()
                    # crossword = play_window['-CROSSWORD-']
                    # generate_grid(size, grid, positioned_words, crossword, word_numbers)
                    # generate_grid(size, TEST_GRID, TEST_POSITIONED_WORDS, crossword, word_numbers)
                    
                    start_time = time.time()
                    window.close()
                    home_screen = False
                    play_screen = True
                    break

    ids = []

    while play_screen:
        event, values = play_window.read()
        if event == sg.WIN_CLOSED or event == '-CLOSE PLAY-':
            exit_game = True
            home_screen = False
            end_screen = False
            play_screen = False
        elif event == '-CHECK PUZZLE-':
            clear_puzzle(ids)
            ids, correct = check_puzzle(positioned_words, grid, values, word_numbers, clue_number_to_word_number, play_window)
            # ids, correct = check_puzzle(TEST_POSITIONED_WORDS, TEST_GRID, values, word_numbers, clue_number_to_word_number, ids)

            # if puzzle was correct
            if correct:
                end_time = time.time()
                end_window = make_end_window(str(end_time - start_time), word_numbers)
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