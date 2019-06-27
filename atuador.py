import socket
from decimal import Decimal
from time import sleep
from componente import Componente
from threading import Thread, Event

class Atuador(Componente):
    def __init__(self, id, incremento, enderecoGerenciador):
        self.id = id
        self.enderecoGerenciador = enderecoGerenciador
        self.incremento = Decimal(str(incremento))
        self.ligado = Event()

    def iniciaThreads(self, valores, atualizando):
        comunicador = Thread(target=self.processaSocket)
        atuador = Thread(target=self.atuacao, args=(valores, atualizando,))

        comunicador.start()
        atuador.start()

    #incrementa ou decrementa os valores a cada meio segundo, a depender do tipo do atuador (classes filhas)
    def atuacao(self, valores, atualizando):
        self.ligado.wait()
        while True:
            while self.ligado.is_set():
                with atualizando:
                    tempAtual = valores.get()
                    valores.put(tempAtual + self.incremento) 
                sleep(0.5)
            self.ligado.wait()

    def processaSocket(self):
        # estabelece um socket para se comunicar com o gerenciador através do protocolo TCP/IP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conexao:
            conexao.connect(self.enderecoGerenciador)
            # mensagem de identificação ao gerenciador
            mensagem = self.geraMensagem(tipo='IDA', id_componente=str(self.id))
            conexao.sendall(mensagem)

            # continuamente recebe mensagens do gerenciador (solicitação de atuação)
            while True:
                resposta = self.recebeMensagem(conexao)
                self.processaMensagem(resposta)
                

    # processa as mensagens recebidas do gerenciador
    def processaMensagem(self, mensagem):
        #mensagem para ativar o atuador 
        if (mensagem['tipo'] == 'ACA'\
        and mensagem['id_componente'] == str(self.id)):
            self.ligado.set()
        #mensagem para desligar o atuador
        elif (mensagem['tipo'] == 'DEA'\
        and mensagem['id_componente'] == str(self.id)):
            self.ligado.clear()


class Resfriador(Atuador):
    def __init__(self, id, decrementoTemp, enderecoGerenciador):
        Atuador.__init__(self, id, -decrementoTemp, enderecoGerenciador)

class Aquecedor(Atuador):
    def __init__(self, id, incrementoTemp, enderecoGerenciador):
        Atuador.__init__(self, id, incrementoTemp, enderecoGerenciador)

class Irrigador(Atuador):
    def __init__(self, id, incrementoUmid, enderecoGerenciador):
        Atuador.__init__(self, id, incrementoUmid, enderecoGerenciador)

class InjetorCO2(Atuador):
    def __init__(self, id, incrementoCO2, enderecoGerenciador):
        Atuador.__init__(self, id, incrementoCO2, enderecoGerenciador)
