#from abc import ABC, abstractmethod
from componente import Componente
import socket
from time import sleep
from threading import Thread, Event
from decimal import Decimal

class Sensor(Componente):
    def __init__(self, id, valorInicial, incrementoInicial):
        self.id = id
        self.valor = valorInicial
        self.incrementoValor = Decimal(str(incrementoInicial))
        self.enviando = False
        
    def iniciaThreads(self, valores, atualizandoValor, enderecoGerenciador):
        conectado = Event()

        atualizador = Thread(target=self.atualizaValor, args=(atualizandoValor, valores, conectado,))
        comunicador = Thread(target=self.processaSocket, args=(enderecoGerenciador, conectado,))

        atualizador.start()
        comunicador.start()

        atualizador.join()
        comunicador.join()

    def atualizaValor(self, atualizandoValor, valores, conectado):
        conectado.wait()

        while conectado.is_set():
            self.valor += self.incrementoValor
            with atualizandoValor:
                if not valores.empty():
                    valores.get()
                valores.put(self.valor)
            sleep(0.5)

    def processaSocket(self, enderecoGerenciador, conectado):
        # estabelece um socket para se comunicar com o servidor através do protocolo TCP/IP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conexao:
            conexao.connect(enderecoGerenciador)
            # mensagem de conexão
            mensagem = self.geraMensagem(tipo='COS', id_mensagem='0', id_sensor=str(self.id))
            conexao.sendall(mensagem)

            # aguarda uma confirmação de conexão do sensor ao gerenciador
            while not conectado.is_set():
                resposta = self.recebeMensagem(conexao)
                self.processaMensagem(resposta, conectado)
                
            while conectado.is_set():
                # aguarda uma solicitação, pelo gerenciador, de envio dos dados
                while not self.enviando:
                    resposta = self.recebeMensagem(conexao)
                    self.processaMensagem(resposta, conectado)
                
                # envia o valor da leitura a cada 1s
                while self.enviando:
                    mensagem = self.geraMensagem(tipo='EVG', id_mensagem='1', id_sensor=str(self.id), valor=str(self.valor))
                    conexao.sendall(mensagem)
                    sleep(1)

    def processaMensagem(self, mensagem, conectado):
        if (mensagem['tipo'] == 'COS'\
            and mensagem['id_mensagem'] == '1'\
            and mensagem['id_sensor'] == str(self.id)):
            conectado.set()
        
        elif (mensagem['tipo'] == 'EVG'\
              and mensagem['id_mensagem'] == '0'\
              and mensagem['id_sensor'] == str(self.id)):
            self.enviando = True
    
  
class SensorTemperatura(Sensor):
    def __init__(self, id, temperaturaInicial, incrementoTemp):
        Sensor.__init__(self, id, temperaturaInicial, incrementoTemp)

class SensorUmidade(Sensor):
    def __init__(self, id, umidadeInicial, incrementoUmid):
        Sensor.__init__(self, id, umidadeInicial, incrementoUmid)


class SensorCO2(Sensor):
    def __init__(self, id, co2Inicial, incrementoCO2):
        Sensor.__init__(self, id, co2Inicial, incrementoCO2)
