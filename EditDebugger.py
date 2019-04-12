
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from GraphScene_v2 import GraphScene

import sys
import math
import inspect
import multiprocessing
import importlib
import threading
from enum import Enum
from queue import Queue

app = None

class Op(Enum):
    STOP = 0
    STEP = 1
    SKIP = 2

class GraphApp(QMainWindow):

    def __init__(self,file):
        super().__init__()

        global app
        app = self

        print('main thread is', threading.get_ident())
        self.setup_main_window(file)
        self.setup_debugger(file)
        self.setup_actions()
        self.setup_connectors()

    def get_graph(self):
        return self.graph_display.scene().get_graph()

    def setup_main_window(self,file):
        self.text_edit = Editor()
        self.text_edit.setPlainText(open(file).read())

        self.graph_display = QGraphicsView()
        self.graph_display.setRenderHint(QPainter.Antialiasing)
        self.graph_display.setMouseTracking(True)
        self.graph_display.setScene(GraphScene())

        central_widget = QSplitter()
        central_widget.addWidget(self.graph_display)
        central_widget.addWidget(self.text_edit)

        self.setCentralWidget(central_widget)

    def setup_debugger(self,file):
        self.debug_queue = Queue()
        self.debugger = Debugger(file,self.debug_queue)
        self.debug_thread = QThread()
        self.debugger.moveToThread(self.debug_thread)
        self.debug_thread.start()

    def setup_actions(self):

        run = QAction(QIcon('assets/run_exc.png'), '&Run', self)
        run.triggered.connect(self.debugger.start_debug)

        step = QAction(QIcon('assets/stepbystep_co.png'), '&Step', self)
        step.triggered.connect(self.debug_step)

        skip = QAction(QIcon('assets/stepover_co.png'), '&Skip', self)
        skip.triggered.connect(self.debug_skip)

        stop = QAction(QIcon('assets/terminate_co.png'), '&Stop', self)
        stop.triggered.connect(self.debug_stop)

        menubar = self.menuBar()
        toolbar = self.addToolBar('bar')

        toolbar.addAction(run)
        toolbar.addAction(step)
        toolbar.addAction(skip)
        toolbar.addAction(stop)


    def setup_connectors(self):
        self.debugger.line_changed.connect(self.text_edit.change_active)

    def debug_step(self):
        self.debug_queue.put(Op.STEP)

    def debug_stop(self):
        self.debug_queue.put(Op.STOP)

    def debug_skip(self):
        self.debug_queue.put(Op.SKIP)



class Debugger(QObject):

    line_changed = pyqtSignal(int, name='lineChanged')
    obj = None

    def __init__(self,file,input):
        super().__init__()
        self.input = input
        self.file = file
        Debugger.obj = self
        #import test_file
        #self.user_mod = importlib.import_module(file.replace('.py',''))

    def start_debug(self):
        print('debug thread is', threading.get_ident())
        sys.settrace(Debugger.debug_ftrace)
        importlib.import_module(self.file.replace('.py',''))

        #TODO: debug completed, run same func as Op.STOP

    def debug_trace(frame, event, arg):
        if event != 'return' and event != 'line':
            return
        print(event, arg)
        print('printing in trace',frame.f_code.co_name)

        Debugger.obj.line_changed.emit(frame.f_lineno)
        print(frame.f_lineno)

        op = Debugger.obj.input.get()
        if op == Op.STOP:
            #TODO do something with this...
            return
        elif op == Op.STEP:
            return Debugger.debug_trace
        elif op == Op.SKIP:
            return Debugger.debug_ftrace


    def debug_ftrace(frame, event, arg):
        if event != 'call':# or frame.f_code.co_filename != Debugger.file:
            return

        if 'test_file.py' not in inspect.getfile(frame):
            return

        Debugger.obj.line_changed.emit(frame.f_lineno)
        op = Debugger.obj.input.get()
        print(op)
        if op == Op.STOP:
            #TODO do something with this...
            return
        elif op == Op.STEP:
            return Debugger.debug_trace
        elif op == Op.SKIP:
            return Debugger.debug_ftrace

class LineMargin(QWidget):

    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        self.max_line_no = 1

    def sizeHint(self):
        return QSize(self.margin_width, 0)

    def resizeEvent(self, event):
        cr = self.editor.contentsRect()
        self.setGeometry(QRect(cr.left(), cr.top(), self.margin_width, cr.height()))

    def paintEvent(self,event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), Qt.cyan)

        line = self.editor.firstVisibleBlock()
        line_no = line.blockNumber()+1
        top_edge = self.editor.blockBoundingGeometry(line).translated(self.editor.contentOffset()).top()
        bot_edge = top_edge + self.editor.blockBoundingRect(line).height()
        height = self.fontMetrics().height()

        painter.setPen(Qt.black)
        while line.isValid() and top_edge <= event.rect().bottom():
            if line.isVisible() and bot_edge >= event.rect().top():
                if line_no == self.editor.active_line:
                    painter.drawText(0,top_edge, self.margin_width-2, height, Qt.AlignRight, '>' + str(line_no))
                else:
                    painter.drawText(0,top_edge, self.margin_width-2, height, Qt.AlignRight, str(line_no))
            line_no += 1
            line = line.next()
            top_edge = bot_edge
            bot_edge = top_edge + self.editor.blockBoundingRect(line).height()

    def compute_width(self):
        digits = int(math.log10(self.max_line_no))+1
        self.margin_width = 15+self.fontMetrics().boundingRect('9').width()*digits
        return self.margin_width

    def update_margin(self, rect, dy):
        if dy:
            self.scroll(0,dy)
        else:
            self.update(0,rect.y(), self.width(), rect.height())
        if rect.contains(self.editor.viewport().rect()):
            self.editor.update_width(0) 


class Editor(QPlainTextEdit):

    @property
    def active_line(self):
        return self._active_line

    @active_line.setter
    def active_line(self, value):
        self._active_line = value
        self.update()

    def __init__(self):
        super().__init__()
        self.lm = LineMargin(self)
        self.blockCountChanged.connect(self.update_width)
        self.updateRequest.connect(self.lm.update_margin)
        self.update_width(1)
        self.active_line = -1

    def update_width(self, blocks):
        self.lm.max_line_no = self.blockCount()
        self.setViewportMargins(self.lm.compute_width(),0,0,0)

    def resizeEvent(self,event):
        super().resizeEvent(event)
        self.lm.resizeEvent(event)

    def sizeHint(self):
        return QSize(500,500)

    def change_active(self, val):
        self.active_line = val
        self.update()

