from sensor import SensorCO2, SensorTemperatura, SensorUmidade
import socket
#from threading import Thread, Lock
from multiprocessing import Queue, Process, Lock
from time import sleep
from decimal import Decimal

def gerenciador(nClientes, host, porta, conectado):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serv:
        serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serv.bind((host, porta))
        serv.listen(nClientes)
        print('aguardando conexão')
        conectado.release()
        conexao, cliente = serv.accept()
        with conexao:
            print('conectado por', cliente)
            print('aguardando mensagem')
            recebe = recebeMensagem(conexao)
            print('mensagem recebida', recebe['tipo'], recebe['id_mensagem'], recebe['id_sensor'])
            mensagem = geraMensagem(tipo='COS', id_mensagem='1', id_sensor=recebe['id_sensor'])
            conexao.sendall(mensagem)
            mensagem = geraMensagem(tipo='EVG', id_mensagem='0', id_sensor=recebe['id_sensor'])
            conexao.sendall(mensagem)
            while True:
                recebe = recebeMensagem(conexao)
                print(recebe['valor'])

def geraMensagem(tipo, id_mensagem, id_sensor, valor=''):
    if valor:
        mensagem = ' '.join([tipo, id_mensagem, id_sensor, valor])
    else:
        mensagem = ' '.join([tipo, id_mensagem, id_sensor])
    tamanho = len(mensagem)
    # pdu = tamanho de 2 bytes + resto da mensagem
    pdu = '{:02d}'.format(tamanho) + mensagem
    return codificaMensagem(pdu)

# gera a resposta recebida do cliente
def recebeMensagem(conexao):
    # campo 'tamanho' ocupa 2 bytes
    tamanho = int(decodificaMensagem(conexao.recv(2)))
    respostabyte = conexao.recv(tamanho)
    resposta = decodificaMensagem(respostabyte)
    # lista com os dados da resposta
    listaDados = resposta.split(' ')
    # convertendo para dicionario: melhor legibilidade
    dictDados = {
        'tipo' : listaDados[0],
        'id_mensagem' : listaDados[1],
        'id_sensor' : listaDados[2]
    }
    if len(listaDados) == 4:
        dictDados['valor'] = listaDados[3]
    return dictDados

def codificaMensagem(mensagem):
    return mensagem.encode('ascii')

def decodificaMensagem(mensagem):
    return mensagem.decode('ascii')


sensortemp = SensorTemperatura(1, 20);
porta = 65000
host = '127.0.0.1'

tempAmbiente = 20
incremento = Decimal('0.1')

temperaturas = Queue()
atualizandoTemp = Lock()

conectado = Lock()
conectado.acquire()

process1 = Process(target=gerenciador, args=(3, host, porta, conectado,))
process2 = Process(target=sensortemp.processaSocket, args=(host, porta, temperaturas, atualizandoTemp,))

process1.start()
with conectado:
    process2.start()

while True:
    tempAmbiente += incremento
    with atualizandoTemp:
        if not temperaturas.empty():
            temperaturas.get()
        temperaturas.put(tempAmbiente)
    sleep(0.5)

process1.join()
process2.join()
