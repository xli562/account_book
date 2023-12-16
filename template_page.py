class template(QWidget):
    def __init__(self):
        super().__init__()
        self.name = 'template'
        self.init_ui()
        self.connecting_dots()
    
    def __new__(cls, *args, **kwargs):
        '''Make sure only one instance is ever created.'''
        if not hasattr(cls, '_instance'):
            cls._instance = super(template, cls).__new__(cls, *args, **kwargs)
        return cls._instance



    def init_ui(self):
        loader = QUiLoader()
        file = QFile(f'./ui/{self.name}.ui')
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self)
        file.close()



    def connecting_dots(self):
        page_ready.sig.connect(self.on_page_load)
    
    

    def on_page_load(self):
        if constants.navigation_info.get('dest_page') == self.name:
            self.ui.dyn_lbl.clear()
            pass