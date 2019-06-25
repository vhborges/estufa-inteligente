import socket
from componente import Componente
from time import sleep
from threading import Thread, Event
import os

class Cliente(Componente):
    def __init__(self, id, valor, tipo, enderecoGerenciador):
        self.id = id
        self.valor = valor
        self.tipo = tipo
        self.enderecoGerenciador = enderecoGerenciador

    def iniciaThreads(self, valores, atualizando):
        conectado = Event()

        inputUsuario = Thread(target=self.recebeSensor, args=(valores, atualizando, conectado,))
        comunicador = Thread(target=self.processaSocket, args=(conectado, ))

        inputUsuario.start()
        comunicador.start()

        inputUsuario.join()
        comunicador.join()

    def processaSocket(self):
        # estabelece um socket para se comunicar com o servidor através do protocolo TCP/IP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conexao:
            conexao.connect(self.enderecoGerenciador)
            # mensagem de conexão
            mensagem = self.geraMensagem(tipo='LES', id_mensagem='0', id_componente=self.id)
            conexao.sendall(mensagem)
            mensagem = self.recebeMensagem(conexao)
            self.processaResposta(mensagem, conexao)

    def processaResposta(self, resposta, conexao):
        if (resposta['tipo'] == 'LES'\
            and resposta['id_mensagem'] == '1'\
            and resposta['id_componente'] == str(self.id)):
            self.valor = resposta['valor']
            if resposta['id_componente'] == '1':
                self.tipo = 'temperatura'
            elif resposta['id_componente'] == '2':
                self.tipo = 'umidade'
            elif resposta['id_componente'] == '3':
                self.tipo = 'CO2'
            self.recebeSensor()

    def exibeSensor(self):
        if(self.id == '1' or self.id == '2' or self.id == '3'):
            self.processaSocket()
            print("\nO sensor de", self.tipo, "está marcando", self.valor, "\n")
        elif(self.id == -1):
            print("\n")
        else:
            print("Insira um sensor válido!")

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
        self.id = input("Escreva o identificador de um sensor e pressione ENTER para ver o valor do mesmo\n")


    
        