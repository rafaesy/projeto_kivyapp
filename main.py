from kivymd.app import MDApp
from kivy.lang import Builder


class ModbusApp(MDApp):

    def build(self):
        return Builder.load_file("interface.kv")

    def conectar(self):
        print("Conectar clicado")

    def ler(self):
        print("Ler clicado")

    def escrever(self):
        print("Escrever clicado")


ModbusApp().run()