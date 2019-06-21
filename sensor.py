import socket
from time import sleep

class Sensor:
    def __init__(self, id, valor):
        self.id = id
        self.valor = valor
        self.conectado = False
        self.enviando = False
        
    def processaSocket(self, gerenciador, porta, valores, atualizandoTemp):
        # estabelece um socket para se comunicar com o servidor através do protocolo TCP/IP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conexao:
            conexao.connect((gerenciador, porta))
            # mensagem de conexão
            mensagem = self.geraMensagem(tipo='COS', id_mensagem='0')
            conexao.sendall(mensagem)

            # aguarda uma confirmação de conexão do sensor ao gerenciador
            while not self.conectado:
                resposta = self.geraResposta(conexao)
                self.processaResposta(resposta)
                
            while self.conectado:
                # aguarda uma solicitação, pelo gerenciador, de envio dos dados
                while not self.enviando:
                    resposta = self.geraResposta(conexao)
                    self.processaResposta(resposta)
                
                # envia o valor da leitura a cada 1s
                while self.enviando:
                    sleep(1)
                    mensagem = self.geraMensagem(tipo='EVG', id_mensagem='1', valor=str(self.valor))
                    conexao.sendall(mensagem)
                    with atualizandoTemp:
                        self.valor = valores.get()

    # gera o PDU da aplicação com cada campo separado por um caractere de espaço
    def geraMensagem(self, tipo, id_mensagem, valor=''):
        id_sensor = str(self.id)
        if valor:
            mensagem = ' '.join([tipo, id_mensagem, id_sensor, valor])
        else:
            mensagem = ' '.join([tipo, id_mensagem, id_sensor])
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
            'id_sensor' : listaDados[2]
        }
        return dictDados
    
    def codificaMensagem(self, mensagem):
        return mensagem.encode('ascii')
    
    def decodificaMensagem(self, mensagem):
        return mensagem.decode('ascii')
    
    def processaResposta(self, resposta):
        if (resposta['tipo'] == 'COS'\
            and resposta['id_mensagem'] == '1'\
            and resposta['id_sensor'] == str(self.id)):
            self.conectado = True
        
        elif (resposta['tipo'] == 'EVG'\
              and resposta['id_mensagem'] == '0'\
              and resposta['id_sensor'] == str(self.id)):
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
