from componente import Componente
import socket
from threading import Thread, Event
from time import sleep

class Gerenciador(Componente):
    def __init__(self, nconexoes, host, limitesAquecedor, limitesResfriador, limitesUmidade, limitesCO2):
        self.nconexoes = nconexoes
        self.host = host
        self.temperatura = None
        self.umidade = None
        self.co2 = None
        #limiares de valores permitidos
        self.tempMinAquecedor = limitesAquecedor[0]
        self.tempMaxAquecedor = limitesAquecedor[1]
        self.tempMinResfriador = limitesResfriador[0]
        self.tempMaxResfriador = limitesResfriador[1]
        self.umidadeMin = limitesUmidade[0]
        self.umidadeMax = limitesUmidade[1]
        self.CO2min = limitesCO2[0]
        self.CO2max = limitesCO2[1]
        #sinaliza quando os atuadores devem ser ligados ou desligados
        self.ligaAquecedor = Event()
        self.desligaAquecedor = Event()
        self.ligaResfriador = Event()
        self.desligaResfriador = Event()
        self.ligaIrrigador = Event()
        self.desligaIrrigador = Event()
        self.ligaInjetor = Event()
        self.desligaInjetor = Event()
    
    #processa o socket que receberá conexões dos outros componentes
    def processaSocket(self, porta, gerenciadorPronto):
        serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serv.bind((self.host, porta))
        serv.listen(self.nconexoes)
        gerenciadorPronto.set()
        while True:
            conexao = serv.accept()[0]
            Thread(target=self.processaConexao, args=(conexao,)).start()
        serv.close()

    def processaConexao(self, conexao):
        with conexao:
            while True:
                mensagem = self.recebeMensagem(conexao)
                self.processaMensagem(mensagem, conexao)
                
    def processaAtuador(self, conexao, id_atuador, ligaAtuador, desligaAtuador):
        while True:
            # aguarda a sinalização de que o atuador deve ser ligado
            ligaAtuador.wait()
            # solicita acionamento do atuador
            mensagem = self.geraMensagem(tipo='ACA', id_componente=id_atuador)
            conexao.sendall(mensagem)

            # aguarda a sinalização de que o atuador deve ser desligado
            desligaAtuador.wait()
            # solicita desligamento do atuador
            mensagem = self.geraMensagem(tipo='DEA', id_componente=id_atuador)
            conexao.sendall(mensagem)

    def processaMensagem(self, mensagem, conexao):
        if (mensagem['tipo'] == 'EVG' and mensagem['sequencia'] == '1'):
            if mensagem['id_componente'] == '1':
                self.temperatura = float(mensagem['valor'])
                if self.temperatura <= self.tempMinAquecedor:
                    self.ligaAquecedor.set()
                    self.desligaAquecedor.clear()
                elif self.temperatura <= self.tempMinResfriador:
                    self.desligaResfriador.set()
                    self.ligaResfriador.clear()
                if self.temperatura >= self.tempMaxResfriador:
                    self.ligaResfriador.set()
                    self.desligaResfriador.clear()
                elif self.temperatura >= self.tempMaxAquecedor:
                    self.desligaAquecedor.set()
                    self.ligaAquecedor.clear()
            if mensagem['id_componente'] == '2':
                self.umidade = float(mensagem['valor'])
                if self.umidade <= self.umidadeMin:
                    self.ligaIrrigador.set()
                    self.desligaIrrigador.clear()
                elif self.umidade >= self.umidadeMax:
                    self.desligaIrrigador.set()
                    self.ligaIrrigador.clear()
            if mensagem['id_componente'] == '3':
                self.co2 = float(mensagem['valor'])
                if self.co2 <= self.CO2min:
                    self.ligaInjetor.set()
                    self.desligaInjetor.clear()
                elif self.co2 >= self.CO2max:
                    self.desligaInjetor.set()
                    self.ligaInjetor.clear()

        elif mensagem['tipo'] == 'IDS':
            solicitaLeitura = self.geraMensagem(tipo='EVG', sequencia='0', id_componente=mensagem['id_componente'])
            conexao.sendall(solicitaLeitura)
        
        elif mensagem['tipo'] == 'IDA':
            if mensagem['id_componente'] == '4':
                self.processaAtuador(conexao, '4', self.ligaAquecedor, self.desligaAquecedor)
            elif mensagem['id_componente'] == '5':
                self.processaAtuador(conexao, '5', self.ligaResfriador, self.desligaResfriador)
            elif mensagem['id_componente'] == '6':
                self.processaAtuador(conexao, '6', self.ligaIrrigador, self.desligaIrrigador)
            elif mensagem['id_componente'] == '7':
                self.processaAtuador(conexao, '7', self.ligaInjetor, self.desligaInjetor)

        elif (mensagem['tipo'] == 'LES' and mensagem['sequencia'] == '0'):
            valor = None
            if mensagem['id_componente'] == '1':
                valor = self.temperatura
            elif mensagem['id_componente'] == '2':
                valor = self.umidade
            elif mensagem['id_componente'] == '3':
                valor = self.co2
            retornaLeitura = self.geraMensagem(tipo='LES', sequencia='1', id_componente=mensagem['id_componente'], valor=str(valor))
            conexao.sendall(retornaLeitura)
