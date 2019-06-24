import socket
from time import sleep
from abc import ABC, abstractmethod

class Atuador(ABC):
    def __init__(self, id):
        self.id = id
        self.ligado = False
        self.conectado = False

    def processaSocket(self, gerenciador, porta, valores, atualizando):
        # estabelece um socket para se comunicar com o servidor através do protocolo TCP/IP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conexao:
            conexao.connect((gerenciador, porta))
            # mensagem de conexão
            mensagem = self.geraMensagem(tipo='COA', id_mensagem='0')
            conexao.sendall(mensagem)

            # aguarda uma confirmação de conexão do sensor ao gerenciador
            while not self.conectado:
                resposta = self.geraResposta(conexao)
                self.processaResposta(resposta)
                
            while self.conectado:
                # aguarda uma solicitação, pelo gerenciador, para ligar o atuador
                while not self.ligado:
                    resposta = self.geraResposta(conexao)
                    self.processaResposta(resposta)
                
                # atuador atuando
                self.atuacao(valores, atualizando, conexao)

    # gera o PDU da aplicação com cada campo separado por um caractere de espaço
    def geraMensagem(self, tipo, id_mensagem):
        id_atuador = str(self.id)
        mensagem = ' '.join([tipo, id_mensagem, id_atuador])
        tamanho = len(mensagem)
        # pdu = tamanho de 2 bytes + resto da mensagem
        pdu = '{:02d}'.format(tamanho) + mensagem
        return self.codificaMensagem(pdu)
        
    # gera a resposta recebida do servidor
    def geraResposta(self, conexao):
        # campo 'tamanho' ocupa 2 bytes
        tamanho = int(self.decodificaMensagem(conexao.recv(2)))
        respostabyte = conexao.recv(tamanho)
        resposta = self.decodificaMensagem(respostabyte)
        # lista com os dados da resposta
        listaDados = resposta.split(' ')
        # convertendo para dicionario: melhor legibilidade
        dictDados = {
            'tipo' : listaDados[0],
            'id_mensagem' : listaDados[1],
            'id_atuador' : listaDados[2]
        }
        return dictDados

    def codificaMensagem(self, mensagem):
        return mensagem.encode('ascii')
    
    def decodificaMensagem(self, mensagem):
        return mensagem.decode('ascii')

    def processaResposta(self, resposta):
        if (resposta['tipo'] == 'COA'\
            and resposta['id_mensagem'] == '1'\
            and resposta['id_atuador'] == str(self.id)):
            self.conectado = True
        
        elif (resposta['tipo'] == 'ACA'\
                and resposta['id_mensagem'] == '0'\
                and resposta['id_atuador'] == str(self.id)):
            self.ligado = True

        elif (resposta['tipo'] == 'DEA'\
                and resposta['id_mensagem'] == '1'\
                and resposta['id_atuador'] == str(self.id)):
            self.ligado = False

    @abstractmethod
    def atuacao(self, valores, atualizando, conexao):
        pass


class AtuadorTemperatura(Atuador):
    def __init__(self, id):
        Atuador.__init__(self, id)

    def atuacao(self, valores, atualizando, conexao):
        # atuador atuando
        while self.ligado:
            sleep(0.5)
            mensagem = self.geraMensagem(tipo='ACA', id_mensagem='4')
            conexao.sendall(mensagem)
            with atualizando:
                valores.put(valores.get() - 0.3)    

class AtuadorUmidade(Atuador):
    def __init__(self, id):
        Atuador.__init__(self, id)

    def atuacao(self, valores, atualizando, conexao):
        # atuador atuando
        while self.ligado:
            sleep(1)
            mensagem = self.geraMensagem(tipo='ACA', id_mensagem='5')
            conexao.sendall(mensagem)
            with atualizando:
                valores.put(valores.get() + 0.4) 

class AtuadorCO2(Atuador):
    def __init__(self, id):
        Atuador.__init__(self, id)

    def atuacao(self, valores, atualizando, conexao):
        # atuador atuando
        while self.ligado:
            sleep(1)
            mensagem = self.geraMensagem(tipo='ACA', id_mensagem='6')
            conexao.sendall(mensagem)
            with atualizando:
                valores.put(valores.get() + 0.4) 
