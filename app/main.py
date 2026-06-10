from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.clock import Clock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from cliente.cliente_modbus import ClienteMODBUS


class ModbusApp(MDApp):

    def build(self):
        self._cliente = None
        self._evento_recorrente = None
        kv_path = os.path.join(os.path.dirname(__file__), "interface.kv")
        return Builder.load_file(kv_path)

    def _tela(self):
        return self.root

    def conectar(self):
        tela = self._tela()
        ip = tela.ids.ip.text.strip()
        porta_txt = tela.ids.porta.text.strip()

        if not ip or not porta_txt:
            tela.ids.resultado.text = "Preencha IP e Porta."
            return

        try:
            porta = int(porta_txt)
        except ValueError:
            tela.ids.resultado.text = "Porta inválida."
            return

        try:
            self._cliente = ClienteMODBUS(ip, porta)
            self._cliente.conecta()
            tela.ids.resultado.text = f"Conectado em {ip}:{porta}"
        except Exception as e:
            tela.ids.resultado.text = f"Erro ao conectar: {e}"

    def _tipo_para_codigo(self, tipo_str):
        mapa = {
            "Holding Register": 1,
            "Coil": 2,
            "Input Register": 3,
            "Discrete Input": 4,
        }
        return mapa.get(tipo_str, None)

    def ler(self):
        if self._evento_recorrente:
            self._evento_recorrente.cancel()
            self._evento_recorrente = None

        tela = self._tela()
        recorrente = tela.ids.recorrente.active

        if recorrente:
            self._evento_recorrente = Clock.schedule_interval(
                lambda dt: self._executar_leitura(), 1.0
            )
        else:
            self._executar_leitura()

    def _executar_leitura(self):
        tela = self._tela()

        if not self._cliente:
            tela.ids.resultado.text = "Não conectado."
            return

        addr_txt = tela.ids.endereco.text.strip()
        tipo_str = tela.ids.tipo.text

        if not addr_txt:
            tela.ids.resultado.text = "Informe o endereço."
            return

        try:
            addr = int(addr_txt)
        except ValueError:
            tela.ids.resultado.text = "Endereço inválido."
            return

        try:
            if tipo_str == "Float":
                resultado = self._cliente.lerFloat(addr)
            elif tipo_str == "Bits":
                resultado = self._cliente.lerBits(addr)
            else:
                codigo = self._tipo_para_codigo(tipo_str)
                if codigo is None:
                    tela.ids.resultado.text = "Tipo desconhecido."
                    return
                resultado = self._cliente.lerDado(codigo, addr)

            if resultado is None:
                tela.ids.resultado.text = "Erro na leitura (sem resposta)."
            else:
                tela.ids.resultado.text = str(resultado)

        except Exception as e:
            tela.ids.resultado.text = f"Erro: {e}"

    def escrever(self):
        if self._evento_recorrente:
            self._evento_recorrente.cancel()
            self._evento_recorrente = None

        tela = self._tela()

        if not self._cliente:
            tela.ids.resultado.text = "Não conectado."
            return

        addr_txt = tela.ids.endereco.text.strip()
        valor_txt = tela.ids.valor.text.strip()
        tipo_str = tela.ids.tipo.text

        if not addr_txt or not valor_txt:
            tela.ids.resultado.text = "Preencha endereço e valor."
            return

        try:
            addr = int(addr_txt)
        except ValueError:
            tela.ids.resultado.text = "Endereço inválido."
            return

        try:
            if tipo_str == "Float":
                valor = float(valor_txt)
                ok = self._cliente.escreveFloat(addr, valor)
            elif tipo_str == "Bits":
                # Formato esperado no campo valor: "posição,bit" ex: "3,1"
                partes = valor_txt.split(",")
                if len(partes) != 2:
                    tela.ids.resultado.text = "Para Bits, use formato: posição,bit  ex: 3,1"
                    return
                posicao = int(partes[0].strip())
                bit = int(partes[1].strip())
                ok = self._cliente.escreveBit(addr, posicao, bit)
            else:
                codigo = self._tipo_para_codigo(tipo_str)
                if codigo is None:
                    tela.ids.resultado.text = "Tipo desconhecido."
                    return
                valor = int(valor_txt)
                ok = self._cliente.escreveDado(codigo, addr, valor)

            tela.ids.resultado.text = "Escrita OK" if ok else "Falha na escrita."

        except Exception as e:
            tela.ids.resultado.text = f"Erro: {e}"


ModbusApp().run()