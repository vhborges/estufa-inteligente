from componente import Componente
import socket
from time import sleep
from threading import Thread
from decimal import Decimal

class Sensor(Componente):
    def __init__(self, id, valorInicial, incremento, enderecoGerenciador):
        self.id = id
        self.valor = Decimal(str(valorInicial))
        self.incrementoValor = Decimal(str(incremento))
        self.enviando = False
        self.enderecoGerenciador = enderecoGerenciador

    def iniciaThreads(self, valores, atualizandoValor):
        comunicador = Thread(target=self.processaSocket)
        atualizador = Thread(target=self.atualizaValor, args=(atualizandoValor, valores,))

        comunicador.start()
        atualizador.start()

    #atualiza o valor (temperatura, pressão e umidade) sendo lido pelos sensores
    def atualizaValor(self, atualizandoValor, valores):
        while True:
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
            mensagem = self.geraMensagem(tipo='IDS', id_componente=str(self.id))
            conexao.sendall(mensagem)

            while True:
                # aguarda uma solicitação, pelo gerenciador, de envio dos dados
                while not self.enviando:
                    resposta = self.recebeMensagem(conexao)
                    self.processaMensagem(resposta)
                
                # envia o valor da leitura a cada 1s
                while self.enviando:
                    mensagem = self.geraMensagem(tipo='EVG', sequencia='1', id_componente=str(self.id), valor=str(self.valor))
                    conexao.sendall(mensagem)
                    sleep(1)

    def processaMensagem(self, mensagem):
        # pedido de envio da leitura dos dados de um sensor para o gerenciador
        if (mensagem['tipo'] == 'EVG'\
        and mensagem['sequencia'] == '0'\
        and mensagem['id_componente'] == str(self.id)):
            self.enviando = True
    
  
class SensorTemperatura(Sensor):
    def __init__(self, id, temperaturaInicial, incrementoTemp, enderecoGerenciador):
        Sensor.__init__(self, id, temperaturaInicial, incrementoTemp, enderecoGerenciador)

class SensorUmidade(Sensor):
    def __init__(self, id, umidadeInicial, decrementoUmid, enderecoGerenciador):
        Sensor.__init__(self, id, umidadeInicial, -decrementoUmid, enderecoGerenciador)


class SensorCO2(Sensor):
    def __init__(self, id, co2Inicial, decrementoCO2, enderecoGerenciador):
        Sensor.__init__(self, id, co2Inicial, -decrementoCO2, enderecoGerenciador)
