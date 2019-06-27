from gerenciador import Gerenciador
from sensor import SensorCO2, SensorTemperatura, SensorUmidade
from atuador import Atuador, Aquecedor, Resfriador, Irrigador, InjetorCO2
from multiprocessing import SimpleQueue, Process, Lock, Event
#from threading import Thread, Lock, Event

if __name__ == "__main__":
    porta = 65000
    
    #declaração dos componentes
    gerenciador = Gerenciador(nconexoes=8, host='127.0.0.1')
    sensortemp = SensorTemperatura(id=1, temperaturaInicial=20, incrementoTemp=1,\
                                   enderecoGerenciador=(gerenciador.host, porta,))
    sensorumid = SensorUmidade(id=2, umidadeInicial=40, incrementoUmid=-1,\
                               enderecoGerenciador=(gerenciador.host, porta,))
    sensorco2 = SensorCO2(id=3, co2Inicial=400, incrementoCO2=-1,\
                          enderecoGerenciador=(gerenciador.host, porta,))
    aquecedor = Aquecedor(id=4, incrementoTemp=1.5, enderecoGerenciador=(gerenciador.host, porta,))
    resfriador = Resfriador(id=5, decrementoTemp=1.5,enderecoGerenciador=(gerenciador.host, porta,))
    irrigador = Irrigador(id=6, incrementoUmid=1.5,enderecoGerenciador=(gerenciador.host, porta,))
    injetor = InjetorCO2(id=7, incrementoCO2=1.5,enderecoGerenciador=(gerenciador.host, porta,))

    #valores dos parametros da estufa
    temperaturas = SimpleQueue()
    umidades = SimpleQueue()
    co2 = SimpleQueue()

    #locks para garantir a correta atualização dos valores entre processos
    atualizandoTemp = Lock()
    atualizandoUmid = Lock()
    atualizandoCO2 = Lock()

    #permite iniciar os componentes somente quando o gerenciador (servidor) estiver pronto
    gerenciadorPronto = Event()

    #declaração dos processos
    processoGerenciador = Process(target=gerenciador.iniciaThreads, args=(porta, gerenciadorPronto,))
    processoSensorTemp = Process(target=sensortemp.iniciaThreads, args=(temperaturas, atualizandoTemp,))
    processoSensorUmid = Process(target=sensorumid.iniciaThreads, args=(umidades, atualizandoUmid,))
    processoSensorCO2 = Process(target=sensorco2.iniciaThreads, args=(co2, atualizandoCO2,))
    processoAquecedor = Process(target=aquecedor.iniciaThreads, args=(temperaturas, atualizandoTemp,))
    processoResfriador = Process(target=resfriador.iniciaThreads, args=(temperaturas, atualizandoTemp,))
    processoIrrigador = Process(target=irrigador.iniciaThreads, args=(umidades, atualizandoUmid,))
    processoInjetor = Process(target=injetor.iniciaThreads, args=(co2, atualizandoCO2,))

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
