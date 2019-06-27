import socket
from componente import Componente
from threading import Thread, Event
import os

class Cliente(Componente):
    def __init__(self, enderecoGerenciador):
        self.enderecoGerenciador = enderecoGerenciador
        self.id = None
        self.valor = None
        #indica se o cliente está ativo... será False quando o usuário digitar 'sair'
        self.ativo = True
        #permitem sincronizar as leituras entre as threads 'comunicador' e 'inputUsuario'
        self.solicitaLeitura = Event()
        self.recebeLeitura = Event()

    def iniciaThreads(self, encerraApp):
        comunicador = Thread(target=self.processaSocket)
        inputUsuario = Thread(target=self.recebeSensor, args=(encerraApp,))

        comunicador.start()
        inputUsuario.start()

    def processaSocket(self):
        # estabelece um socket para se comunicar com o gerenciador através do protocolo TCP/IP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conexao:
            conexao.connect(self.enderecoGerenciador)
            # aguarda a primeira solicitação de leitura
            self.solicitaLeitura.wait()
            while self.ativo:
                # solicita uma leitura ao gerenciador
                mensagem = self.geraMensagem(tipo='LES', sequencia='0', id_componente=self.id)
                conexao.sendall(mensagem)
                # aguarda a resposta com o valor da leitura
                mensagem = self.recebeMensagem(conexao)
                self.processaMensagem(mensagem)
                # aguarda nova solicitação de leitura
                self.solicitaLeitura.wait()

    def processaMensagem(self, mensagem):
        if (mensagem['tipo'] == 'LES'\
        and mensagem['sequencia'] == '1'\
        and mensagem['id_componente'] == str(self.id)):
            self.valor = mensagem['valor']
            self.recebeLeitura.set()
            self.solicitaLeitura.clear()
            self.recebeLeitura.clear()

    def exibeSensor(self, id, encerraApp):
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
            self.ativo = False
            self.solicitaLeitura.set()
            encerraApp.set()
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

    # recebe do usuário o id do sensor a ser lido
    def recebeSensor(self, encerraApp):
        id = None
        while self.ativo:
            self.apaga()
            self.exibeSensor(id, encerraApp)
            print("1 - Sensor de Temperatura \n2 - Sensor de Umidade \n3 - Sensor de CO2\n")
            id = input("Escreva o identificador de um sensor e pressione ENTER para ver o valor do mesmo\nEscreva *sair* e pressione ENTER para encerrar o gerenciador e sair do programa\n")
            if id in ('1', '2', '3'):
                self.id = id
                self.solicitaLeitura.set()
                self.recebeLeitura.wait()