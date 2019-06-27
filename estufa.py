from gerenciador import Gerenciador
from sensor import SensorCO2, SensorTemperatura, SensorUmidade
from atuador import Atuador, Aquecedor, Resfriador, Irrigador, InjetorCO2
from cliente import Cliente
from multiprocessing import SimpleQueue, Process, Lock, Event
from threading import Thread

def main():
    # obtenção de valores de configuração da estufa
    incrementoTemp = obtemValores()
    limitesAquecedor, limitesResfriador, limitesUmidade, limitesCO2 = obtemLimites()
    #valores iniciais dos parâmetros da estufa
    temperatura = 30
    umidade = 35
    decrementoUmid = 0.7
    co2 = 400
    decrementoCO2 = 0.8
    incrementoAquec = 1.5
    decrementoResf = 1.5
    incrementoIrrig = 1.5
    incrementoInj = 1.5

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
    
    incrementoTemp = inputExcept("Digite o incremento da temperatura (entre -0.9 e 0.9): ")
    while not -0.9 <= incrementoTemp <= 0.9:
        print("Coloque um valor dentro da faixa especificada!")
        incrementoTemp = inputExcept("Digite o incremento da temperatura (entre -0.9 e 0.9): ")
    
    return incrementoTemp

def obtemLimites():
    print(("\nCONFIGURAÇÃO DO AQUECEDOR E RESFRIADOR\n"\
            "Valor máximo do aquecedor deve ser menor que o máximo do resfriador\n"\
            "Valor mínimo do aquecedor deve ser menor que o mínimo do resfriador"))
    tempMinAquecedor, tempMaxAquecedor = inputLimites("Digite o valor mínimo do aquecedor (recomendado = 10): ", "Digite o valor máximo do aquecedor (recomendado = 35): ")
    tempMinResfriador, tempMaxResfriador = inputLimites("Digite o valor mínimo do resfriador (recomendado = 15): ", "Digite o valor máximo do resfriador (recomendado = 40): ")
    while tempMinAquecedor >= tempMinResfriador or tempMaxAquecedor >= tempMaxResfriador:
        print("Os valores máximo e mínimo devem ser como especificados anteriormente!")
        tempMinAquecedor, tempMaxAquecedor = inputLimites("Digite o valor mínimo do aquecedor (recomendado = 10): ", "Digite o valor máximo do aquecedor (recomendado = 35): ")
        tempMinResfriador, tempMaxResfriador = inputLimites("Digite o valor mínimo do resfriador (recomendado = 15): ", "Digite o valor máximo do resfriador (recomendado = 40): ")

    print("\nCONFIGURAÇÃO DO IRRIGADOR")
    umidadeMin, umidadeMax = inputLimites("Digite o valor mínimo da umidade (recomendado = 20): ", "Digite o valor máximo da umidade (recomendado = 50): ")
    print("\nCONFIGURAÇÃO DO INJETOR DE CO2")
    CO2min, CO2max = inputLimites("Digite o valor mínimo do CO2 (recomendado = 390): ", "Digite o valor máximo do CO2 (recomendado = 410): ")
    return (tempMinAquecedor, tempMaxAquecedor), (tempMinResfriador, tempMaxResfriador), (umidadeMin, umidadeMax), (CO2min, CO2max)


if __name__ == "__main__":
    main()