from gerenciador import Gerenciador
from sensor import SensorCO2, SensorTemperatura, SensorUmidade
from atuador import Atuador, AtuadorAquecedor, AtuadorResfriador, AtuadorUmidade, AtuadorCO2
from multiprocessing import Queue, Process, Lock, Event
#from threading import Thread, Lock, Event

if __name__ == "__main__":
    gerenciador = Gerenciador(nconexoes=8, host='127.0.0.1')

    portas = [(65100 + i) for i in range(9)]
    
    sensortemp = SensorTemperatura(id=1, temperaturaInicial=20, incrementoTemp=1, enderecoGerenciador=(gerenciador.host, portas[0]))
    sensorumid = SensorUmidade(id=2, umidadeInicial=10, incrementoUmid=-0.1, enderecoGerenciador=(gerenciador.host, portas[1]))
    sensorco2 = SensorCO2(id=3, co2Inicial=30, incrementoCO2=-0.1, enderecoGerenciador=(gerenciador.host, portas[2]))

    atuadorAquec = AtuadorResfriador(id=4, enderecoGerenciador=(gerenciador.host, portas[3]))
    atuadorResfr = AtuadorResfriador(id=5, enderecoGerenciador=(gerenciador.host, portas[4]))

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
    processoAtuadorAquec = Process(target=atuadorAquec.iniciaThreads, args=(temperaturas, atualizandoTemp))
    processoAtuadorResfr = Process(target=atuadorResfr.iniciaThreads, args=(temperaturas, atualizandoTemp))

    processoGerenciador.start()
    gerenciadorPronto.wait()
    processoSensorTemp.start()
    processoSensorUmid.start()
    processoSensorCO2.start()
    processoAtuadorAquec.start()
    processoAtuadorResfr.start()

    processoGerenciador.join()
    processoSensorTemp.join()
    processoSensorUmid.join()
    processoSensorCO2.join()
    processoAtuadorAquec.join()
    processoAtuadorResfr.join()