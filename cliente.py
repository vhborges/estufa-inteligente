import socket
from componente import Componente
from time import sleep
from threading import Thread, Event
import os

class Cliente(Componente):
    def __init__(self):
        self.id = None
        self.valor = None
        self.tipo = None
        self.unidade = None
        #self.enderecoGerenciador = enderecoGerenciador

    def iniciaThreads(self, valores):
        conectado = Event()

        inputUsuario = Thread(target=self.recebeSensor, args=(valores, conectado,))
        comunicador = Thread(target=self.processaSocket, args=(conectado, ))

        inputUsuario.start()
        comunicador.start()

        inputUsuario.join()
        comunicador.join()

    def processaSocket(self):
        # estabelece um socket para se comunicar com o servidor através do protocolo TCP/IP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conexao:
            #conexao.connect(self.enderecoGerenciador)
            # mensagem de conexão
            mensagem = self.geraMensagem(tipo='LES', id_mensagem='0', id_componente=self.id)
            conexao.sendall(mensagem)
            mensagem = self.recebeMensagem(conexao)
            self.processaMensagem(mensagem, conexao)

    def processaMensagem(self, resposta, conexao):
        if (resposta['tipo'] == 'LES'\
            and resposta['id_mensagem'] == '1'\
            and resposta['id_componente'] == str(self.id)):
            self.valor = resposta['valor']
            self.recebeSensor()

    def exibeSensor(self):
        self.apaga()
        if(self.id == ''):
            self.id = None
        if(self.id == '1' or self.id == '2' or self.id == '3'):
            #self.processaSocket()
            if self.id == '1':
                self.tipo = 'temperatura'
                self.unidade = '°C'
            elif self.id == '2':
                self.tipo = 'umidade'
                self.unidade = '%'
            elif self.id == '3':
                self.tipo = 'CO2'
                self.unidade = 'ppm'
            print("\nO sensor de", self.tipo, "está marcando", self.valor, self.unidade, "\n")
        elif(self.id == None):
            print("\n\n")
        elif(self.id == 'sair'):
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
        self.apaga()
        self.exibeSensor()
        print("1 - Sensor de Temperatura \n2 - Sensor de Umidade \n3 - Sensor de CO2\n")
        self.id = input("Escreva o identificador de um sensor e pressione ENTER para ver o valor do mesmo\nEscreva *sair* e pressione ENTER para encerrar o gerenciador e sair do programa\n")


    
        