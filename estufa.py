from gerenciador import Gerenciador
from sensor import SensorCO2, SensorTemperatura, SensorUmidade
from atuador import Atuador, Aquecedor, Resfriador, Irrigador, InjetorCO2
from cliente import Cliente
from multiprocessing import SimpleQueue, Process, Lock, Event
from threading import Thread

def main():
    # obtenção de valores de configuração da estufa
    temperatura, incrementoTemp, incrementoAquec, decrementoResf, umidade, decrementoUmid,\
    incrementoIrrig, co2, decrementoCO2, incrementoInj = obtemValores()
    limitesAquecedor, limitesResfriador, limitesUmidade, limitesCO2 = obtemLimites()

    # porta utilizada nas comunicações entre componentes
    porta = 65000
    
    #declaração dos componentes
    gerenciador = Gerenciador(8, '127.0.0.1', limitesAquecedor, limitesResfriador, limitesUmidade, limitesCO2)
    sensortemp = SensorTemperatura(1, temperatura, incrementoTemp, (gerenciador.host, porta,))
    sensorumid = SensorUmidade(2, umidade, decrementoUmid, (gerenciador.host, porta,))
    sensorco2 = SensorCO2(3, co2, decrementoCO2, (gerenciador.host, porta,))
    aquecedor = Aquecedor(4, incrementoAquec, (gerenciador.host, porta,))
    resfriador = Resfriador(5, decrementoResf, (gerenciador.host, porta,))
    irrigador = Irrigador(6, incrementoIrrig, (gerenciador.host, porta,))
    injetor = InjetorCO2(7, incrementoInj, (gerenciador.host, porta,))
    cliente = Cliente((gerenciador.host, porta,))

    #fila de valores dos parametros da estufa
    #usada para compartilhar os valores entre diferentes processos
    temperaturas = SimpleQueue()
    umidades = SimpleQueue()
    co2 = SimpleQueue()

    #locks para garantir a correta atualização dos valores entre processos
    atualizandoTemp = Lock()
    atualizandoUmid = Lock()
    atualizandoCO2 = Lock()

    #permite iniciar os componentes somente quando o gerenciador (servidor) estiver pronto
    gerenciadorPronto = Event()
    
    #permite encerrar a aplicação quando solicitado
    encerraApp = Event()

    #declaração dos processos
    processoGerenciador = Process(target=gerenciador.processaSocket, args=(porta, gerenciadorPronto,))
    processoSensorTemp = Process(target=sensortemp.iniciaThreads, args=(temperaturas, atualizandoTemp,))
    processoSensorUmid = Process(target=sensorumid.iniciaThreads, args=(umidades, atualizandoUmid,))
    processoSensorCO2 = Process(target=sensorco2.iniciaThreads, args=(co2, atualizandoCO2,))
    processoAquecedor = Process(target=aquecedor.iniciaThreads, args=(temperaturas, atualizandoTemp,))
    processoResfriador = Process(target=resfriador.iniciaThreads, args=(temperaturas, atualizandoTemp,))
    processoIrrigador = Process(target=irrigador.iniciaThreads, args=(umidades, atualizandoUmid,))
    processoInjetor = Process(target=injetor.iniciaThreads, args=(co2, atualizandoCO2,))
    threadCliente = Thread(target=cliente.iniciaThreads, args=(encerraApp,))

    #inicia o gerenciador e aguarda até que ele esteja pronto para receber conexões
    processoGerenciador.start()
    gerenciadorPronto.wait()

    # inicia os outros processos
    processoSensorTemp.start()
    processoSensorUmid.start()
    processoSensorCO2.start()
    processoAquecedor.start()
    processoResfriador.start()
    processoIrrigador.start()
    processoInjetor.start()
    threadCliente.start()

    # aguarda a sinalização de encerrar a aplicação
    encerraApp.wait()
    # finaliza os processos
    processoSensorTemp.terminate()
    processoAquecedor.terminate()
    processoResfriador.terminate()
    processoSensorUmid.terminate()
    processoIrrigador.terminate()
    processoSensorCO2.terminate()
    processoInjetor.terminate()
    processoGerenciador.terminate()

def inputExcept(str):
    while True:
        try:
            valor = float(input(str))
        except ValueError:
            print("Valor inválido!")
            continue
        break
    return valor

def inputLimites(str1, str2):
    valor1 = inputExcept(str1)
    valor2 = inputExcept(str2)
    while valor1 > valor2:
        print("Valor mínimo deve ser menor do que o máximo!")
        valor1 = inputExcept(str1)
        valor2 = inputExcept(str2)
    return valor1, valor2

def obtemValores():
    temperatura = inputExcept("Digite o valor da temperatura inicial: ")
    incrementoTemp = inputExcept("Digite o incremento da temperatura (positivo ou negativo): ")

    incrementoAquec = inputExcept("Digite o incremento do aquecedor (apenas positivo): ")
    while incrementoAquec < 0:
        print("Incremento do aquecedor deve ser positivo!")
        decrementoUmid = inputExcept("Digite o incremento do aquecedor: ")

    decrementoResf = inputExcept("Digite o decremento do resfriador (apenas positivo): ")
    while decrementoResf < 0:
        print("Decremento do resfriador deve ser positivo!")
        decrementoResf = inputExcept("Digite o decremento do resfriador: ")

    umidade = inputExcept("Digite o valor da umidade inicial: ")
    decrementoUmid = inputExcept("Digite o decremento da umidade (apenas positivo): ")
    while decrementoUmid < 0:
        print("Decremento da umidade deve ser positiva!")
        decrementoUmid = inputExcept("Digite o decremento da umidade: ")
    
    incrementoIrrig = inputExcept("Digite o incremento do irrigador (apenas positivo): ")
    while incrementoIrrig < 0:
        print("Incremento do irrigador deve ser positivo!")
        incrementoIrrig = inputExcept("Digite o incremento do irrigador: ")

    co2 = inputExcept("Digite o valor do CO2 inicial: ")
    decrementoCO2 = inputExcept("Digite o decremento do CO2 (apenas positivo): ")
    while decrementoCO2 < 0:
        print("Decremento do CO2 deve ser positivo!")
        decrementoUmid = inputExcept("Digite o decremento do CO2: ")
    
    incrementoInj = inputExcept("Digite o incremento do injetor de CO2 (apenas positivo): ")
    while incrementoInj < 0:
        print("Incremento do injetor deve ser positivo!")
        incrementoInj = inputExcept("Digite o incremento do injetor de CO2: ")
    
    return temperatura, incrementoTemp, incrementoAquec, decrementoResf,\
    umidade, decrementoUmid, incrementoIrrig, co2, decrementoCO2, incrementoInj

def obtemLimites():
    tempMinAquecedor, tempMaxAquecedor = inputLimites("Digite o valor mínimo do aquecedor: ", "Digite o valor máximo do aquecedor: ")
    tempMinResfriador, tempMaxResfriador = inputLimites("Digite o valor mínimo do resfriador: ", "Digite o valor máximo do resfriador: ")
    umidadeMin, umidadeMax = inputLimites("Digite o valor mínimo da umidade: ", "Digite o valor máximo da umidade: ")
    CO2min, CO2max = inputLimites("Digite o valor mínimo do CO2: ", "Digite o valor máximo do CO2: ")
    return (tempMinAquecedor, tempMaxAquecedor), (tempMinResfriador, tempMaxResfriador), (umidadeMin, umidadeMax), (CO2min, CO2max)


if __name__ == "__main__":
    main()