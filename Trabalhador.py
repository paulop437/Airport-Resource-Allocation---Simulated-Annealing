

class Trabalhador:

    def __init__(self, id, nome:str, localizacao: str, estado = 'aguarda'):
        self.id = id
        self.nome = nome
        self.localizacao = localizacao
        #Estados: aguarda, moving , working , returning
        self.estado = estado
        self.time_till_arrival = 5000
        self.moving_to = ""
        self.work_log = {}

    def __str__(self):
        return 'Nome: ' + str(self.nome) + '\n' + 'Localização atual: ' + str(self.localizacao) + '\n' + 'Estado: ' + str(self.estado) + '\n' + 'ETA:' + str(self.time_till_arrival)