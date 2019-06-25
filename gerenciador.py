from componente import Componente
import socket
from threading import Thread, Event
from time import sleep

class Gerenciador(Componente):
    def __init__(self, nconexoes, host):
        self.nconexoes = nconexoes
        self.host = host
        self.temperatura = None
        self.umidade = None
        self.co2 = None
    
    def iniciaThreads(self, portas, gerenciadorPronto):
        servidorTempPronto = Event()
        sensorTemp = Thread(target=self.processaSocket, args=(portas[0], servidorTempPronto,))

        servidorUmidPronto = Event()
        sensorUmid = Thread(target=self.processaSocket, args=(portas[1], servidorUmidPronto,))

        servidorCO2Pronto = Event()
        sensorCO2 = Thread(target=self.processaSocket, args=(portas[2], servidorCO2Pronto,))

        servidorClientePronto = Event()
        cliente = Thread(target=self.processaCliente, args=(servidorClientePronto,))

        sensorTemp.start()
        sensorUmid.start()
        sensorCO2.start()
        cliente.start()
        servidorTempPronto.wait()
        servidorUmidPronto.wait()
        servidorCO2Pronto.wait()
        servidorClientePronto.wait()
        gerenciadorPronto.set()

        sensorTemp.join()
        sensorUmid.join()
        sensorCO2.join()
        cliente.join()
    
    def processaSocket(self, porta, servidorPronto):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serv:
            serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            serv.bind((self.host, porta))
            serv.listen(self.nconexoes)
            servidorPronto.set()
            print('aguardando conexão')
            conexao, cliente = serv.accept()
            with conexao:
                print('conectado por', cliente)
                conectado = Event()
                recebendo = Event()
                print('aguardando solicitação de conexão')
                while not conectado.is_set():
                    mensagem = self.recebeMensagem(conexao)
                    print('mensagem recebida', mensagem['tipo'], mensagem['id_mensagem'], mensagem['id_componente'])
                    self.processaMensagem(mensagem, conexao, conectado)

                solicitaLeitura = self.geraMensagem(tipo='EVG', id_mensagem='0', id_componente=mensagem['id_componente'])
                conexao.sendall(solicitaLeitura)
                recebendo.set()
                
                while conectado.is_set():
                    if int(mensagem['id_componente']) in range(1, 4):
                        self.processaSensor(conexao, conectado, recebendo)
                    elif int(mensagem['id_componente']) in range(4, 8):
                        self.processaAtuador(conexao, conectado)
                    elif int(mensagem['id_componente']) == 8:
                        self.processaCliente(servidorPronto)
                

    def processaSensor(self, conexao, conectado, recebendo):
        while recebendo.is_set():
            mensagem = self.recebeMensagem(conexao)
            self.processaMensagem(mensagem, conexao, conectado)
    
    def processaAtuador(self, conexao, conectado):
        pass

    def processaCliente(self, servidorPronto):
        servidorPronto.set()
        while True:
            sleep(2)
            print('Temperatura:', self.temperatura)
            print('Umidade:', self.umidade)
            print('CO2:', self.co2)
    
    def processaMensagem(self, mensagem, conexao, conectado):
        if (mensagem['tipo'] == 'EVG' and mensagem['id_mensagem'] == '1'):
            if mensagem['id_componente'] == '1':
                self.temperatura = mensagem['valor']
            if mensagem['id_componente'] == '2':
                self.umidade = mensagem['valor']
            if mensagem['id_componente'] == '3':
                self.co2 = mensagem['valor']

        elif (mensagem['tipo'] == 'COS' and mensagem['id_mensagem'] == '0'):
            confirmaConexao = self.geraMensagem(tipo='COS', id_mensagem='1', id_componente=mensagem['id_componente'])
            conexao.sendall(confirmaConexao)
            conectado.set()
