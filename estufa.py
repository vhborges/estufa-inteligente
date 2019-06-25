from gerenciador import Gerenciador
from sensor import SensorCO2, SensorTemperatura, SensorUmidade
from atuador import Atuador
from multiprocessing import Queue, Process, Lock, Event

if __name__ == "__main__":
    gerenciador = Gerenciador(nclientes=3, host='127.0.0.1')
    sensortemp = SensorTemperatura(id=1, temperaturaInicial=20, incrementoTemp=0.1, enderecoGerenciador=(gerenciador.host, 65000))

    temperaturas = Queue()
    atualizandoTemp = Lock()

    servidorConfigurado = Event()

    processoGerenciador = Process(target=gerenciador.processaSocket, args=(sensortemp.enderecoGerenciador[1], servidorConfigurado,))
    processoSensorTemp = Process(target=sensortemp.iniciaThreads, args=(temperaturas, atualizandoTemp))

    processoGerenciador.start()
    servidorConfigurado.wait()
    processoSensorTemp.start()

    processoGerenciador.join()
    processoSensorTemp.join()