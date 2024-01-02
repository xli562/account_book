import json, threading
from PySide2.QtCore import QObject, Signal

# Setup mongo client
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
db = client.entries
collection = db.entries_collection

days_of_the_week = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']



save_settings = True   # For debugging only: set to True for customer machines.
sys_stngs_path = './files/system_settings/sys_stngs.json'
backup_sys_stngs_path = './files/system_settings/sys_stngs backup.json'



def sys_stng_interface(var_name, new_val=None, recalculate:tuple=None):
    ''' Read/write data from/to sys_stngs.json, so that the 
    machine remembers its settings when powered off.
    Execution time: 0-0.001s on the Windows machine.
    
    recalculate: recalculates a value dependant on other sys stngs.
    eg var_name = deflt_times, recalculate = ('empty', empty_times()[current_rv()])'''
    with open(sys_stngs_path, 'r') as f:
        settings = json.load(f)

    if new_val == None:
        # Update a value as necessary.
        if recalculate != None:
            recalc_key = recalculate[0]
            recalc_val = recalculate[1]
            settings[var_name][recalc_key] = recalc_val

        return settings[var_name]
    else:
        settings[var_name] = new_val
        with open(sys_stngs_path, 'w') as f:
            json.dump(settings, f, indent=4)


# List of accounts
def accnts(new_val=None):
    ''' eg ['HSBC(7476)', '微信零钱', '现金'] '''
    return sys_stng_interface('accnts', new_val)
accnts(collection.distinct('account'))

# List of currencies
def currs(new_val=None):
    ''' eg ['CNY', 'GBP', 'EUR'] '''
    return sys_stng_interface('currs', new_val)
currs(collection.distinct('currency'))



class AutoCompletionHelper():
    '''enabes vscode to autocomplete names while typing'''
    
    # Basic operations
    nop = 'nop'
    purge = 'purge'

    pressurise = 'pressurise'
    depressurise = 'depressurise'
    prime_bottles = 'prime_bottles'

    vent_wash = 'vent_wash'
    mix = 'mix'
    empty = 'empty'
    add_fluid = 'add_fluid'
    flush = 'flush'

    start_block = 'start_block'
    end_block = 'end_block'
    wait_for_aa = 'wait_for_aa'

    # Composite operations
    wash_rv = 'wash_rv'
    clean_machine = 'clean_machine'
    deprotect = 'deprotect'
    manual_mix = 'manual_mix'
    cleave = 'cleave'

    # Parameters for operations
    volume = 'volume'
    bottle = 'bottle'
    mix_for = 'mix_for'
    empty_for = 'empty_for'
    empty_to = 'empty_to'
    heat_to = 'heat_to'
    repeat = 'repeat'
    wash_uv_line = 'wash_uv_line'

    # Running status
    running = 'running'
    paused = 'paused'
    finished = 'finished'
    aborted = 'aborted'

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(AutoCompletionHelper, cls).__new__(cls, *args, **kwargs)

        return cls._instance
d = AutoCompletionHelper()



# Default time constants. The synthesis will by default use these times in protocols and manual commands.
def empty_times(new_val=None):
    ''' eg [7, 20, 30] '''
    return sys_stng_interface('empty_times', new_val)



class GoToSignal(QObject):
    '''A global signal that can be passed between classes,
    to tell the main statcked layout to display the active window.
    Only one instance of this class can ever be created, 
    to make sure the same signal is used in the whole program.'''
    sig = Signal()    # 1st str is src, 2nd str is dest

    # make sure only one instance is ever created
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(GoToSignal, cls).__new__(cls, *args, **kwargs)

        return cls._instance
goto_sig = GoToSignal()

navigation_info = {'src_page':'', 'dest_page':'', 'ret_to_page':'', 'src_btn':''}
page_stack = ['home'] # A bit similar to the call stack of a program's functions.



class PageReady(QObject):
    '''For synchronisation.
    Emitted when the next page is loaded by the EmptyFrameBackground.'''
    sig = Signal()    # 1st str is src, 2nd str is dest

    # make sure only one instance is ever created
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(PageReady, cls).__new__(cls, *args, **kwargs)

        return cls._instance
page_ready = PageReady()