import socket
from time import sleep

class Sensor:
    def __init__(self, id, valor):
        self.id = id
        self.valor = valor
        self.conectado = False
        self.enviando = False
        
    def processaSocket(self, gerenciador, porta, valores):
        # estabelece um socket para se comunicar com o servidor através do protocolo TCP/IP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conexao:
            conexao.connect((gerenciador, porta))
            # mensagem de conexão
            mensagem = self.geraMensagem(tipo='COS', id_mensagem='0')
            mensagem = self.codificaMensagem(mensagem)
            conexao.sendall(mensagem)

            # aguarda uma confirmação de conexão do sensor ao gerenciador
            while not self.conectado:
                resposta = conexao.recv(7)
                resposta = self.decodificaMensagem(resposta)
                # cria uma lista com cada campo da resposta
                listaDados = resposta.split(' ')
                self.processaResposta(listaDados)
                
            while self.conectado:
                # aguarda uma solicitação, pelo gerenciador, de envio dos dados
                while not self.enviando:
                    resposta = conexao.recv(7)
                    resposta = self.decodificaMensagem(resposta)
                    listaDados = resposta.split(' ')
                    self.processaResposta(listaDados)
                
                # envia o valor da leitura a cada 1s
                while self.enviando:
                    sleep(1)
                    mensagem = self.geraMensagem(tipo='EVG', id_mensagem='1', valor=str(self.valor))
                    mensagem = self.codificaMensagem(mensagem)
                    conexao.sendall(mensagem)
                    self.valor = valores.get()

    # gera o datagrama com cada campo separado por um caractere de espaço
    def geraMensagem(self, tipo, id_mensagem, valor=''):
        id_sensor = str(self.id)
        if valor:
            return ' '.join([tipo, id_mensagem, id_sensor, valor])
        else:
            return ' '.join([tipo, id_mensagem, id_sensor])
    
    def codificaMensagem(self, mensagem):
        return mensagem.encode('ascii')
    
    def decodificaMensagem(self, mensagem):
        return mensagem.decode('ascii')
    
    def processaResposta(self, listaDados):
        if (listaDados[0] == 'COS'\
            and listaDados[1] == '1'\
            and listaDados[2] == str(self.id)):
            self.conectado = True
        
        elif (listaDados[0] == 'EVG'\
              and listaDados[1] == '0'\
              and listaDados[2] == str(self.id)):
            self.enviando = True
  
  
class SensorTemperatura(Sensor):
    def __init__(self, id, temperatura):
        Sensor.__init__(self, id, temperatura)

class SensorUmidade(Sensor):
    def __init__(self, id, umidade):
        Sensor.__init__(self, id, umidade)


class SensorCO2(Sensor):
    def __init__(self, id, co2):
        Sensor.__init__(self, id, co2)
