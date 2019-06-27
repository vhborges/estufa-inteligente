#from abc import ABC, abstractmethod
from componente import Componente
import socket
from time import sleep
from threading import Thread, Event
from decimal import Decimal

class Sensor(Componente):
    def __init__(self, id, valorInicial, incrementoInicial, enderecoGerenciador):
        self.id = id
        self.valor = valorInicial
        self.incrementoValor = Decimal(str(incrementoInicial))
        self.ativo = True
        self.enviando = False
        self.enderecoGerenciador = enderecoGerenciador
        
    def iniciaThreads(self, valores, atualizandoValor):
        atualizador = Thread(target=self.atualizaValor, args=(atualizandoValor, valores,))
        comunicador = Thread(target=self.processaSocket)

        atualizador.start()
        comunicador.start()

    #atualiza o valor (temperatura, pressão e umidade) sendo lido pelos sensores
    def atualizaValor(self, atualizandoValor, valores):
        while self.ativo:
            with atualizandoValor:
                if not valores.empty():
                    self.valor = valores.get() + self.incrementoValor
                valores.put(self.valor)
            sleep(0.5)

    def processaSocket(self):
        # estabelece um socket para se comunicar com o servidor através do protocolo TCP/IP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conexao:
            conexao.connect(self.enderecoGerenciador)
            # mensagem de identificação
            mensagem = self.geraMensagem(tipo='IDS', id_mensagem='0', id_componente=str(self.id))
            conexao.sendall(mensagem)

            while self.ativo:
                # aguarda uma solicitação, pelo gerenciador, de envio dos dados
                while not self.enviando:
                    resposta = self.recebeMensagem(conexao)
                    self.processaMensagem(resposta)
                
                # envia o valor da leitura a cada 1s
                while self.enviando:
                    mensagem = self.geraMensagem(tipo='EVG', id_mensagem='1', id_componente=str(self.id), valor=str(self.valor))
                    conexao.sendall(mensagem)
                    sleep(1)

    def processaMensagem(self, mensagem):
        #processa uma mensagem pedido de envio da leitura dos dados de um sensor para o gerenciador
        if (mensagem['tipo'] == 'EVG'\
        and mensagem['id_mensagem'] == '0'\
        and mensagem['id_componente'] == str(self.id)):
            self.enviando = True
    
  
class SensorTemperatura(Sensor):
    def __init__(self, id, temperaturaInicial, incrementoTemp, enderecoGerenciador):
        Sensor.__init__(self, id, temperaturaInicial, incrementoTemp, enderecoGerenciador)

class SensorUmidade(Sensor):
    def __init__(self, id, umidadeInicial, incrementoUmid, enderecoGerenciador):
        Sensor.__init__(self, id, umidadeInicial, incrementoUmid, enderecoGerenciador)


class SensorCO2(Sensor):
    def __init__(self, id, co2Inicial, incrementoCO2, enderecoGerenciador):
        Sensor.__init__(self, id, co2Inicial, incrementoCO2, enderecoGerenciador)
