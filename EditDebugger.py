
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from GraphScene import GraphScene
from GraphScene import Graph

import sys
import os
import math
import inspect
import multiprocessing
import importlib
import threading
import tempfile
from enum import Enum
from queue import Queue

app = None

class Op(Enum):
    STOP = 0
    STEP = 1
    SKIP = 2
    RESUME = 3

class GraphApp(QMainWindow):

    def __init__(self,file=None):
        super().__init__()

        global app
        app = self

        self.current_file = None

        self.setup_main_window(file)
        self.setup_debugger()
        self.setup_actions()
        self.setup_connectors()

    def setup_main_window(self,file=None):
        self.text_edit = Editor(file)
        self.breakpoints = self.text_edit.lm.breakpoints

        self.graph_display = QGraphicsView()
        self.graph_display.setRenderHint(QPainter.Antialiasing)
        self.graph_display.setMouseTracking(True)
        self.graph_display.setScene(GraphScene())

        central_widget = QSplitter()
        central_widget.addWidget(self.graph_display)
        central_widget.addWidget(self.text_edit)

        self.setCentralWidget(central_widget)

    def setup_debugger(self):
        self.debug_queue = Queue()
        self.debugger = Debugger(self,self.debug_queue,self.breakpoints)
        self.debug_thread = QThread()
        self.debugger.moveToThread(self.debug_thread)
        self.debug_thread.start()

    def setup_actions(self):

        new = QAction(QIcon('assets/new_untitled_text_file.png'), '&New', self)
        new.triggered.connect(self.new_file)

        save = QAction(QIcon('assets/save_edit.png'), '&Save', self)
        save.triggered.connect(self.save_file)

        save_as = QAction('&Save As', self)
        save_as.triggered.connect(self.save_file_as)

        export_graph = QAction('&Export Graph', self)
        export_graph.triggered.connect(self.graph_export)

        import_graph = QAction('&Import Graph', self)
        import_graph.triggered.connect(self.graph_import)

        open = QAction(QIcon('assets/fldr_obj.png'), '&Open', self)
        open.triggered.connect(self.load_file)

        run = QAction(QIcon('assets/run_exc.png'), '&Run', self)
        run.triggered.connect(self.debugger.start_debug)

        resume = QAction(QIcon('assets/resume_co.png'), '&Resume', self)
        resume.triggered.connect(self.debug_resume)

        step = QAction(QIcon('assets/stepbystep_co.png'), '&Step', self)
        step.triggered.connect(self.debug_step)

        skip = QAction(QIcon('assets/stepover_co.png'), '&Skip', self)
        skip.triggered.connect(self.debug_skip)

        stop = QAction(QIcon('assets/terminate_co.png'), '&Stop', self)
        stop.triggered.connect(self.debug_stop)

        toggle_weight = QAction(QIcon('assets/weights.png'), '&Display Weights', self)
        toggle_weight.setCheckable(True)
        toggle_weight.triggered.connect(self.toggle_weight)

        toggle_flow = QAction(QIcon('assets/flow.png'), '&Display Flow', self)
        toggle_flow.setCheckable(True)
        toggle_flow.triggered.connect(self.toggle_flow)

        toggle_directed = QAction(QIcon('assets/directed.png'), '&Directed Edges', self)
        toggle_directed.setCheckable(True)
        toggle_directed.triggered.connect(self.toggle_directed)

        menubar = self.menuBar()

        fileMenu = menubar.addMenu('&File')

        fileMenu.addAction(new)
        fileMenu.addAction(save)
        fileMenu.addAction(save_as)
        fileMenu.addAction(open)
        fileMenu.addSeparator()
        fileMenu.addAction(import_graph)
        fileMenu.addAction(export_graph)

        toolbar = self.addToolBar('bar')
        toolbar.addAction(new)
        toolbar.addAction(save)
        toolbar.addAction(open)
        toolbar.addSeparator()
        toolbar.addAction(run)
        toolbar.addAction(resume)
        toolbar.addAction(step)
        toolbar.addAction(skip)
        toolbar.addAction(stop)
        toolbar.addSeparator()
        toolbar.addAction(toggle_weight)
        toolbar.addAction(toggle_flow)
        toolbar.addAction(toggle_directed)


    def setup_connectors(self):
        self.debugger.line_changed.connect(self.text_edit.change_active)
        self.debugger.graph_reloaded.connect(self.graph_display.scene().set_graph_from_json)

    def new_file(self):
        #TODO: save current?
        self.current_file = None
        self.text_edit.setPlainText('')

    def save_file(self):
        if self.current_file is not None:
            text = self.text_edit.toPlainText()
            with open(self.current_file, 'wt') as file:
                file.write(text)
        else:
            self.save_file_as()

    def load_file(self):
        filename,file_type = QFileDialog.getOpenFileName(self, 'Select Graph To Import', 'scripts/',
                        'Python File (*.py);;All Files (*.*)')
        if not filename:
            return
        text = open(filename).read()
        self.text_edit.setPlainText(text)
        self.current_file = filename

    def save_file_as(self):
        filename,file_type = QFileDialog.getSaveFileName(self, 'Save File As', 'scripts/', 
                        'Python File (*.py);;All Files (*.*)')
        if not filename:
            return
        text = self.text_edit.toPlainText()
        with open(filename, 'wt') as file:
            file.write(text)
        self.current_file = filename

    def debug_resume(self):
        self.debug_queue.put(Op.RESUME)

    def debug_step(self):
        self.debug_queue.put(Op.STEP)

    def debug_stop(self):
        self.debug_queue.put(Op.STOP)

    def debug_skip(self):
        self.debug_queue.put(Op.SKIP)

    def graph_export(self):
        filename,file_type = QFileDialog.getSaveFileName(self, 'Export Graph To', 'graphs/myGraph', 
                        'JavaScript Object Notation File (*.json);;All Files (*.*)')
        if not filename:
            return
        self.get_graph().write_graph(filename)

    def graph_import(self):
        filename,file_type = QFileDialog.getOpenFileName(self, 'Select Graph To Import', 'graphs/',
                        'JavaScript Object Notation File (*.json);;All Files (*.*)')
        if not filename:
            return
        graph = Graph.read_graph(filename)
        self.set_graph(graph)

    def set_graph(self, graph):
        self.graph_display.scene().set_graph(graph)

    def get_graph(self):
        return self.graph_display.scene().get_graph()

    def toggle_weight(self, new_value):
        self.graph_display.scene().set_show_weight(new_value)

    def toggle_flow(self, new_value):
        self.graph_display.scene().set_show_flow(new_value)

    def toggle_directed(self, new_value):
        self.graph_display.scene().set_show_direction(new_value)






class DebugHalted(Exception):
    pass

class Debugger(QObject):

    line_changed = pyqtSignal(int, name='lineChanged')
    graph_reloaded = pyqtSignal(dict, name='graphReloaded')
    obj = None

    def __init__(self,app,input,breakpoints):
        super().__init__()
        self.input = input
        self.breakpoints = breakpoints
        self.app = app
        self.mod = None
        self.file = None
        Debugger.obj = self

    def start_debug(self):
        print(Debugger.obj.app.current_file)
        sys.settrace(Debugger.debug_fbtrace)
        self.input.queue.clear()
        data = Graph.write_graph_to_json(self.app.get_graph())
        try:
            print(self.mod)
            if not self.mod or self.mod.__name__ + '.py' not in self.app.current_file:
                file = os.path.basename(self.app.current_file)
                dir = os.path.dirname(self.app.current_file)

                sys.path.append(dir)
                self.file = file
                self.mod = importlib.import_module(file.replace('.py', ''))
            else:
                importlib.reload(self.mod)

        except DebugHalted:
            pass
        self.graph_reloaded.emit(data)

        print('finished')

        self.line_changed.emit(-1)

    def debug_fbtrace(frame, event, arg):
        if event != 'call':
            return

        if not Debugger.obj.file or Debugger.obj.file not in str(inspect.getfile(frame)):
            return

        if frame.f_lineno in Debugger.obj.breakpoints:
            return Debugger.debug_ftrace(frame, event, arg)
        else:
            return Debugger.debug_btrace

    def debug_btrace(frame, event, arg):
        if event != 'return' and event != 'line':
            return
        if frame.f_lineno in Debugger.obj.breakpoints:
            return Debugger.debug_trace(frame,event,arg)
        else:
            return Debugger.debug_btrace

    #TODO: add a separate debug trace for "looking for breakpoint" (play with eclipse)
    def debug_trace(frame, event, arg):
        if event != 'return' and event != 'line':
            return
        Debugger.obj.line_changed.emit(frame.f_lineno)

        op = Debugger.obj.input.get()
        if op == Op.STOP:
            raise DebugHalted
        elif op == Op.STEP:
            return Debugger.debug_trace
        elif op == Op.SKIP:
            return Debugger.debug_ftrace
        elif op == Op.RESUME:
            return Debugger.debug_btrace


    def debug_ftrace(frame, event, arg):
        if event != 'call':# or frame.f_code.co_filename != Debugger.file:
            return

        if not Debugger.obj.file or Debugger.obj.file not in str(inspect.getfile(frame)):
            return

        Debugger.obj.line_changed.emit(frame.f_lineno)

        op = Debugger.obj.input.get()
        if op == Op.STOP:
            raise DebugHalted
        elif op == Op.STEP:
            return Debugger.debug_trace
        elif op == Op.SKIP:
            return Debugger.debug_ftrace
        elif op == Op.RESUME:
            return Debugger.debug_btrace

class LineMargin(QWidget):

    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        self.max_line_no = 1
        self.breakpoints = set()

    def mouseDoubleClickEvent(self, event):
        self.flip_breakpoint(event.pos())


    def flip_breakpoint(self, pos):

        line = self.editor.firstVisibleBlock()
        lineno = line.blockNumber()+1
        top_edge = self.editor.blockBoundingGeometry(line).translated(self.editor.contentOffset()).top()
        bot_edge = top_edge + self.editor.blockBoundingRect(line).height()

        while pos.y() > bot_edge and line.isValid():
            line = line.next()
            top_edge = bot_edge
            bot_edge = top_edge + self.editor.blockBoundingRect(line).height()
            lineno = line.blockNumber()+1

        if lineno in self.breakpoints:
            self.breakpoints.remove(lineno)
        else:
            self.breakpoints.add(lineno)
        self.update()

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

                if line_no in self.breakpoints:
                    bkpt = QImage('assets/brkp_obj.png')
                    painter.drawImage(QRect(0,top_edge, height, height), bkpt)


            line_no += 1
            line = line.next()
            top_edge = bot_edge
            bot_edge = top_edge + self.editor.blockBoundingRect(line).height()

    def compute_width(self):
        digits = int(math.log10(self.max_line_no))+1
        self.margin_width =18+self.fontMetrics().boundingRect('9').width()*digits
        return self.margin_width

    def update_margin(self, rect, dy):
        if dy:
            self.scroll(0,dy)
        else:
            self.update(0,rect.y(), self.width(), rect.height())
        if rect.contains(self.editor.viewport().rect()):
            self.editor.update_width(0) 


class Editor(QPlainTextEdit):

    highlight_color = QColor(Qt.yellow).lighter(160)

    highlight_format = QTextBlockFormat()
    highlight_format.setBackground(highlight_color)

    @property
    def active_line(self):
        return self._active_line

    @active_line.setter
    def active_line(self, value):
        self._active_line = value
        self.update()

    def __init__(self,file=None):
        super().__init__()
        if file is not None:
            self.setPlainText(open(file).read())
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
        blk = self.document().findBlockByLineNumber(val-1)
        QTextCursor(blk).setBlockFormat(Editor.highlight_format)
        self.active_line = val


