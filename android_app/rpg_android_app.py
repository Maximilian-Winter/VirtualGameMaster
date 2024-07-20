from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.clock import Clock

from rpg_app import Config, OpenAIChatAPI, RPGApp

class RPGAndroidApp(App):
    def build(self):
        self.config = Config()
        api = OpenAIChatAPI(self.config.OPEN_ROUTER_API_KEY, "https://openrouter.ai/api/v1", self.config.MODEL)
        self.rpg_app = RPGApp(self.config, api)
        self.rpg_app.load()

        layout = BoxLayout(orientation='vertical')

        self.output_label = Label(text="Welcome to the RPG App!", size_hint_y=0.8, text_size=(Window.width, None))
        self.output_label.bind(texture_size=self.output_label.setter('size'))

        self.input_box = TextInput(multiline=False, size_hint_y=0.1)
        self.input_box.bind(on_text_validate=self.on_enter)

        button_layout = BoxLayout(size_hint_y=0.1)
        self.submit_button = Button(text="Submit")
        self.submit_button.bind(on_press=self.on_submit)
        self.save_button = Button(text="Save")
        self.save_button.bind(on_press=self.on_save)
        self.exit_button = Button(text="Exit")
        self.exit_button.bind(on_press=self.on_exit)

        button_layout.add_widget(self.submit_button)
        button_layout.add_widget(self.save_button)
        button_layout.add_widget(self.exit_button)

        layout.add_widget(self.output_label)
        layout.add_widget(self.input_box)
        layout.add_widget(button_layout)

        return layout

    def on_enter(self, instance):
        self.process_input(instance.text)
        instance.text = ""

    def on_submit(self, instance):
        self.process_input(self.input_box.text)
        self.input_box.text = ""

    def on_save(self, instance):
        self.rpg_app.manual_save()
        self.output_label.text += "\nGame saved successfully!"

    def on_exit(self, instance):
        self.rpg_app.save()
        self.stop()

    def process_input(self, user_input):
        response_generator, should_exit = self.rpg_app.process_input(user_input.strip(), True)

        if should_exit:
            self.stop()
        else:
            self.output_label.text += f"\nYou: {user_input}"
            Clock.schedule_once(lambda dt: self.stream_response(response_generator), 0)

    def stream_response(self, response_generator):
        response = ""
        for token in response_generator:
            response += token
            self.output_label.text += token
            Clock.schedule_once(lambda dt: None, 0)  # Force UI update

if __name__ == '__main__':
    RPGAndroidApp().run()