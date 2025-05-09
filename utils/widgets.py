from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.factory import Factory
from kivy.graphics import Color, Rectangle, Line, RoundedRectangle
from kivy.properties import ListProperty, StringProperty, NumericProperty
from utils.loading import PRIMARY, SECONDARY, ACCENT, TEXT
from kivy.clock import Clock

class StyledWidget:
    """Abstract base class for all styled widgets"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(lambda dt: self._setup_canvas())

    def _setup_canvas(self):
        """Override this method in subclasses to set up canvas instructions"""
        pass

class StyledButton(Button, StyledWidget):
    border_radius = NumericProperty(15)
    border_width = NumericProperty(2)
    maximum_width = NumericProperty(300)
    minimum_width = NumericProperty(100)
    
    def _setup_canvas(self):
        with self.canvas.before:
            # Transparent background
            Color(0, 0, 0, 0)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
            
            # Accent color border
            Color(*ACCENT)
            self._border = Line(
                width=self.border_width,
                rounded_rectangle=(
                    self.x, self.y, self.width, self.height,
                    self.border_radius, self.border_radius
                )
            )
        
        self.bind(pos=self._update_canvas, size=self._update_canvas)
        self.font_name = "Bold"
        self.color = TEXT
        self.background_color = (0, 0, 0, 0)  # Transparent background
        self.size_hint_y = None
        self.size_hint_x = None
        self.height = 50  # Default height for buttons
        self.width = 200  # Default width for buttons

    def _update_canvas(self, *args):
        if hasattr(self, 'bg_rect'):
            # Ensure width stays within bounds
            if self.width > self.maximum_width:
                self.width = self.maximum_width
            elif self.width < self.minimum_width:
                self.width = self.minimum_width
                
            self.bg_rect.pos = self.pos
            self.bg_rect.size = self.size
            if hasattr(self, '_border'):
                self._border.rounded_rectangle = (
                    self.x, self.y, self.width, self.height,
                    self.border_radius, self.border_radius
                )

class StyledTextInput(TextInput, StyledWidget):
    def _setup_canvas(self):
        self.font_name = "Regular"
        self.foreground_color = TEXT
        self.background_color = SECONDARY
        self.cursor_color = TEXT
        self.hint_text_color = TEXT
        self.padding = [10, 10, 10, 10]
        self.multiline = True
        self.size_hint_y = None
        self.height = 45  # Default height for text inputs

class StyledLabel(Label, StyledWidget):
    def _setup_canvas(self):
        self.font_name = "Regular"
        self.color = TEXT
        self.text_size = self.size
        self.halign = 'center'
        self.valign = 'middle'
        self.padding = [10, 0, 0, 0]
        self.size_hint_y = None
        self.height = 30  # Default height for labels
        self.size_hint_x = 1  # Allow full width
        self.shorten = False  # Prevent text shortening
        self.shorten_from = 'right'  # If shortening is needed, do it from right
        self.markup = True  # Enable markup for better text control
        self.text_size = (None, None)  # Allow text to use natural size

class RoundedLabel(StyledLabel):
    border_radius = NumericProperty(15)
    
    def _setup_canvas(self):
        super()._setup_canvas()
        with self.canvas.before:
            Color(*PRIMARY)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[self.border_radius]
            )
        
        self.bind(pos=self._update_canvas, size=self._update_canvas)
    
    def _update_canvas(self, *args):
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = self.pos
            self.bg_rect.size = self.size

class StyledBoxLayout(BoxLayout, StyledWidget):
    border_radius = NumericProperty(15)
    padding = ListProperty([20, 20, 20, 20])  # [left, top, right, bottom]
    spacing = NumericProperty(10)
    
    def _setup_canvas(self):
        with self.canvas.before:
            Color(*PRIMARY)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[self.border_radius]
            )
        
        self.bind(pos=self._update_canvas, size=self._update_canvas)
    
    def _update_canvas(self, *args):
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = self.pos
            self.bg_rect.size = self.size

class TitleLabel(StyledLabel):
    def _setup_canvas(self):
        super()._setup_canvas()
        self.font_name = "Bold"
        self.font_size = 24  # Fixed font size for titles
        self.height = 40  # Taller height for titles

class SubtitleLabel(StyledLabel):
    def _setup_canvas(self):
        super()._setup_canvas()
        self.font_name = "Regular"
        self.font_size = 18  # Fixed font size for subtitles
        self.height = 35  # Slightly taller than regular labels

# Register the widgets with Kivy's Factory
Factory.register('StyledButton', cls=StyledButton)
Factory.register('StyledTextInput', cls=StyledTextInput)
Factory.register('StyledLabel', cls=StyledLabel)
Factory.register('RoundedLabel', cls=RoundedLabel)
Factory.register('StyledBoxLayout', cls=StyledBoxLayout)
Factory.register('TitleLabel', cls=TitleLabel)
Factory.register('SubtitleLabel', cls=SubtitleLabel) 