import PySimpleGUI as sg

home_layout = [
    [sg.Text("Hello from Crossword", key='-HOME-')],
    [sg.Text('Enter the size of your crossword (6 to 20)', key='-HOME-'), sg.InputText(key='-HOME-')],
    [sg.Button("Make Crossword", key='-HOME-')],
    [sg.Button("Close", key='-HOME-')]
]

window = sg.Window(title='hello', layout=home_layout, margins=(100,50))

while True: 
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break

window.close()