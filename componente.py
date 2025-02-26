from abc import ABC, abstractmethod

class Componente(ABC):
    
    @abstractmethod
    def processaMensagem(self, mensagem):
        pass

    @abstractmethod
    def processaSocket(self):
        pass

    # gera o PDU da aplicação com cada campo separado por um caractere de espaço
    # sequencia ou valor podem não existir em algumas mensagens (default = None)
    def geraMensagem(self, tipo, id_componente, sequencia=None, valor=None):
        # mensagem = dados (válidos) separados por um caractere de espaço
        mensagem = ' '.join(filter(None, [tipo, id_componente, sequencia, valor]))
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
            'id_componente' : listaDados[1]
        }
        if len(listaDados) > 2:
            dictDados['sequencia'] = listaDados[2]
        if len(listaDados) == 4:
            dictDados['valor'] = listaDados[3]
        return dictDados
    
    # conexão somente aceita bytestrings
    def codificaMensagem(self, mensagem):
        return mensagem.encode('ascii')
    
    # retorna ao formato padrão de string
    def decodificaMensagem(self, mensagem):
        return mensagem.decode('ascii')