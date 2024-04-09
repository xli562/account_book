from PySide2.QtWidgets import *
from PySide2.QtGui import *
from modules.functional_convenience import *





class RowWidget(QWidget):
    """ The widget for a row. """

    


    def __init__(self, row_data_list:list, row_sizes:tuple, scroll_group, parent, raw_data=None):
        """ row_sizes: (height, width_1, width_2, ... , width_n)"""
        super().__init__()
        self.parent = parent

        self.name = row_data_list[0]
        self.raw_data = raw_data
        self.content_list = row_data_list
        self.scroll_group = scroll_group

        # Create an hbox layout
        hbox = QHBoxLayout(self)
        hbox.setMargin(0)
        hbox.setSpacing(0)

        # Populate the row with data
        col = 1
        for text in row_data_list:
            label = QLabel(str(text))
            label.setFixedHeight(row_sizes[0])    # Change this line to change row height

            # The last element in the row would fill the empty space.
            if col == len(row_data_list):
                label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            else:
                label.setFixedWidth(row_sizes[col])
            hbox.addWidget(label)
            col += 1
        
        self.setLayout(hbox)
        self.setStyleSheet("background-color: none;")

    def highlight(self, color='lightblue'):
        """ Sets row background color. """

        # De-highlight the previous row
        if self.parent.current_highlighted_rows[self.scroll_group-1]:
            self.parent.current_highlighted_rows[self.scroll_group-1].setStyleSheet("background-color: none;")

        # Highlight the clicked widget (row)
        self.setStyleSheet(f"background-color: {color};")
        self.parent.current_highlighted_rows[self.scroll_group-1] = self  # Update the currently highlighted row

    def mousePressEvent(self, event):
        self.highlight()

    def __repr__(self):
        return f'{self.content_list} in group {self.scroll_group}'
