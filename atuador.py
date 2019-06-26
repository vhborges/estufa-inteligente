import socket
from decimal import Decimal
from time import sleep
from componente import Componente
from abc import ABC, abstractmethod
from threading import Thread, Event

class Atuador(Componente):
    def __init__(self, id, incremento, enderecoGerenciador):
        self.id = id
        self.enderecoGerenciador = enderecoGerenciador
        self.incremento = Decimal(str(incremento))

    def iniciaThreads(self, valores, atualizando):
        conectado = Event()
        ligado = Event()

        atuador = Thread(target=self.atuacao, args=(valores, atualizando, conectado, ligado, ))
        comunicador = Thread(target=self.processaSocket, args=(conectado, ligado, ))

        atuador.start()
        comunicador.start()

        atuador.join()
        comunicador.join()

    #atuacao do atuador (incrementa ou decrementa os valores, a depender das classes filhas)
    def atuacao(self, valores, atualizando, conectado, ligado):
        conectado.wait()
        while conectado.is_set():
            ligado.wait()
            while ligado.is_set():
                with atualizando:
                    tempAtual = valores.get()
                    valores.put(tempAtual + self.incremento) 
                sleep(0.5)

    def processaSocket(self, conectado, ligado):
        # estabelece um socket para se comunicar com o servidor através do protocolo TCP/IP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conexao:
            conexao.connect(self.enderecoGerenciador)
            # mensagem de conexão
            mensagem = self.geraMensagem(tipo='COA', id_mensagem='0', id_componente=str(self.id))
            conexao.sendall(mensagem)

            # aguarda uma confirmação de conexão do atuador ao gerenciador
            while not conectado.is_set():
                resposta = self.recebeMensagem(conexao)
                self.processaMensagem(resposta, conexao, conectado, ligado)
                
            while conectado.is_set():
                # aguarda uma solicitação, pelo gerenciador, para ligar o atuador
                while not ligado.is_set():
                    resposta = self.recebeMensagem(conexao)
                    self.processaMensagem(resposta, conexao, conectado, ligado)
                # atuador atuando
                while ligado.is_set():
                    resposta = self.recebeMensagem(conexao)
                    self.processaMensagem(resposta, conexao, conectado, ligado)
                

    def processaMensagem(self, resposta, conexao, conectado, ligado):
        #mensagem para conectar o atuador
        if (resposta['tipo'] == 'COA'\
            and resposta['id_mensagem'] == '1'\
            and resposta['id_componente'] == str(self.id)):
            conectado.set() 
        ##mensagem para ativar o atuador 
        elif (resposta['tipo'] == 'ACA'\
                and resposta['id_mensagem'] == '0'\
                and resposta['id_componente'] == str(self.id)):
            ligado.set()
            mensagem = self.geraMensagem(tipo='ACA', id_mensagem='1', id_componente=str(self.id))
            conexao.sendall(mensagem)
        ##mensagem para desligar o atuador
        elif (resposta['tipo'] == 'DEA'\
                and resposta['id_mensagem'] == '0'\
                and resposta['id_componente'] == str(self.id)):
            ligado.clear()
            mensagem = self.geraMensagem(tipo='DEA', id_mensagem='1', id_componente=str(self.id))
            conexao.sendall(mensagem)  
        #mensagem para desconectar o atuador
        elif (resposta['tipo'] == 'DCA'\
                and resposta['id_mensagem'] == '0'\
                and resposta['id_componente'] == str(self.id)):
            ligado.clear() 
            conectado.clear()
            mensagem = self.geraMensagem(tipo='DCA', id_mensagem='1', id_componente=str(self.id))
            conexao.sendall(mensagem)


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
