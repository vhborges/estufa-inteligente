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
        #limiares de valores permitidos
        self.tempMaxResfriador = 40
        self.tempMinResfriador = 15
        self.tempMaxAquecedor = 35
        self.tempMinAquecedor = 10
        self.umidadeMin = 20
        self.umidadeMax = 50
        self.CO2min = 390
        self.CO2max = 410
    
    def iniciaThreads(self, portas, gerenciadorPronto):
        #declaração das threads juntamente com os Events que sinalizarão quando os servidores estiverem prontos
        #para receber conexões dos outros componentes
        servidorTempPronto = Event()
        sensorTemp = Thread(target=self.processaSocket, args=(portas[0], servidorTempPronto, None,))

        servidorUmidPronto = Event()
        sensorUmid = Thread(target=self.processaSocket, args=(portas[1], servidorUmidPronto, None,))

        servidorCO2Pronto = Event()
        sensorCO2 = Thread(target=self.processaSocket, args=(portas[2], servidorCO2Pronto, None,))

        servidorClientePronto = Event()
        cliente = Thread(target=self.processaCliente, args=(servidorClientePronto,))

        aquecedorAtuando = Event()
        servidorAquecedorPronto = Event()
        aquecedor = Thread(target=self.processaSocket, args=(portas[3], servidorAquecedorPronto, aquecedorAtuando,))

        resfriadorAtuando = Event()
        servidorResfriadorPronto = Event()
        resfriador = Thread(target=self.processaSocket, args=(portas[4], servidorResfriadorPronto, resfriadorAtuando,))

        irrigadorAtuando = Event()
        servidorIrrigadorPronto = Event()
        irrigador = Thread(target=self.processaSocket, args=(portas[5], servidorIrrigadorPronto, irrigadorAtuando,))

        injetorAtuando = Event()
        servidorInjetorPronto = Event()
        injetor = Thread(target=self.processaSocket, args=(portas[6], servidorInjetorPronto, injetorAtuando,))

        #inicia as threads
        sensorTemp.start()
        sensorUmid.start()
        sensorCO2.start()
        cliente.start()
        aquecedor.start()
        resfriador.start()
        irrigador.start()
        injetor.start()

        # aguarda até que todos os servidores estejam prontos
        #e então sinaliza que o gerenciador está pronto
        servidorTempPronto.wait()
        servidorUmidPronto.wait()
        servidorCO2Pronto.wait()
        servidorClientePronto.wait()
        servidorAquecedorPronto.wait()
        servidorResfriadorPronto.wait()
        servidorIrrigadorPronto.wait()
        servidorInjetorPronto.wait()
        gerenciadorPronto.set()

        #aguarda a finalização das threads
        sensorTemp.join()
        sensorUmid.join()
        sensorCO2.join()
        cliente.join()
        aquecedor.join()
        resfriador.join()
        irrigador.join()
        injetor.join()
    
    #processa o socket que receberá conexão dos outros componentes
    def processaSocket(self, porta, servidorPronto, componenteAtuando):
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
                
                # a depender do tipo de componente, redireciona para cada função específica
                while conectado.is_set():
                    if int(mensagem['id_componente']) in range(1, 4):
                        self.processaSensor(conexao, conectado, recebendo)
                    elif int(mensagem['id_componente']) in range(4, 8):
                        self.processaAtuador(conexao, conectado, mensagem['id_componente'], componenteAtuando)
                    elif int(mensagem['id_componente']) == 8:
                        self.processaCliente(servidorPronto)
                

    def processaSensor(self, conexao, conectado, recebendo):
        while recebendo.is_set():
            mensagem = self.recebeMensagem(conexao)
            self.processaMensagem(mensagem, conexao, conectado)
    
    def processaAtuador(self, conexao, conectado, id_componente, componenteAtuando):
        if id_componente == '4':
            self.monitoraAquecedor(conexao, conectado, componenteAtuando)
        elif id_componente == '5':
            self.monitoraResfriador(conexao, conectado, componenteAtuando)
        elif id_componente == '6':
            self.monitoraIrrigador(conexao, conectado, componenteAtuando)
        elif id_componente == '7':
            self.monitoraInjetor(conexao, conectado, componenteAtuando)
    
    def monitoraAquecedor(self, conexao, conectado, aquecedorAtuando):
        while not aquecedorAtuando.is_set():
            if self.temperatura <= self.tempMinAquecedor:
                # solicita acionamento do aquecedor
                mensagem = self.geraMensagem(tipo='ACA', id_mensagem='0', id_componente='4')
                conexao.sendall(mensagem)
                # aguarda a confirmação do acionamento
                resposta = self.recebeMensagem(conexao)
                self.processaMensagem(resposta, conexao, conectado)
                aquecedorAtuando.set()
        while aquecedorAtuando.is_set():
            if self.temperatura >= self.tempMaxAquecedor:
                # solicita desligamento do aquecedor
                mensagem = self.geraMensagem(tipo='DEA', id_mensagem='0', id_componente='4')
                conexao.sendall(mensagem)
                # aguarda a confirmação do desligamento
                resposta = self.recebeMensagem(conexao)
                self.processaMensagem(resposta, conexao, conectado)
                aquecedorAtuando.clear()

    def monitoraResfriador(self, conexao, conectado, resfriadorAtuando):
        while not resfriadorAtuando.is_set():
            if self.temperatura >= self.tempMaxResfriador:
                # solicita acionamento do resfriador
                mensagem = self.geraMensagem(tipo='ACA', id_mensagem='0', id_componente='5')
                conexao.sendall(mensagem)
                # aguarda a confirmação do acionamento
                resposta = self.recebeMensagem(conexao)
                self.processaMensagem(resposta, conexao, conectado)
                resfriadorAtuando.set()
        while resfriadorAtuando.is_set():
            if self.temperatura <= self.tempMinResfriador:
                # solicita desligamento do resfriador
                mensagem = self.geraMensagem(tipo='DEA', id_mensagem='0', id_componente='5')
                conexao.sendall(mensagem)
                # aguarda a confirmação do desligamento
                resposta = self.recebeMensagem(conexao)
                self.processaMensagem(resposta, conexao, conectado)
                resfriadorAtuando.clear()

    def monitoraIrrigador(self, conexao, conectado, irrigadorAtuando):
        while not irrigadorAtuando.is_set():
            if self.umidade <= self.umidadeMin:
                # solicita acionamento do irrigador
                mensagem = self.geraMensagem(tipo='ACA', id_mensagem='0', id_componente='6')
                conexao.sendall(mensagem)
                # aguarda a confirmação do acionamento
                resposta = self.recebeMensagem(conexao)
                self.processaMensagem(resposta, conexao, conectado)
                irrigadorAtuando.set()
        while irrigadorAtuando.is_set():
            if self.umidade >= self.umidadeMax:
                # solicita desligamento do irrigador
                mensagem = self.geraMensagem(tipo='DEA', id_mensagem='0', id_componente='6')
                conexao.sendall(mensagem)
                # aguarda a confirmação do desligamento
                resposta = self.recebeMensagem(conexao)
                self.processaMensagem(resposta, conexao, conectado)
                irrigadorAtuando.clear()

    def monitoraInjetor(self, conexao, conectado, injetorAtuando):
        while not injetorAtuando.is_set():
            if self.co2 <= self.CO2min:
                # solicita acionamento do injetor de CO2
                mensagem = self.geraMensagem(tipo='ACA', id_mensagem='0', id_componente='7')
                conexao.sendall(mensagem)
                # aguarda a confirmação do acionamento
                resposta = self.recebeMensagem(conexao)
                self.processaMensagem(resposta, conexao, conectado)
                injetorAtuando.set()
        while injetorAtuando.is_set():
            if self.co2 >= self.CO2max:
                # solicita desligamento do injetor de CO2
                mensagem = self.geraMensagem(tipo='DEA', id_mensagem='0', id_componente='7')
                conexao.sendall(mensagem)
                # aguarda a confirmação do desligamento
                resposta = self.recebeMensagem(conexao)
                self.processaMensagem(resposta, conexao, conectado)
                injetorAtuando.clear()

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
                self.temperatura = float(mensagem['valor'])
            if mensagem['id_componente'] == '2':
                self.umidade = float(mensagem['valor'])
            if mensagem['id_componente'] == '3':
                self.co2 = float(mensagem['valor'])

        elif (mensagem['tipo'] == 'COS' and mensagem['id_mensagem'] == '0'):
            confirmaConexao = self.geraMensagem(tipo='COS', id_mensagem='1', id_componente=mensagem['id_componente'])
            conexao.sendall(confirmaConexao)
            conectado.set()
        
        elif (mensagem['tipo'] == 'COA' and mensagem['id_mensagem'] == '0'):
            confirmaConexao = self.geraMensagem(tipo='COA', id_mensagem='1', id_componente=mensagem['id_componente'])
            conexao.sendall(confirmaConexao)
            conectado.set()
        
        #elif (mensagem['tipo'] == 'ACA' and mensagem['id_mensagem'] == '1'):
        #    if (mensagem['id_componente'] == '4'):
        #        self.aquecedorLigado = True
        #    elif (mensagem['id_componente'] == '5'):
        #        self.resfriadorLigado = True

        #elif (mensagem['tipo'] == 'DEA' and mensagem['id_mensagem'] == '1'):
        #    if (mensagem['id_componente'] == '4'):
        #        self.aquecedorLigado = False
        #    elif (mensagem['id_componente'] == '5'):
        #        self.resfriadorLigado = False
