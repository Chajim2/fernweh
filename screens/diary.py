from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager
from utils.loading import load_fonts
from utils.ai import get_emotions
from kivy.clock import Clock
from utils.loading import load_colors
from kivy.lang import Builder

PRIMARY, SECONDARY, ACCENT, TEXT = load_colors()

class DiaryConstructor(BoxLayout):
    def __init__(self, **kwargs):
        super(DiaryConstructor, self).__init__(**kwargs)
        Window.bind(on_resize=self.on_window_resize)
        load_fonts()
        Clock.schedule_once(lambda dt: self.on_window_resize(None, *Window.size))
        self.chosen = []
        self.emotion_buttons = {}

    def on_window_resize(self, instance, width, height):
        try:
            if not self.width:  
                return
            # handling desktop, tablet and phone screen sizes
            if (width / height) > (15/9):
                padding_h = width / (3.3)
            elif (width / height) > 1:
                padding_h = width / 5
            else:         
                padding_h = 10
            self.padding = [padding_h, 0, padding_h, 0]
        except Exception as e:
            print(f"Error in resize handler: {e}")


    def add_emotion(self, emotion):
        self.chosen.append(emotion)
        self.emotion_buttons[emotion].disabled = True
        

    def submit_text(self, diary_input):
        emotions = get_emotions(diary_input)
        self.ids.placeholder.size_hint_y = 0.03
        self.remove_widget(self.ids.button)
        self.ids.labels_container.clear_widgets()
        self.ids.labels_container.size_hint_y = 0.28
        
        for emotion, value in emotions[:3]:
            label = Button(
                text=f"{emotion} : {value}",
                background_color=SECONDARY,
                color=TEXT,
                font_name="Regular",
                font_size=self.height / 31,
                halign='left',
                valign='middle',
                size_hint_x=1,
                padding=[10, 10],
                text_size=(None, None)
            )
            self.emotion_buttons[emotion] = label
            label.bind(on_press=lambda btn, em=emotion: self.add_emotion(em))
            label.bind(size=lambda instance, size: setattr(instance, 'text_size', (instance.width - 20, None)))
            self.ids.labels_container.add_widget(label)
        
        # Add a new confirmation button
        confirm_button = Button(
            text="Confirm Selection",
            background_color=PRIMARY,
            color=TEXT,
            font_name="Bold",
            font_size=self.height / 31,
            size_hint=(1, 0.1),
            pos_hint={'center_x': 0.5}
        )
        confirm_button.bind(on_press=self.go_to_confirmation)
        self.add_widget(confirm_button)

    def go_to_confirmation(self, instance):
        # Walk up the widget tree until we find the ScreenManager
        parent = self.parent
        while parent and not isinstance(parent, ScreenManager):
            parent = parent.parent
        
        if parent:
            # Now we have the ScreenManager
            screen_manager = parent
            confirmation_screen = screen_manager.get_screen('confirm')
            confirmation_screen.display_summary(
                self.ids.diary_input.text, 
                self.chosen
            )
            screen_manager.current = 'confirm'

class DiaryScreen(Screen):
    def __init__(self, **kwargs):
        Builder.load_file('screens/diary.kv')
        super(DiaryScreen, self).__init__(**kwargs)
        self.diary_constructor = DiaryConstructor()
        self.add_widget(self.diary_constructor)