from sensor import SensorCO2, SensorTemperatura, SensorUmidade
import socket
from multiprocessing import Queue, Process, Lock

def gerenciador(host, porta, tempAmbiente, temperaturas, conectado):
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
            recebe = con.recv(7)
            print('mensagem recebida', recebe)
            con.sendall(b'COS 1 1')
            con.sendall(b'EVG 0 1')
            while True:
                resposta = con.recv(10)
                resposta = resposta.decode('ascii')
                print(resposta.split(' ')[3])
                tempAmbiente = tempAmbiente + 1
                temperaturas.put(tempAmbiente)

sensortemp = SensorTemperatura(1, 20);
porta = 65000
host = '127.0.0.1'
tempAmbiente = 20

temperaturas = Queue()

conectado = Lock()
conectado.acquire()

process1 = Process(target=gerenciador, args=(host, porta, tempAmbiente, temperaturas, conectado))
process2 = Process(target=sensortemp.processaSocket, args=(host, porta, temperaturas))

process1.start()
conectado.acquire()
process2.start()
conectado.release()

process1.join()
process2.join()