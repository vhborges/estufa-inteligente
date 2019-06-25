from gerenciador import Gerenciador
from sensor import SensorCO2, SensorTemperatura, SensorUmidade
from atuador import Atuador
from multiprocessing import Queue, Process, Lock, Event
#from threading import Thread, Lock

if __name__ == "__main__":
    gerenciador = Gerenciador(nconexoes=8, host='127.0.0.1')
    portas = [(65000 + i) for i in range(9)]
    sensortemp = SensorTemperatura(id=1, temperaturaInicial=20, incrementoTemp=0.1, enderecoGerenciador=(gerenciador.host, portas[0]))
    sensorumid = SensorUmidade(id=2, umidadeInicial=10, incrementoUmid=-0.1, enderecoGerenciador=(gerenciador.host, portas[1]))
    sensorco2 = SensorCO2(id=3, co2Inicial=30, incrementoCO2=-0.1, enderecoGerenciador=(gerenciador.host, portas[2]))

    temperaturas = Queue()
    umidades = Queue()
    co2 = Queue()
    atualizandoTemp = Lock()
    atualizandoUmid = Lock()
    atualizandoCO2 = Lock()

    gerenciadorPronto = Event()

    processoGerenciador = Process(target=gerenciador.iniciaThreads, args=(portas, gerenciadorPronto,))
    processoSensorTemp = Process(target=sensortemp.iniciaThreads, args=(temperaturas, atualizandoTemp))
    processoSensorUmid = Process(target=sensorumid.iniciaThreads, args=(umidades, atualizandoUmid))
    processoSensorCO2 = Process(target=sensorco2.iniciaThreads, args=(co2, atualizandoCO2))

    processoGerenciador.start()
    gerenciadorPronto.wait()
    processoSensorTemp.start()
    processoSensorUmid.start()
    processoSensorCO2.start()

    processoGerenciador.join()
    processoSensorTemp.join()
    processoSensorUmid.join()
    processoSensorCO2.join()