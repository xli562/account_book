from modules import constants


def colour_print(colour:str, text:str, to_screen=False):
    '''prints with colour'''
    text = str(text)
    if to_screen == True:
        constants.print_sig.sig.emit(text)
    if colour == 'orange':
        print('\033[38;5;202m'+text+'\033[0m')
    if colour == 'light blue':
        print('\033[94m'+text+'\033[0m')
    if colour == 'magenta':
        print('\033[35m'+text+'\033[0m')
    if colour == 'pink':
        print('\033[95m'+text+'\033[0m')
    if colour == 'yellow':
        print('\033[33m'+text+'\033[0m')