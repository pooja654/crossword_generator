import PySimpleGUI as sg
import generate

BLOCK_SIZE = 25

home_layout = [
    [sg.Text("Hello from Crossword")],
    [sg.Text('Enter the size of your crossword (6 to 20)'), sg.InputText()],
    [sg.Button("Make Crossword", key='-PLAY BUTTON-')],
    [sg.Button("Close", key='-CLOSE HOME-')],
    [sg.Text("INVALID SIZE, TRY AGAIN", key='-INVALID SIZE-', visible=False)]
]

play_layout = [
    [sg.Text("Let's Play!", key='-KEY-')],
    [sg.Graph((100, 100), (0, 450), (450, 0), key='-CROSSWORD-',
              change_submits=True, drag_submits=False)],
    [sg.Button("Close", key='-CLOSE PLAY-'), sg.Button("Play Again", key='-PLAY AGAIN-')]
]

# pasted--------
col_layout = [
    # [sg.Input(size=(0, 0), key='box')],
]

layout = [[sg.pin(sg.Column(home_layout, key='-HOME-', size=(300, 300))),
            sg.pin(sg.Column(play_layout, key='-PLAY-', visible=False)),
            sg.Column(col_layout, key="-PLAY-", element_justification='c', expand_x=True)]]

window = sg.Window("Crossword", layout, margins=(300,300))
crossword = window['-CROSSWORD-']

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
    print(clues)
    horizontal = [sg.Text('Across')]
    vertical = [sg.Text('Down')]
    for i in range(len(clues['Horizontal'])):
        horizontal.append(sg.Text(str(clues['Horizontal'][i][0]) + '. ' + clues['Horizontal'[i][1]]))
    for i in range(len(clues['Vertical'])):
        vertical.append(sg.Text(str(clues['Vertical'][i][0]) + '. ' + clues['Vertical'[i][1]]))
    play_layout.append([sg.Column([horizontal], element_justification='c'), sg.Column([vertical], element_justification='c')])


def generate_grid(size, grid, positioned_words):
    word_numbers = {}
    for y in range(size):
        for x in range(size):
            # text box
            if grid[y][x] != ' ' and grid[y][x] != '-':
                # create white text box
                crossword.draw_rectangle((x * BLOCK_SIZE + 5, y * BLOCK_SIZE + 3), (x * BLOCK_SIZE + BLOCK_SIZE + 5, y * BLOCK_SIZE + BLOCK_SIZE + 3), line_color='black')
                # add input text
                col_layout.append(sg.Input(size=(BLOCK_SIZE, BLOCK_SIZE)))
                
                # add numbers to top left of block
                # fix numbers
                for key in positioned_words.keys():
                    if positioned_words[key] == (x, y, True) or positioned_words[key] == (x, y, False):
                        if key not in word_numbers:
                            number = len(word_numbers) + 1
                            word_numbers[key] = number
                            crossword.draw_text('{}'.format(number),(x * BLOCK_SIZE + 10, y * BLOCK_SIZE + 8))
            # black space (no letter here)
            else:
                # create black text box
                crossword.draw_rectangle((x * BLOCK_SIZE + 5, y * BLOCK_SIZE + 3), (x * BLOCK_SIZE + BLOCK_SIZE + 5, y * BLOCK_SIZE + BLOCK_SIZE + 3), line_color='black', fill_color='black')
    return word_numbers

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == "-CLOSE HOME-" or event == '-CLOSE PLAY-':
        break
    elif event == '-PLAY AGAIN-':
        window['-PLAY-'].update(visible=False)
        window['-INVALID SIZE-'].update(visible=False)
        window['-HOME-'].update(visible=True)
    elif event == '-PLAY BUTTON-':
        size = int(values[0])
        if size < 4 or size > 20:
            window["-INVALID SIZE-"].update(visible=True)
        else:
            window['-HOME-'].update(visible=False)
            grid, clues_dict = generate.clean_words_create_grid(size)
            grid, positioned_words = generate.generate_puzzle_highest_ranked_first(size, grid, clues_dict)
            positioned_words = generate.clean_placed_words(positioned_words)
            word_numbers = generate_grid(size, grid, positioned_words)
            # clues = generate_clues(clues_dict, word_numbers, positioned_words)
            # format_clues(clues)
            window['-PLAY-'].update(visible=True)       
    
window.close()
