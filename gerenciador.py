from componente import Componente
from sensor import SensorCO2, SensorTemperatura, SensorUmidade
import socket
#from threading import Thread, Lock
from multiprocessing import Queue, Process, Lock, Event
from time import sleep
from decimal import Decimal

class Gerenciador(Componente):
    def __init__(self, nclientes, host):
        self.nclientes = nclientes
        self.host = host
        self.temperatura = None
        self.umidade = None
        self.co2 = None
    
    def processaSocket(self, porta, servidorConfigurado):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serv:
            serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            serv.bind((self.host, porta))
            serv.listen(self.nclientes)
            print('aguardando conexão')
            servidorConfigurado.set()
            conexao, cliente = serv.accept()
            with conexao:
                print('conectado por', cliente)
                print('aguardando mensagem')
                mensagem = self.recebeMensagem(conexao)
                print('mensagem recebida', mensagem['tipo'], mensagem['id_mensagem'], mensagem['id_sensor'])
                self.processaMensagem(mensagem, conexao)
                while True:
                    mensagem = self.recebeMensagem(conexao)
                    self.processaMensagem(mensagem, conexao)
                    print(self.temperatura)
    
    def processaMensagem(self, mensagem, conexao):
        if (mensagem['tipo'] == 'EVG' and mensagem['id_mensagem'] == '1'):
            if mensagem['id_sensor'] == '1':
                self.temperatura = mensagem['valor']
            if mensagem['id_sensor'] == '2':
                self.umidade = mensagem['valor']
            if mensagem['id_sensor'] == '3':
                self.co2 = mensagem['valor']

        elif (mensagem['tipo'] == 'COS' and mensagem['id_mensagem'] == '0'):
            confirmaConexao = self.geraMensagem(tipo='COS', id_mensagem='1', id_sensor=mensagem['id_sensor'])
            conexao.sendall(confirmaConexao)
            solicitaLeitura = self.geraMensagem(tipo='EVG', id_mensagem='0', id_sensor=mensagem['id_sensor'])
            conexao.sendall(solicitaLeitura)

gerenciador = Gerenciador(3, '127.0.0.1')
sensortemp = SensorTemperatura(1)
porta = 65000

tempAmbiente = 20
incremento = Decimal('0.1')

temperaturas = Queue()
atualizandoTemp = Lock()

servidorConfigurado = Event()

process1 = Process(target=gerenciador.processaSocket, args=(porta, servidorConfigurado,))
process2 = Process(target=sensortemp.processaSocket, args=(gerenciador.host, porta, temperaturas, atualizandoTemp,))

process1.start()
servidorConfigurado.wait()
process2.start()

while True:
    tempAmbiente += incremento
    with atualizandoTemp:
        if not temperaturas.empty():
            temperaturas.get()
        temperaturas.put(tempAmbiente)
    sleep(0.5)

process1.join()
process2.join()
