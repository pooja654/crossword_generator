import PySimpleGUI as sg
import generate

TEST_GRID = [['-','E','-','S'], [' ','A',' ','E'],['A','S','E','A'],[' ','E',' ','S']]
TEST_POSITIONED_WORDS = {'ASEA':(0, 2, True), 'EASE':(1, 0, False), 'SEAS':(3, 0, False)}

BLOCK_SIZE = 25

home_layout = [
    [sg.Text("Hello from Crossword")],
    [sg.Text('Enter the size of your crossword (6 to 20)'), sg.InputText()],
    [sg.Button("Make Crossword", key='-PLAY BUTTON-')],
    [sg.Button("Close", key='-CLOSE HOME-')],
    [sg.Text("INVALID SIZE, TRY AGAIN", key='-INVALID SIZE-', visible=False)]
]

across = [[sg.Text('Across')]]
down = [[sg.Text('Down')]]

play_layout = [
    [sg.Text("Let's Play!", key='-KEY-')],
    [sg.Button("Close", key='-CLOSE PLAY-', visible=True), sg.Button("Play Again", key='-PLAY AGAIN-', visible=True)],
    [sg.Graph((500, 500), (0, 400), (400, 0), key='-CROSSWORD-',
              change_submits=True, drag_submits=False)]
    # [sg.Column(across, element_justification='c'), sg.Column(down, element_justification='c')]
]

# pasted--------
col_layout = [
    # [sg.Input(size=(0, 0), key='box')],
]

# layout = [[sg.pin(sg.Column(home_layout, key='-HOME-', size=(300, 300))),
#             sg.pin(sg.Column(play_layout, key='-PLAY-', size=(300, 300), visible=False)),
#             sg.Column(col_layout, key="-PLAY-", element_justification='c', expand_x=True)]]

window = sg.Window("Crossword", home_layout, size=(1000,1000), margins=(50, 50))

def generate_clues(clues_dict, word_numbers, positioned_words):
    clues = {'Horizontal' : [], 'Vertical' : []}
    for word in word_numbers:
        clue = clues_dict[word]
        if positioned_words[word][2]:
            clues['Horizontal'].append((word_numbers[word], clue))
        else:
            clues['Vertical'].append((word_numbers[word], clue))
    return clues

def format_clues(clues):
    horizontal = [sg.Text('Across')]
    vertical = [sg.Text('Down')]
    for i in range(len(clues['Horizontal'])):
        horizontal.append(sg.Text(str(clues['Horizontal'][i][0]) + '. ' + clues['Horizontal'][i][1]))
    for i in range(len(clues['Vertical'])):
        vertical.append(sg.Text(str(clues['Vertical'][i][0]) + '. ' + clues['Vertical'][i][1]))
    # across += [horizontal]
    # down += [vertical]
    play_layout.append([sg.Column([horizontal], element_justification='c'), sg.Column([vertical], element_justification='c')])

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
                crossword.draw_rectangle((x * BLOCK_SIZE + 5, y * BLOCK_SIZE + 3), (x * BLOCK_SIZE + BLOCK_SIZE + 5, y * BLOCK_SIZE + BLOCK_SIZE + 3), line_color='black')
                # add input text
                col_layout.append(sg.InputText(size=(BLOCK_SIZE, BLOCK_SIZE)))
                
                # add numbers to top left of block
                for word in word_numbers:
                    if positioned_words[word][0] == x and positioned_words[word][1] == y:
                        crossword.draw_text('{}'.format(word_numbers[word]),(x * BLOCK_SIZE + 10, y * BLOCK_SIZE + 8))
            # black space (no letter here)
            else:
                # create black text box
                crossword.draw_rectangle((x * BLOCK_SIZE + 5, y * BLOCK_SIZE + 3), (x * BLOCK_SIZE + BLOCK_SIZE + 5, y * BLOCK_SIZE + BLOCK_SIZE + 3), line_color='black', fill_color='black')

def generate_crossword(size, numIter):
    grid, clues_dict = generate.clean_words_create_grid(size)

    # run each algorithm and select one with the highest score
    grid1, positioned_words1 = generate.generate_puzzle_highest_ranked_first(size, grid, clues_dict)
    positioned_words1 = generate.clean_placed_words(positioned_words1)

    grid2, positioned_words2 = generate.generate_puzzle_highest_ranked_longest_first(size, grid, clues_dict)
    positioned_words2 = generate.clean_placed_words(positioned_words2)

    random_grid = [[]]
    positioned_words_random = {}
    highest_score = 0
    for i in range(numIter):
        random_grid_temp, positioned_words_random_temp = generate.generate_puzzle_random_first_word(size, grid, clues_dict)
        positioned_words_random_temp = generate.clean_placed_words(positioned_words_random_temp)
        score = generate.score_generated(random_grid)
        if score > highest_score:
            highest_score = score
            random_grid = random_grid_temp
            positioned_words_random = positioned_words_random_temp

    if generate.score_generated(grid1) > generate.score_generated(grid2) and generate.score_generated(grid1) > generate.score_generated(random_grid):
        pass        

    word_numbers = generate_grid(size, grid, positioned_words)
    clues = generate_clues(clues_dict, word_numbers, positioned_words)
    format_clues(clues)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == "-CLOSE HOME-" or event == '-CLOSE PLAY-':
        break
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
                grid, clues_dict = generate.clean_words_create_grid(size)
                # grid, positioned_words = generate.generate_puzzle_highest_ranked_first(size, grid, clues_dict)
                # positioned_words = generate.clean_placed_words(positioned_words)
                # crossword = play_layout[2][0]
                word_numbers = create_word_numbers(size, TEST_GRID, TEST_POSITIONED_WORDS)
                clues = generate_clues(clues_dict, word_numbers, TEST_POSITIONED_WORDS)
                format_clues(clues)
                
                # open a new window here
                play_window = sg.Window("Crossword", play_layout, size=(1000,1000), margins=(50, 50))
                play_window.Finalize()
                crossword = play_window['-CROSSWORD-']
                generate_grid(size, TEST_GRID, TEST_POSITIONED_WORDS, crossword, word_numbers)
                # 
                window.close()
                break


                # generate_crossword(size, 5)
                # window['-PLAY-'].update(visible=True)       

while True:
    event, values = play_window.read()
    if event == sg.WIN_CLOSED or event == '-CLOSE PLAY-':
        break

play_window.close()