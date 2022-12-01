

class Trabalhador:

    def __init__(self, nome:str, localizacao: str, estado = 'aguarda'):
        self.nome = nome
        self.localizacao =localizacao
        #Estados: aguarda, moving, livre, returning
        self.estado = estado

    def __str__(self):
        return 'Nome: ' + str(self.nome) + '\n' + 'Localização atual: ' + str(self.localizacao) + '\n' + 'Estado: ' + str(self.estado)