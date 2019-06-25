from gerenciador import Gerenciador
from sensor import SensorCO2, SensorTemperatura, SensorUmidade
from atuador import Atuador
from multiprocessing import Queue, Process, Lock, Event
#from threading import Thread, Lock

if __name__ == "__main__":
    gerenciador = Gerenciador(nconexoes=8, host='127.0.0.1')
    portas = [(65000 + i) for i in range(9)]
    sensortemp = SensorTemperatura(id=1, temperaturaInicial=20, incrementoTemp=0.1, enderecoGerenciador=(gerenciador.host, portas[0]))

    temperaturas = Queue()
    atualizandoTemp = Lock()

    gerenciadorPronto = Event()

    processoGerenciador = Process(target=gerenciador.iniciaThreads, args=(portas, gerenciadorPronto,))
    processoSensorTemp = Process(target=sensortemp.iniciaThreads, args=(temperaturas, atualizandoTemp))

    processoGerenciador.start()
    gerenciadorPronto.wait()
    processoSensorTemp.start()

    processoGerenciador.join()
    processoSensorTemp.join()