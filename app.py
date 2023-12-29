import os, sys, time, json, copy, subprocess, glob, shutil
from datetime import *

from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import *
from PySide2.QtGui import QPixmap, QFontDatabase


from modules.functional_convenience import *
from modules import constants
from gui_modules.page_elements_setup import *



# Global variables in the scope of app.py
# To save typing constants.xxx every time.
goto_sig = constants.goto_sig
page_ready = constants.page_ready
d = constants.d


QResource.registerResource('resources_rc.rcc')


def navigate(src_page:str, dest_page:str, ret_to_page:str, src_btn:str, extras:dict=None):
    '''Emits signal to navigate to new page
    modifies constants.navigation_info, 
    with the option to pass extra temporary arguments.'''

    constants.navigation_info = {'src_page':src_page, 
                                 'dest_page':dest_page, 
                                 'ret_to_page':ret_to_page, 
                                 'src_btn':src_btn}
    
    constants.page_stack.append(dest_page)
    if len(constants.page_stack) >= 3:
        if dest_page in constants.page_stack:
            index = constants.page_stack.index(dest_page)
            del constants.page_stack[index+1:]
    
    if type(extras) == dict:
        for key, value in extras.items():
            constants.navigation_info[key] = value
    constants.goto_sig.sig.emit()


def navigate_back(src_page, ret_to_page, src_btn, extras:dict=None):
    navigate(src_page, constants.page_stack[-2], ret_to_page, src_btn, extras)





# =============== The pages =============== #




class home(QWidget):
    ''' The home page which shows upon opening of app.
        Input: Initial page.
        Output: Buttons navigate to different pages.
                No data output.
    '''
    def __init__(self):
        super().__init__()
        self.name = 'home'
        self.init_variables()
        self.init_ui()
        self.connecting_dots()

    def __new__(cls, *args, **kwargs):
        '''Make sure only one instance is ever created.'''
        if not hasattr(cls, '_instance'):
            cls._instance = super(home, cls).__new__(cls, *args, **kwargs)
        return cls._instance



    def init_variables(self):
        ''' Initialises pages and the input buffer. '''
        self.pages = {'entrs':entrs(),
                      'stats':stats()}



    def init_ui(self):
        loader = QUiLoader()
        file = QFile('./ui/home.ui')
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self)
        file.close()

        layout = QVBoxLayout(self)
        layout.addWidget(self.ui)


        self.nav_btn_group = QButtonGroup(self.ui)  # Bottom navigation button group
        self.nav_btn_group.addButton(self.ui.entrs_rbtn)
        self.nav_btn_group.addButton(self.ui.stats_rbtn)
        self.nav_btn_group.addButton(self.ui.disc_rbtn)
        self.nav_btn_group.addButton(self.ui.my_rbtn)


        for page_name, page in self.pages.items():
            self.ui.home_stacked_widget.addWidget(page.ui)
        
        # Default display the Entries page
        self.ui.home_stacked_widget.setCurrentWidget(self.pages.get('entrs').ui)



    def connecting_dots(self):
        '''connecting signals and slots'''
        self.ui.entrs_rbtn.clicked.connect(lambda:
                self.ui.home_stacked_widget.setCurrentWidget(self.pages.get('entrs').ui))
        self.ui.stats_rbtn.clicked.connect(lambda:
                self.ui.home_stacked_widget.setCurrentWidget(self.pages.get('stats').ui))




class entrs(QWidget):
    ''' Entries, 明细页。
        Input: 
        Output:
    '''
    def __init__(self):
        super().__init__()
        self.name = 'entrs'
        self.init_variables()
        self.init_ui()
        self.connecting_dots()
    
    def __new__(cls, *args, **kwargs):
        '''Make sure only one instance is ever created.'''
        if not hasattr(cls, '_instance'):
            cls._instance = super(entrs, cls).__new__(cls, *args, **kwargs)
        return cls._instance



    def init_variables(self):
        ''' Initialises pages and/or the input buffer. '''
        self.inputs = {'accnts':constants.accnts}

        def calculate_sums() -> dict:
            ''' 计算并以字典形式返回账户及其对应收支 '''
            for accnt in self.inputs.get('accnts'):
                summing_pipeline = [
                    {
                        "$match": {
                            "account": accnt,
                            "transaction_type": "收入"
                        }
                    },  # Match documents with 'account'='HSBC' and 'transaction_type'='income'
                    {
                        "$group": {
                            "_id": None,
                            "total_amount": {"$sum": "$amount"}
                        }
                    }  # Sum the 'amount' for matched documents
                ]
                # Perform aggregation
                result = constants.db.entries_collection.aggregate(summing_pipeline)

                # Print the result
                for doc in result:
                    print(f"Total amount: {doc['total_amount']}")
                # total_amounts = {}
                # for doc in result:
                #     total_amounts[1] = doc['total_amount']
                # return total_amounts
        self.cache = {
            'total_amounts':{}}


    def init_ui(self):
        loader = QUiLoader()
        file = QFile(f'./ui/entrs/{self.name}.ui')
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self)
        file.close()


        # Add a rbtn for each account
        self.accnt_rbtns = []
        self.accnts_btn_group = QButtonGroup(self.ui)     # Accounts button group
        self.accnts_btn_group.addButton(self.ui.accnt_0_rbtn, 0)
        i = 0
        for accnt in self.inputs.get('accnts'):
            i += 1
            accnt_rbtn = QRadioButton(accnt)
            accnt_rbtn.setObjectName(f'accnt_{i}_rbtn')
            self.accnt_rbtns.append(accnt_rbtn)
            self.ui.accnt_rbtns_hbox.addWidget(accnt_rbtn)
            self.accnts_btn_group.addButton(accnt_rbtn, i)


        # Initialise the scroll areas for the entries
        self.scroll_areas = []
        self.scroll_containers = []
        self.entries_vboxes = []
        for i in range(len(self.inputs.get('accnts'))+1):   # '+1' to accommodate the overall view.
            scroll_area = QScrollArea(self.ui.entrs_stacked_widget)
            scroll_area.setObjectName(f'scroll_area{i}')
            self.scroll_areas.append(scroll_area)

            scroll_container = QWidget(scroll_area)
            scroll_container.setObjectName(f'scroll_container_{i}')
            self.scroll_containers.append(scroll_container)

            entries_vbox = QVBoxLayout(scroll_container)
            entries_vbox.setObjectName(f'scrolled_vbox_{i}')
            self.entries_vboxes.append(entries_vbox)

            self.ui.entrs_stacked_widget.addWidget(scroll_area)

            self.refresh_scroll_area(i)
        self.ui.entrs_stacked_widget.setCurrentWidget(self.scroll_areas[0])



    def refresh_scroll_area(self, accnt_index, year_index=datetime.now().year, month_index=datetime.now().month):
        ''' Refresh the scrolled widgets. 
            accnt_index: index of the target account, as stored in constants.accnts
            accnt_index = 0 for all_accounts-view.'''
        self.scroll_containers[accnt_index].destroy()
        self.scroll_containers[accnt_index] = QWidget()
        self.entries_vboxes[accnt_index] = QVBoxLayout(self.scroll_containers[accnt_index])

        def find_entrs(account, year, month) -> list:
            ''' Finds entries for a given account within a natural month. 
                Returns a list of documents. '''
            # Start and end dates for the month
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1)  # Handle December case
            else:
                end_date = datetime(year, month + 1, 1)

            # Query for documents with the specified account and date range
            if account is None:
                query = {"date": {"$gte": start_date, "$lt": end_date}}
            else:
                query = {
                    "account": account,
                    "date": {"$gte": start_date, "$lt": end_date}
                }

            return list(constants.collection.find(query))

        if accnt_index == 0:
            entries = find_entrs(None, year_index, month_index)
        else:
            entries = find_entrs(self.inputs.get('accnts')[accnt_index-1], year_index, month_index)
        entries.reverse()   # Reverse the list of entries so that it's in time descending order

        # Populate the rows
        entry_date = datetime(3000,1,1)
        ROW_HEIGHT = 50
        for entry in entries:
            if entry_date > entry.get('date'):
                entry_date = entry.get('date')
                row = RowWidget([f'{entry_date.month}月{entry_date.day}日 {constants.days_of_the_week[entry_date.weekday()]}'], (ROW_HEIGHT, 500), 2, self)
                self.entries_vboxes[accnt_index].addWidget(row)

            entry_category = entry.get('category')
            entry_remarks = entry.get('remarks')
            entry_amount = entry.get('amount') * -(entry.get('transaction_type') == '支出')
            row = RowWidget([entry_category, entry_remarks, entry_amount], (ROW_HEIGHT, 100, 500, 100), 1, self)
            self.entries_vboxes[accnt_index].addWidget(row)
        self.entries_vboxes[accnt_index].setSpacing(0)

        self.scroll_areas[accnt_index].update()

        self.scroll_areas[accnt_index].setWidgetResizable(True)
        self.scroll_areas[accnt_index].setWidget(self.scroll_containers[accnt_index])





    def connecting_dots(self):
        page_ready.sig.connect(self.on_page_load)
        def on_accnts_btn_group_click():
            btn_id = self.accnts_btn_group.checkedId()
            self.ui.entrs_stacked_widget.setCurrentWidget(self.scroll_areas[btn_id])

            # Update 收支数字显示
            def sum_income_expenditure(account, year=datetime.now().year, month=datetime.now().month):
                ''' Copied from ChatGPT. Works well. '''
                # Start and end dates for the month
                start_date = datetime(year, month, 1)
                end_date = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)

                # Base query
                base_query = {"date": {"$gte": start_date, "$lt": end_date}}
                if account is not None:
                    base_query["account"] = account

                # Aggregation pipeline
                pipeline = [
                    {"$match": base_query},
                    {"$group": {
                        "_id": "$transaction_type",
                        "total": {"$sum": "$amount"}
                    }}
                ]

                # Perform aggregation
                result = constants.collection.aggregate(pipeline)

                # Initialize sums
                income_sum = 0
                expenditure_sum = 0

                # Calculate sums
                for entry in result:
                    if entry["_id"] == "收入":  # Assuming "收入" is the identifier for income
                        income_sum = entry["total"]
                    elif entry["_id"] == "支出":  # Assuming "支出" is the identifier for expenditure
                        expenditure_sum = entry["total"]

                return income_sum, expenditure_sum
            accnt = None if btn_id == 0 else self.inputs.get('accnts')[btn_id - 1]
            income, expenditure = sum_income_expenditure(accnt)
            self.ui.incomes_btn.setText(f'收入\n{income}')
            self.ui.expenditures_btn.setText(f'支出\n{expenditure}')

        self.accnts_btn_group.buttonClicked.connect(on_accnts_btn_group_click)
    
    

    def on_page_load(self):
        if constants.navigation_info.get('dest_page') == self.name:
            pass




class stats(QWidget):
    ''' Statistics and chatrs, 统计信息与图表。
        Input: 
        Output:
    '''
    def __init__(self):
        super().__init__()
        self.name = 'stats'
        self.init_ui()
        self.connecting_dots()
    
    def __new__(cls, *args, **kwargs):
        '''Make sure only one instance is ever created.'''
        if not hasattr(cls, '_instance'):
            cls._instance = super(stats, cls).__new__(cls, *args, **kwargs)
        return cls._instance



    def init_ui(self):
        loader = QUiLoader()
        file = QFile(f'./ui/stats/{self.name}.ui')
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self)
        file.close()



    def connecting_dots(self):
        page_ready.sig.connect(self.on_page_load)
    
    

    def on_page_load(self):
        if constants.navigation_info.get('dest_page') == self.name:
            pass   







class EmptyFrameBackground(QWidget):
    '''An empty QWidget to put all of the windows upon.
    Switching between windows is achieved by 
    hiding / showing child windows (ie widgets).'''
    def __init__(self):
        super().__init__()
        self.init_variables()
        self.init_ui()
        self.connecting_dots()
    
    def __new__(cls, *args, **kwargs):
        '''Make sure only one instance is ever created.'''
        if not hasattr(cls, '_instance'):
            cls._instance = super(EmptyFrameBackground, cls).__new__(cls, *args, **kwargs)
        return cls._instance


    def init_variables(self):
        self.pages = {'home':home()}
        

    def init_ui(self):
        self.setFixedSize(1000, 1200)
        self.base_stacked_layout = QStackedLayout(self)

        self.setWindowTitle('Account Book')

        for page_name, page in self.pages.items():
            self.base_stacked_layout.addWidget(page.ui)


        self.base_stacked_layout.setCurrentWidget(self.pages.get('home').ui)
        constants.page_ready.sig.emit()



    def connecting_dots(self):
        goto_sig.sig.connect(self.goto)


    def goto(self):
        nav = constants.navigation_info
        dest = nav.get('dest_page')

        for page_name, page in self.pages.items():
            if dest == page_name:
                self.base_stacked_layout.setCurrentWidget(page.ui)

                colour_print('pink', '\n==================== Page loaded ====================')
                colour_print('pink', f"src_page = {nav.get('src_page')}, dest_page = {nav.get('dest_page')}, ret_to_page = {nav.get('ret_to_page')}, src_btn = {nav.get('src_btn')}")
                colour_print('pink', f'Full info: {nav}')
                colour_print('pink', f'Page stack: {constants.page_stack}')
                colour_print('yellow', f'Flags: pause request={constants.pause_request.is_set()}, last_input_ckecked={constants.last_ledit_input_checked}\n')

                
                break   # Stop the search for the target page if the target page is found
        constants.page_ready.sig.emit()




if __name__ == '__main__':
    app = QApplication(sys.argv)

    with open('./ui/styles.css', 'r') as f:
        app.setStyleSheet(f.read())

    window = EmptyFrameBackground()
    window.show()

    app.exec_()

    # Revert to the backup settings if needed.
    if constants.save_settings == False:

        # Read from source JSON file
        with open(constants.backup_sys_stngs_path, 'r') as source_file:
            data = json.load(source_file)

        # Write to destination JSON file
        with open(constants.sys_stngs_path, 'w') as destination_file:
            json.dump(data, destination_file, indent=4)