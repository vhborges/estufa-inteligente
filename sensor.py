from componente import Componente
import socket
from time import sleep

class Sensor(Componente):
    def __init__(self, id):
        self.id = id
        self.valor = None
        self.conectado = False
        self.enviando = False
        
    def processaSocket(self, gerenciador, porta, valores, atualizandoTemp):
        # estabelece um socket para se comunicar com o servidor através do protocolo TCP/IP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conexao:
            conexao.connect((gerenciador, porta))
            # mensagem de conexão
            mensagem = self.geraMensagem(tipo='COS', id_mensagem='0', id_sensor=str(self.id))
            conexao.sendall(mensagem)

            # aguarda uma confirmação de conexão do sensor ao gerenciador
            while not self.conectado:
                resposta = self.recebeMensagem(conexao)
                self.processaMensagem(resposta)
                
            while self.conectado:
                # aguarda uma solicitação, pelo gerenciador, de envio dos dados
                while not self.enviando:
                    resposta = self.recebeMensagem(conexao)
                    self.processaMensagem(resposta)
                
                # envia o valor da leitura a cada 1s
                while self.enviando:
                    with atualizandoTemp:
                        self.valor = valores.get()
                    mensagem = self.geraMensagem(tipo='EVG', id_mensagem='1', id_sensor=str(self.id), valor=str(self.valor))
                    conexao.sendall(mensagem)
                    sleep(1)

    def processaMensagem(self, mensagem):
        if (mensagem['tipo'] == 'COS'\
            and mensagem['id_mensagem'] == '1'\
            and mensagem['id_sensor'] == str(self.id)):
            self.conectado = True
        
        elif (mensagem['tipo'] == 'EVG'\
              and mensagem['id_mensagem'] == '0'\
              and mensagem['id_sensor'] == str(self.id)):
            self.enviando = True
    
  
class SensorTemperatura(Sensor):
    def __init__(self, id):
        Sensor.__init__(self, id)

class SensorUmidade(Sensor):
    def __init__(self, id):
        Sensor.__init__(self, id)


class SensorCO2(Sensor):
    def __init__(self, id):
        Sensor.__init__(self, id)
