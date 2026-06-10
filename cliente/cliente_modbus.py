from pymodbus.client import ModbusTcpClient
from time import sleep

class ClienteMODBUS():
    """
    Classe Cliente MODBUS usando pymodbus
    """
    def __init__(self, server_ip, porta, scan_time=1):
        """
        Construtor
        """
        # Cria o cliente TCP
        self._cliente = ModbusTcpClient(host=server_ip, port=porta)
        self._scan_time = scan_time

    def conecta(self):
        """
        Abre conexão MODBUS
        """
        self._cliente.connect()

    def close(self):
        """
        Fecha conexão MODBUS
        """
        self._cliente.close()

    def lerDado(self, tipo, addr):
        """
        Método para leitura de um dado da Tabela MODBUS
        """
        # Holding Register (função 03)
        if tipo == 1:
            resp = self._cliente.read_holding_registers(address=addr, count=1, device_id=1)
            if resp and not resp.isError():
                return resp.registers[0]
            return None

        # Coil (função 01)
        if tipo == 2:
            resp = self._cliente.read_coils(address=addr, count=1, device_id=1)
            if resp and not resp.isError():
                return resp.bits[0]
            return None

        # Input Register (função 04)
        if tipo == 3:
            resp = self._cliente.read_input_registers(address=addr, count=1, device_id=1)
            if resp and not resp.isError():
                return resp.registers[0]
            return None

        # Discrete Input (função 02)
        if tipo == 4:
            resp = self._cliente.read_discrete_inputs(address=addr, count=1, device_id=1)
            if resp and not resp.isError():
                return resp.bits[0]
            return None

        # Tipo inválido
        return None

    def escreveDado(self, tipo, addr, valor):
        """
        Método para a escrita de dados na Tabela MODBUS
        """
        # Holding Register (função 06 - single)
        if tipo == 1:
            resp = self._cliente.write_register(address=addr, value=valor, device_id=1)
            return bool(resp and not resp.isError())

        # Coil (função 05 - single)
        if tipo == 2:
            # Em coils, valor esperado é 0/1 (False/True)
            resp = self._cliente.write_coil(address=addr, value=bool(valor), device_id=1)
            return bool(resp and not resp.isError())

        # Tipo inválido
        return False
    
    def escreveFloat(self, addr, valor):

        """
        Escrita de float em dois registradores
        """

        regs = self._cliente.convert_to_registers(valor, data_type=self._cliente.DATATYPE.FLOAT32)

        resp = self._cliente.write_registers(
            address=addr,
            values=regs,
            device_id=1
        )

        return bool(resp and not resp.isError())

    def lerFloat(self, addr):

        """
        Leitura de float em dois registradores
        """

        resp = self._cliente.read_holding_registers(
            address=addr,
            count=2,
            device_id=1
        )

        if resp and not resp.isError():
            return self._cliente.convert_from_registers(resp.registers, data_type=self._cliente.DATATYPE.FLOAT32)
        
        return None

    def lerBits(self, addr):

        """
        Leitura individual dos bits
        """

        resp = self._cliente.read_holding_registers(
            address=addr,
            count=1,
            device_id=1
        )

        if resp and not resp.isError():
            valor = resp.registers[0]
            bits = [int(b) for b in format(valor, '016b')]
            return bits
        
        return None

    def escreveBit(self, addr, posicao, bit):

        """
        Escrita de bit individual
        """

        resp = self._cliente.read_holding_registers(
            address=addr,
            count=1,
            device_id=1
        )

        if resp and not resp.isError():
            valor = resp.registers[0]
            
            bits = [int(b) for b in format(valor, '016b')]
            bits[15-posicao] = int(bit)
            
            novo_valor = int(''.join(str(b) for b in bits), 2)
            
            escrita = self._cliente.write_register(
                address=addr,
                value=novo_valor,
                device_id=1
            )

            return bool(escrita and not escrita.isError())

        return False