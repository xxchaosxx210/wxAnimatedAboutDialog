import wx

cdef class C_LineText:
    cdef public int x
    cdef public int y
    cdef public int width
    cdef public int height
    cdef public int max_x
    cdef public int velocity
    cdef public int finished_scrolling
    cpdef public object text
    cpdef public object font

    def __init__(self, text, font):
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.max_x = 0
        self.velocity = 8
        self.finished_scrolling = 0
        self.text = text
        self.font = font


cdef class C_BackgroundBox:
    cdef public int x
    cdef public int y
    cdef public int width
    cdef public int height
    cdef public int min_x
    cdef public int velocity
    cdef public int finished_scrolling
    cpdef public object colour
    cpdef public object border

    def __init__(self, colour, border):
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.min_x = 0
        self.velocity = 8
        self.finished_scrolling = 0
        self.colour = colour
        self.border = border
    