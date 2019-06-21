from sensor import SensorCO2, SensorTemperatura, SensorUmidade
import socket
from multiprocessing import Queue, Process, Lock
from time import sleep
from decimal import Decimal

def gerenciador(host, porta, conectado):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serv:
        serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serv.bind((host, porta))
        serv.listen(10)
        print('aguardando conexão')
        conectado.release()
        con, cliente = serv.accept()
        with con:
            print('conectado por', cliente)
            print('aguardando mensagem')
            tamanho = int(con.recv(2).decode('ascii'))
            recebe = con.recv(tamanho)
            print('mensagem recebida', recebe.decode('ascii'))
            con.sendall(b'07COS 1 1')
            con.sendall(b'07EVG 0 1')
            while True:
                tamanho = int(con.recv(2).decode('ascii'))
                resposta = con.recv(tamanho)
                resposta = resposta.decode('ascii')
                temperatura = resposta.split(' ')[3]
                print(temperatura)

sensortemp = SensorTemperatura(1, 20);
porta = 65000
host = '127.0.0.1'

tempAmbiente = 20
incremento = Decimal('0.1')

temperaturas = Queue()
atualizandoTemp = Lock()

conectado = Lock()
conectado.acquire()

process1 = Process(target=gerenciador, args=(host, porta, conectado))
process2 = Process(target=sensortemp.processaSocket, args=(host, porta, temperaturas, atualizandoTemp))

process1.start()
conectado.acquire()
process2.start()
conectado.release()

while True:
    tempAmbiente += incremento
    with atualizandoTemp:
        if not temperaturas.empty():
            temperaturas.get()
        temperaturas.put(tempAmbiente)
    sleep(0.5)

process1.join()
process2.join()
