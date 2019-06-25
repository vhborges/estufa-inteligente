from abc import ABC, abstractmethod

class Componente(ABC):
    
    @abstractmethod
    def processaMensagem(self, mensagem):
        pass

    #@abstractmethod
    #def processaSocket(self):
    #    pass

    # gera o PDU da aplicação com cada campo separado por um caractere de espaço
    def geraMensagem(self, tipo, id_mensagem, id_componente, valor=''):
        if valor:
            mensagem = ' '.join([tipo, id_mensagem, id_componente, valor])
        else:
            mensagem = ' '.join([tipo, id_mensagem, id_componente])
        tamanho = len(mensagem)
        # pdu = tamanho de 2 bytes + resto da mensagem
        pdu = '{:02d}'.format(tamanho) + mensagem
        return self.codificaMensagem(pdu)
    
    # recebe e processa a proxima mensagem recebida
    def recebeMensagem(self, conexao):
        # campo 'tamanho' ocupa 2 bytes
        tamanho = int(self.decodificaMensagem(conexao.recv(2)))
        respostabyte = conexao.recv(tamanho)
        resposta = self.decodificaMensagem(respostabyte)
        # lista com os dados da resposta
        listaDados = resposta.split(' ')
        # convertendo para dicionario: melhor legibilidade
        dictDados = {
            'tipo' : listaDados[0],
            'id_mensagem' : listaDados[1],
            'id_componente' : listaDados[2]
        }
        if len(listaDados) == 4:
            dictDados['valor'] = listaDados[3]
        return dictDados
    
    def codificaMensagem(self, mensagem):
        return mensagem.encode('ascii')
    
    def decodificaMensagem(self, mensagem):
        return mensagem.decode('ascii')