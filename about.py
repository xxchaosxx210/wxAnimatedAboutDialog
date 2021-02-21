import wx
import threading
import queue
from collections import namedtuple
from dataclasses import dataclass
import random

# set the frame rate
_FRAME_RATE = 1/60 # 60 FPS

# speed range at the veolicty rate the text will scroll at
_RANDOM_SPEED_RANGE = (3, 6)

# defines the spacing between the lines
_LINE_SPACING = 20

@dataclass
class LineText:
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0
    text: str = ''
    max_x: int = 0
    velocity: int = 1
    font: wx.Font = None
    
def _define_size(abouttext, dc):
    text_size = dc.GetFullTextExtent(abouttext.text, abouttext.font)
    abouttext.width, abouttext.height = (text_size[0], text_size[1])
    width, height = dc.Size
    abouttext.max_x = round(int(width/2) - int(abouttext.width/2))

@dataclass
class CoolEffect:

    x: int = 0
    y: int = 0
    width: int = 20
    height: int = 0
    colour: wx.Colour = None
    velocity: int = 2


class AnimatedDialog(wx.Dialog):

    def __init__(self, parent=None, id=-1, title="About", 
                 text=["My Program", "Paul Millar", 
                 "This is a brief description", "0.1"]):
        """Animated AboutDialog

        Args:
            parent (wxWindow, optional): The wxWindow Parent. Defaults to None.
            id (int, optional): The unique identifier window number. Defaults to -1.
            title (str, optional): Title of the AboutDialog. Defaults to "About".
            text (list, optional): App name, Author, description and Version. Defaults to ["My Program", "Paul Millar", "This is a brief description", "0.1"].
        """
        super().__init__()
        self.Create(parent=parent, id=id, title=title, style=wx.DEFAULT_DIALOG_STYLE)
        self.panel = AboutPanel(self, -1, text)
        btn_close = wx.Button(self, wx.ID_OK, "Close", size=(68, -1))

        self.Bind(wx.EVT_INIT_DIALOG, self.panel.start_animation, self)
        self.Bind(wx.EVT_WINDOW_DESTROY, self.panel.stop_animation, self)

        vs = wx.BoxSizer(wx.VERTICAL)

        hs = wx.BoxSizer(wx.HORIZONTAL)
        hs.Add(self.panel, 1, wx.EXPAND|wx.ALL, 0)
        vs.Add(hs, 1, wx.EXPAND|wx.ALL, 0)

        hs = wx.BoxSizer(wx.HORIZONTAL)
        hs.Add(btn_close, 0, wx.ALIGN_CENTER, 0)
        vs.Add(hs, 0, wx.ALIGN_CENTER, 0)

        self.SetSizerAndFit(vs)

        self.SetSize((400, 400))

        self.CenterOnParent()

class AboutPanel(wx.Panel):

    def __init__(self, parent, id, text):
        super().__init__(parent=parent, id=id)

        self._app = wx.GetApp()
        self._buffer = wx.EmptyBitmap(*self.GetSize())

        h1_font = wx.Font(pointSize=12, family=wx.FONTFAMILY_DECORATIVE,
        style=wx.FONTSTYLE_MAX, weight=wx.FONTWEIGHT_MAX, underline=True,
        faceName="arial", encoding=wx.FONTENCODING_DEFAULT)

        h2_font = wx.Font(pointSize=10, family=wx.FONTFAMILY_DECORATIVE,
        style=wx.FONTSTYLE_MAX, weight=wx.FONTWEIGHT_MAX, underline=False,
        faceName="arial", encoding=wx.FONTENCODING_DEFAULT)

        lines = (
            LineText(font=h1_font, text=text[0], velocity=random.randint(*_RANDOM_SPEED_RANGE)),
            LineText(font=h2_font, text=f"Developed by {text[1]}", velocity=random.randint(*_RANDOM_SPEED_RANGE)),
            LineText(font=h2_font, text=text[2], velocity=random.randint(*_RANDOM_SPEED_RANGE)),
            LineText(font=h2_font, text=f"Version - {text[3]}", velocity=random.randint(*_RANDOM_SPEED_RANGE))
        )

        self._lines = namedtuple("TextGroup", ["name", "author", "description", "version"])(*lines)

        self._cooleffect = CoolEffect(colour=wx.Colour(0, 0, 0, 10))

        self.Bind(wx.EVT_PAINT, self._on_paint, self)
        self.Bind(wx.EVT_SIZE, self._on_size, self)
    
    def start_animation(self, evt):
        self._queue = queue.Queue()
        self._thread = threading.Thread(target=self._animation_loop)
        self._thread.start()
        evt.Skip()
    
    def stop_animation(self, evt):
        if self._thread.is_alive():
            self._queue.put("quit")
        evt.Skip()

    def _on_size(self, evt):
        self._buffer = wx.EmptyBitmap(*evt.GetSize())
        self._width, self._height = evt.GetSize()
        dc = wx.ClientDC(self)
        for line in self._lines:
            _define_size(line, dc)
            line.x = 0 - line.width
        # define the Y starting position
        lines_height = (line.height * len(self._lines)) + (_LINE_SPACING * len(self._lines))
        starting_y = round((self._height/2) - (lines_height/2))
        for line in self._lines:
            line.y = starting_y
            starting_y = starting_y + line.height + _LINE_SPACING
        
        # cooleffect
        self._cooleffect.height = lines_height + 20
        line_widths = list(map(lambda line : line.width, self._lines))
        self._cooleffect.width = max(line_widths)
        self._cooleffect.y = round((self._height/2) - (self._cooleffect.height/2))
        self._cooleffect.x = self._width
    
    def _on_paint(self, evt):
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self._buffer, 0, 0)
    
    def _update_positions(self):
        for line in self._lines:
            if line.x < line.max_x:
                line.x += line.velocity
        
        if self._cooleffect.x < -self._cooleffect.width:
            self._cooleffect.x = self._width
        self._cooleffect.x -= self._cooleffect.velocity
        
    def _animation_loop(self):
        quit = threading.Event()
        while not quit.is_set():
            try:
                msg = self._queue.get(timeout=_FRAME_RATE)
                if msg == "quit":
                    quit.set()
            except queue.Empty:
                # update next frame animation
                wx.CallAfter(self._update_frame)
    
    def _update_frame(self):
        self._update_positions()
        dc = wx.MemoryDC()
        dc.SelectObject(self._buffer)
        self._draw(wx.GCDC(dc))
        del dc
        self.Refresh()
        self.Update()

    def _draw(self, dc):
        dc.Clear()
        dc.SetBackground(wx.WHITE_BRUSH)
        dc.SetBrush(wx.WHITE_BRUSH)
        dc.SetPen(wx.WHITE_PEN)
        dc.DrawRectangle(0, 0, self._width, self._height)
        # Draw the cooleffect
        dc.SetBrush(wx.Brush(self._cooleffect.colour))
        dc.SetPen(wx.Pen(self._cooleffect.colour))
        dc.DrawRectangle(self._cooleffect.x, self._cooleffect.y, 
                         self._cooleffect.width, self._cooleffect.height)
        dc.SetBrush(wx.BLACK_BRUSH)
        dc.SetPen(wx.BLACK_PEN)
        # draw text here
        for line in self._lines:
            dc.SetFont(line.font)
            dc.DrawText(line.text, line.x, line.y)