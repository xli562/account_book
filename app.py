import os, sys, time, json, copy, subprocess, glob, shutil

from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import *
from PySide2.QtGui import QPixmap, QFontDatabase


from modules import constants



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
    ''' Input: Initial page.
        Output: Buttons navigate to different pages.
                No data output.
    '''
    def __init__(self):
        super().__init__()
        self.name = 'home'
        self.init_ui()
        self.connecting_dots()

    def __new__(cls, *args, **kwargs):
        '''Make sure only one instance is ever created.'''
        if not hasattr(cls, '_instance'):
            cls._instance = super(home, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def init_ui(self):
        loader = QUiLoader()
        file = QFile('./ui/home.ui')
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self)
        file.close()

        layout = QVBoxLayout(self)
        layout.addWidget(self.ui)

        # The logo img_lbl
        # pixmap = QPixmap("./ui/resources/logo.png")
        # self.ui.img_lbl.setPixmap(pixmap.scaled(self.ui.img_lbl.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        # self.ui.img_lbl.setScaledContents(True)
    

    def connecting_dots(self):
        '''connecting signals and slots'''
        # def on_new_syn_btn_click():
        #     constants.rerun_or_open_syn = False
        #     navigate(self.name, 'edit_seq', self.name, 'new_syn_btn')
        #     self.cnfrm_fluids_alctn_instance = cnfrm_fluid_alctn(self)
        #     self.cnfrm_fluids_alctn_instance.setAttribute(Qt.WA_DeleteOnClose)
        #     self.cnfrm_fluids_alctn_instance.exec_()

        # self.ui.new_syn_btn.clicked.connect(on_new_syn_btn_click)
        
        # def on_open_syn_btn_click():
        #     # Select the synthesis file in the file dialog, 
        #     # then go to edit_seq.
        #     if constants.on_linux:
        #         subprocess.Popen(['onboard'])
        #     file_sel = QFileDialog()
        #     options = file_sel.Options()
        #     options |= file_sel.ReadOnly
        #     filename, _ = file_sel.getOpenFileName(None, 'Select a synthesis file', './files/synthesis_parameters', 'All Files (*)', options=options)
        #     if filename:
        #         pickle_data = marinate(filename)
        #         constants.syn_config = pickle_data[0]
        #         constants.syn_data = pickle_data[1]

        #         constants.rerun_or_open_syn = True
        #         navigate(self.name, 'edit_seq', self.name, 'open_syn_btn')
        #         self.cnfrm_fluids_alctn_instance = cnfrm_fluid_alctn(self)
        #         self.cnfrm_fluids_alctn_instance.setAttribute(Qt.WA_DeleteOnClose)
        #         self.cnfrm_fluids_alctn_instance.exec_()

        #     if constants.on_linux:
        #         subprocess.call(['pkill', 'onboard'])
            
        # self.ui.open_syn_btn.clicked.connect(on_open_syn_btn_click)

        # self.ui.manual_comm_btn.clicked.connect(lambda: 
        #     navigate(self.name, 'manual_comm', self.name, 'manual_comm_btn'))
        
        # self.ui.sys_stngs_btn.clicked.connect(lambda: 
            # navigate(self.name, 'sys_stngs', self.name, 'sys_stngs_btn'))




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