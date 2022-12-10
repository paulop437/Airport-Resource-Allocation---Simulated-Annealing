

class Trabalhador:

    def __init__(self, nome:str, localizacao: str, estado = 'aguarda'):
        self.nome = nome
        self.localizacao = localizacao
        #Estados: aguarda, moving , working , returning
        self.estado = estado
        self.time_till_arrival = 5000
        self.moving_to = ""

    def __str__(self):
        return 'Nome: ' + str(self.nome) + '\n' + 'Localização atual: ' + str(self.localizacao) + '\n' + 'Estado: ' + str(self.estado) + '\n' + 'ETA:' + str(self.time_till_arrival)