import socket
from componente import Componente
from threading import Thread, Event
import os

class Cliente(Componente):
    def __init__(self, enderecoGerenciador):
        self.enderecoGerenciador = enderecoGerenciador
        self.id = None
        self.valor = None
        self.tipo = None
        self.unidade = None
        self.ativo = True
        self.solicitaLeitura = Event()
        self.recebeLeitura = Event()

    def iniciaThreads(self):
        comunicador = Thread(target=self.processaSocket)
        inputUsuario = Thread(target=self.recebeSensor)

        comunicador.start()
        inputUsuario.start()

    def processaSocket(self):
        # estabelece um socket para se comunicar com o servidor através do protocolo TCP/IP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conexao:
            conexao.connect(self.enderecoGerenciador)
            while self.ativo:
                self.solicitaLeitura.wait()
                # solicita uma leitura ao gerenciador
                mensagem = self.geraMensagem(tipo='LES', id_mensagem='0', id_componente=self.id)
                conexao.sendall(mensagem)
                # aguarda a resposta com o valor da leitura
                mensagem = self.recebeMensagem(conexao)
                self.processaMensagem(mensagem)

    def processaMensagem(self, mensagem):
        if (mensagem['tipo'] == 'LES'\
        and mensagem['id_mensagem'] == '1'\
        and mensagem['id_componente'] == str(self.id)):
            self.valor = mensagem['valor']
            self.recebeLeitura.set()
            self.solicitaLeitura.clear()
            self.recebeLeitura.clear()

    def exibeSensor(self, id):
        self.apaga()
        if(id == ''):
            id = None
        if(id == '1' or id == '2' or id == '3'):
            #self.processaSocket()
            if id == '1':
                tipo = 'temperatura'
                unidade = '°C'
            elif id == '2':
                tipo = 'umidade'
                unidade = '%'
            elif id == '3':
                tipo = 'CO2'
                unidade = 'ppm'
            print("\nO sensor de", tipo, "está marcando", self.valor, unidade, "\n")
        elif(id == None):
            print("\n\n")
        elif(id == 'sair'):
            exit()
        else:
            print("\nInsira um sensor válido!\n")

    # apaga a tela executando um comando a depender do sistema operacional utilizado
    def apaga(self):
        # caso o sistema operacional seja Windows
        if os.name == 'nt':
            os.system('cls')
        # caso contrário (Unix)
        else:
            os.system('clear')

    def recebeSensor(self):
        id = None
        while self.ativo:
            self.apaga()
            self.exibeSensor(id)
            print("1 - Sensor de Temperatura \n2 - Sensor de Umidade \n3 - Sensor de CO2\n")
            id = input("Escreva o identificador de um sensor e pressione ENTER para ver o valor do mesmo\n\
                            Escreva *sair* e pressione ENTER para encerrar o gerenciador e sair do programa\n")
            if id in ('1', '2', '3'):
                self.id = id
                self.solicitaLeitura.set()
                self.recebeLeitura.wait()