from componente import Componente
import socket
from threading import Thread, Event
from time import sleep

class Gerenciador(Componente):
    def __init__(self, nconexoes, host):
        self.nconexoes = nconexoes
        self.host = host
        self.ativo = True
        self.temperatura = None
        self.umidade = None
        self.co2 = None
        #limiares de valores permitidos
        self.tempMaxResfriador = 40
        self.tempMinResfriador = 15
        self.tempMaxAquecedor = 35
        self.tempMinAquecedor = 10
        self.umidadeMin = 20
        self.umidadeMax = 50
        self.CO2min = 390
        self.CO2max = 410
        #sinaliza quando os atuadores devem ser ligados ou desligados
        self.ligaAquecedor = Event()
        self.desligaAquecedor = Event()
        self.ligaResfriador = Event()
        self.desligaResfriador = Event()
        self.ligaIrrigador = Event()
        self.desligaIrrigador = Event()
        self.ligaInjetor = Event()
        self.desligaInjetor = Event()
    
    #def iniciaThreads(self, porta, gerenciadorPronto):
    #    #inicia a thread do gerenciador
    #    Thread(target=self.processaSocket, args=(porta, gerenciadorPronto,)).start()
    #    
    #    Thread(target=self.processaCliente).start()
    
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
            while self.ativo:
                mensagem = self.recebeMensagem(conexao)
                self.processaMensagem(mensagem, conexao)
                
    def processaAtuador(self, conexao, id_atuador, ligaAtuador, desligaAtuador):
        while self.ativo:
            # aguarda a sinalização de que o atuador deve ser ligado
            ligaAtuador.wait()
            # solicita acionamento do atuador
            mensagem = self.geraMensagem(tipo='ACA', id_mensagem='0', id_componente=id_atuador)
            conexao.sendall(mensagem)

            # aguarda a sinalização de que o atuador deve ser desligado
            desligaAtuador.wait()
            # solicita desligamento do atuador
            mensagem = self.geraMensagem(tipo='DEA', id_mensagem='0', id_componente=id_atuador)
            conexao.sendall(mensagem)

    #def processaCliente(self):
    #    while self.ativo:
    #        sleep(2)
    #        print('Temperatura:', self.temperatura)
    #        print('Umidade:', self.umidade)
    #        print('CO2:', self.co2)
    
    def processaMensagem(self, mensagem, conexao):
        if (mensagem['tipo'] == 'EVG' and mensagem['id_mensagem'] == '1'):
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

        elif (mensagem['tipo'] == 'IDS' and mensagem['id_mensagem'] == '0'):
            solicitaLeitura = self.geraMensagem(tipo='EVG', id_mensagem='0', id_componente=mensagem['id_componente'])
            conexao.sendall(solicitaLeitura)
        
        elif (mensagem['tipo'] == 'DEG' and mensagem['id_mensagem'] == '0' and mensagem['id_componente'] == '8'):
            self.ativo = False
        
        elif (mensagem['tipo'] == 'IDA' and mensagem['id_mensagem'] == '0'):
            if mensagem['id_componente'] == '4':
                self.processaAtuador(conexao, '4', self.ligaAquecedor, self.desligaAquecedor)
            elif mensagem['id_componente'] == '5':
                self.processaAtuador(conexao, '5', self.ligaResfriador, self.desligaResfriador)
            elif mensagem['id_componente'] == '6':
                self.processaAtuador(conexao, '6', self.ligaIrrigador, self.desligaIrrigador)
            elif mensagem['id_componente'] == '7':
                self.processaAtuador(conexao, '7', self.ligaInjetor, self.desligaInjetor)

        elif (mensagem['tipo'] == 'LES' and mensagem['id_mensagem'] == '0'):
            valor = None
            if mensagem['id_componente'] == '1':
                valor = self.temperatura
            elif mensagem['id_componente'] == '2':
                valor = self.umidade
            elif mensagem['id_componente'] == '3':
                valor = self.co2
            retornaLeitura = self.geraMensagem(tipo='LES', id_mensagem='1', id_componente=mensagem['id_componente'], valor=str(valor))
            conexao.sendall(retornaLeitura)
