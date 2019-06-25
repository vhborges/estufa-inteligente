import socket
from decimal import Decimal
from time import sleep
from componente import Componente
from abc import ABC, abstractmethod
from threading import Thread, Event

class Atuador(Componente):
    def __init__(self, id, enderecoGerenciador):
        self.id = id
        self.enderecoGerenciador = enderecoGerenciador

    def iniciaThreads(self, valores, atualizando):
        conectado = Event()
        ligado = Event()

        atuador = Thread(target=self.atuacao, args=(valores, atualizando, conectado, ligado, ))
        comunicador = Thread(target=self.processaSocket, args=(conectado, ligado, ))

        atuador.start()
        comunicador.start()

        atuador.join()
        comunicador.join()

    def processaSocket(self, conectado, ligado):
        # estabelece um socket para se comunicar com o servidor através do protocolo TCP/IP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conexao:
            conexao.connect(self.enderecoGerenciador)
            # mensagem de conexão
            mensagem = self.geraMensagem(tipo='COA', id_mensagem='0', id_componente=str(self.id))
            conexao.sendall(mensagem)

            # aguarda uma confirmação de conexão do sensor ao gerenciador
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
            and resposta['id_atuador'] == str(self.id)):
            conectado.set() 
        ##mensagem para ativar o atuador 
        elif (resposta['tipo'] == 'ACA'\
                and resposta['id_mensagem'] == '0'\
                and resposta['id_atuador'] == str(self.id)):
            ligado.set()
            mensagem = self.geraMensagem(tipo='ACA', id_mensagem='1', id_componente=str(self.id))
            conexao.sendall(mensagem)
        ##mesnagem para desligar o atuador
        elif (resposta['tipo'] == 'DEA'\
                and resposta['id_mensagem'] == '0'\
                and resposta['id_atuador'] == str(self.id)):
            ligado.clear()
            mensagem = self.geraMensagem(tipo='DEA', id_mensagem='1', id_componente=str(self.id))
            conexao.sendall(mensagem)  
        #mensagem para desconectar o atuador
        elif (resposta['tipo'] == 'DCA'\
                and resposta['id_mensagem'] == '0'\
                and resposta['id_atuador'] == str(self.id)):
            ligado.clear() 
            conectado.clear()
            mensagem = self.geraMensagem(tipo='DCA', id_mensagem='1', id_componente=str(self.id))
            conexao.sendall(mensagem)

    @abstractmethod
    def atuacao(self, valores, atualizando, conectado, ligado):
        pass


class AtuadorResfriador(Atuador):
    def __init__(self, id, enderecoGerenciador):
        Atuador.__init__(self, id, enderecoGerenciador)

    #atuacao do resfriador
    def atuacao(self, valores, atualizando, conectado, ligado):
        conectado.wait()
        while conectado.is_set():
            while ligado.is_set():
                with atualizando:
                    tempAtual = valores.get()
                    valores.put(tempAtual - Decimal('0.3')) 
                sleep(0.5)
            ligado.wait() 

class AtuadorAquecedor(Atuador):
    def __init__(self, id, enderecoGerenciador):
        Atuador.__init__(self, id, enderecoGerenciador)

    #atuacao do aquecedor
    def atuacao(self, valores, atualizando, conectado, ligado):  
        conectado.wait()
        while conectado.is_set():
            with atualizando:
                tempAtual = valores.get()
                valores.put(tempAtual + Decimal('0.3')) 
            sleep(0.5) 

class AtuadorUmidade(Atuador):
    def __init__(self, id, enderecoGerenciador):
        Atuador.__init__(self, id, enderecoGerenciador)

    #atuacao do sistema de irrigacao
    def atuacao(self, valores, atualizando, conectado, ligado):     
        conectado.wait()
        while conectado.is_set():
            with atualizando:
                tempAtual = valores.get()
                valores.put(tempAtual + Decimal('0.3')) 
            sleep(0.5) 

class AtuadorCO2(Atuador):
    def __init__(self, id, enderecoGerenciador):
        Atuador.__init__(self, id, enderecoGerenciador)

    #atuacao do injetor de CO2
    def atuacao(self, valores, atualizando, conectado, ligado):
        conectado.wait()
        while conectado.is_set():
            with atualizando:
                tempAtual = valores.get()
                valores.put(tempAtual + Decimal('0.3')) 
            sleep(0.5) 
