from componente import Componente
import socket
#from threading import Thread, Lock

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
