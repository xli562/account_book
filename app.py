import os, sys, time, json, copy, subprocess, glob, shutil
import datetime as dt

from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import *
from PySide2.QtGui import QPixmap, QFontDatabase


from modules.functional_convenience import *
from modules import constants
from gui_modules.page_elements_setup import *
from gui_modules.convenience_functions import *



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
        self.inputs = {
            'accnts':constants.accnts(),
            'currs':constants.currs()}
        self.cache = {
            'month_sels':{
                accnt:dt.datetime.now().date() for accnt in self.inputs.get('accnts')
            },
            'curr':'CNY',
            'accnt':None,
            'total_amounts':{}}
        self.cache['month_sels'][None] = dt.datetime.now().date()



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
        self.accnts_btn_group.button(0).setChecked(True)
        i = 0
        for accnt in self.inputs.get('accnts'):
            i += 1
            accnt_rbtn = QRadioButton(accnt)
            accnt_rbtn.setObjectName(f'accnt_{i}_rbtn')
            self.accnt_rbtns.append(accnt_rbtn)
            self.ui.accnt_rbtns_hbox.addWidget(accnt_rbtn)
            self.accnts_btn_group.addButton(accnt_rbtn, i)

        # Add a rbtn for each currency
        self.curr_rbtns = []
        self.currs_btn_group = QButtonGroup(self.ui)
        i = 0
        for curr in self.inputs.get('currs'):
            curr_rbtn = QRadioButton(curr)
            curr_rbtn.setObjectName(f'curr_{i}_rbtn')
            self.curr_rbtns.append(curr_rbtn)
            self.ui.curr_hbox.addWidget(curr_rbtn)
            self.currs_btn_group.addButton(curr_rbtn, i)
            i += 1
        self.currs_btn_group.button(0).setChecked(True)

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

        self.set_widget_states_to_default()

        self.update_sel_month_btn_text()
        self.update_income_expenditure_display()



    def refresh_scroll_area(self, accnt_index, year_index=None, month_index=None):
        ''' Refresh the scrolled widgets. 
            accnt_index: index of the target account, as stored in constants.accnts
            accnt_index = 0 for all_accounts-view.'''
        # The account name, as a string | None.
        if accnt_index == 0:
            accnt = None
        else:
            accnt = self.inputs.get('accnts')[accnt_index-1]
        
        # Initialise the year and month indices
        year_index = self.cache.get('month_sels').get(accnt).year if year_index is None else year_index
        month_index = self.cache.get('month_sels').get(accnt).month if month_index is None else month_index

        # Delete the old scroll area
        self.scroll_containers[accnt_index].destroy()
        self.scroll_containers[accnt_index] = QWidget()
        self.entries_vboxes[accnt_index] = QVBoxLayout(self.scroll_containers[accnt_index])

        def get_entrs_for_a_month(account:str, year, month) -> list:
            ''' Finds entries for a given account within a natural month. 
                Returns a list of documents. '''
            # Start and end dates for the month
            start_date, end_date = start_and_end_of_month(dt.datetime(year, month, 1))

            # Query for documents with the specified account and date range
            if account is None:
                query = {"date": {"$gte": start_date, "$lte": end_date}}
            else:
                query = {
                    "account": account,
                    "date": {"$gte": start_date, "$lte": end_date}
                }

            return list(constants.entries_collection.find(query))

        entries = get_entrs_for_a_month(accnt, year_index, month_index)

        # Sort entries in time descending order 
        def getdate(ditn):
            return ditn.get('date')
        entries.sort(key=getdate, reverse=True)

        # Preparations before populating the rows
        entry_date = dt.datetime(3000,1,1)
        ROW_HEIGHT = 50

        # Find the monthly balance in the database for this month, else we would need to do this in every iteration.
        # The monthly balance of a month is the balance at month's start.
        query = {'month': dt.datetime(year_index, month_index, 1)}
        monthly_balances:dict = constants.monthly_balances.find_one(query).get('balances')


        if accnt is None:
            monthly_balance = 0
            exchange_rates = entries[0].get('exchange_rates')
            for accnt, balance in monthly_balances.items():
                curr = constants.accnts_to_currs().get(accnt)
                if curr == self.cache.get('curr'):
                    monthly_balance += balance
                else:
                    original_cny_rate = 1.0 if curr == 'CNY' else exchange_rates.get(f'{curr.lower()}_cny')
                    target_cny_rate = 1.0 if self.cache.get('curr') == 'CNY' else exchange_rates.get(f'{self.cache.get("curr").lower()}_cny')
                    monthly_balance += balance * original_cny_rate / target_cny_rate
        else:
            monthly_balance = monthly_balances.get(accnt)
        
            



        # Change monthly_balance according to currencies for 总账本

        # Populate the rows
        for entry in entries:
            # Insert day-marking row.
            if entry_date > entry.get('date'):
                entry_date = entry.get('date')
                daily_income_and_expenditure = self.calculate_sums(accnt, dt.datetime(entry_date.year,entry_date.month,1), entry_date, entry.get('currency'))
                daily_balance = round(monthly_balance + daily_income_and_expenditure[0] - daily_income_and_expenditure[1], 2)
                row = RowWidget([f'{entry_date.month}月{entry_date.day}日 {constants.days_of_the_week[entry_date.weekday()]}',
                                 daily_balance], 
                                (ROW_HEIGHT, 500, 200), 
                                2, 
                                self)
                self.entries_vboxes[accnt_index].addWidget(row)

            entry_category = entry.get('category')
            entry_remarks = entry.get('remarks')
            entry_amount = entry.get('amount') if entry.get('transaction_type') == '收入' else -entry.get('amount')
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
            self.cache['accnt'] = None if btn_id == 0 else self.inputs.get('accnts')[btn_id - 1]
            self.ui.entrs_stacked_widget.setCurrentWidget(self.scroll_areas[btn_id])

            # Update 收支数字显示 和 月份选择按钮显示的月份
            self.update_income_expenditure_display()
            self.update_sel_month_btn_text()

        self.accnts_btn_group.buttonClicked.connect(on_accnts_btn_group_click)


        # 月份选择按钮
        def on_sel_month_btn_click():
            accnt = self.cache.get('accnt')
            if self.ui.month_selector_dedit.isVisible():
                
                # Hide the date selection tools
                toggle_visibility(self.ui.month_selector_dedit, False)
                toggle_visibility(self.ui.apply_month_sel_globally_cbtn, False)
                
                selected_date = self.ui.month_selector_dedit.date().toPython()

                # Update month selection for all accounts if the button is checked
                if self.ui.apply_month_sel_globally_cbtn.isChecked():
                    self.cache['month_sels'] = {accnt:selected_date for accnt in self.cache.get('month_sels')}
                    self.update_sel_month_btn_text()
                    self.update_income_expenditure_display()
                    for i in range(len(self.inputs.get('accnts')) + 1):
                        self.refresh_scroll_area(i, selected_date.year, selected_date.month)
                
                # Otherwise only update month selection for the active account
                else:
                    btn_id = self.accnts_btn_group.checkedId()
                    self.cache['month_sels'][accnt] = selected_date
                    self.update_sel_month_btn_text()
                    self.update_income_expenditure_display()
                    self.refresh_scroll_area(btn_id, selected_date.year, selected_date.month)
            else:
                toggle_visibility(self.ui.month_selector_dedit, True)
                toggle_visibility(self.ui.apply_month_sel_globally_cbtn, True)
                self.ui.month_selector_dedit.setDate(QDate(self.cache.get('month_sels').get(accnt)))
                self.ui.apply_month_sel_globally_cbtn.setChecked(True)


        self.ui.sel_month_btn.clicked.connect(on_sel_month_btn_click)
        self.ui.month_selector_dedit.editingFinished.connect(on_sel_month_btn_click)


        def on_currs_btn_group_click():
            self.cache['curr'] = self.currs_btn_group.checkedButton().text()
            self.update_income_expenditure_display()
            if self.cache.get('accnt') is None:
                self.refresh_scroll_area(0)
        self.currs_btn_group.buttonClicked.connect(on_currs_btn_group_click)
    
    
    # FIXME: See if on_page_load can be replaced by showEvent() somehow.
    def showEvent(self, event):
        super().showEvent(event)
        self.set_widget_states_to_default()
        for i in range(len(self.inputs.get('accnts')) + 1):
            # self.refresh_scroll_area(i)
            self.ui.entrs_stacked_widget.setCurrentWidget(i)
        print('done')

    def on_page_load(self):
        pass
        



    def set_widget_states_to_default(self):
        toggle_visibility(self.ui.month_selector_dedit, False)
        toggle_visibility(self.ui.apply_month_sel_globally_cbtn, False)
        # self.ui.apply_month_sel_globally_cbtn.setChecked(True)

    

    def update_income_expenditure_display(self):
        ''' Update收支数字显示 '''
        accnt = self.cache.get('accnt')
        month_start, month_end = start_and_end_of_month(self.cache.get('month_sels')[accnt])

        # 计算收支
        income, expenditure = self.calculate_sums(accnt, month_start, month_end, self.cache['curr'])
        self.ui.incomes_btn.setText(f'收入\n{round(income, 2)}')
        self.ui.expenditures_btn.setText(f'支出\n{round(expenditure, 2)}')


    def update_sel_month_btn_text(self):
        ''' Update月份选择按钮显示的月份 '''
        accnt = self.cache.get('accnt')
        month_sels = self.cache.get('month_sels')
        date = month_sels.get(accnt)
        self.ui.sel_month_btn.setText(f'{date.year}年\n{date.month}月')


    
    def calculate_sums(self, accnts:str|None, start_date:dt.datetime, end_date:dt.datetime, currency:str='GBP') -> tuple:
        ''' Calculates the sum for a specified account, or a list of accounts, or all accounts (set accnts to None),
            within a specified time range (both ends inclusive), for a given currency. 
            Returns a tuple: (收入,支出)'''
        income_sum = 0
        expenditure_sum = 0

        # Default currency to GBP
        currency = 'GBP' if currency == '未指定' else currency

        # Create query for date range and accounts
        query = {
            "date": {"$gte": start_date, "$lte": end_date}
        }
        if accnts is not None:
            query['account'] = {"$in": accnts} if isinstance(accnts, list) else accnts

        # Iterate through documents that match the query
        for doc in constants.entries_collection.find(query):
            amount = doc['amount']
            transaction_type = doc['transaction_type']
            original_currency = doc['currency'] if doc['currency'] != '未指定' else 'GBP'
            exchange_rates:dict = doc.get('exchange_rates', {})

            # Currency conversion
            if original_currency == currency:
                if transaction_type == '收入':
                    income_sum += amount
                elif transaction_type == '支出':
                    expenditure_sum += amount
            else:
                original_cny_rate = 1.0 if original_currency == 'CNY' else exchange_rates.get(f'{original_currency.lower()}_cny')
                target_cny_rate = 1.0 if currency == 'CNY' else exchange_rates.get(f'{currency.lower()}_cny')
                try:
                    if transaction_type == '收入':
                        income_sum += amount * original_cny_rate / target_cny_rate
                    elif transaction_type == '支出':
                        expenditure_sum += amount * original_cny_rate / target_cny_rate
                except TypeError:
                    print(original_currency)
                    print(exchange_rates.get(f'{original_currency.lower()}_cny'))
                    print(original_cny_rate, target_cny_rate)

        return (income_sum, expenditure_sum)




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