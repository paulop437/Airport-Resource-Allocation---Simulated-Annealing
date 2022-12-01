
class Evento:

    def __init__(self, localizacao: str, num_elems: int, start_time: int, estimated_dur: int, estado: str, elems_on : int, dur : int):
        self.localizacao = localizacao
        self.num_elems = num_elems
        self.start_time =start_time
        self.estimated_dur =estimated_dur
        self.estado =estado
        self.elems_on = elems_on
        self.dur = dur


    def update_status(self, tempo:int, eventos_ativos : list, historico : dict):
        if self.start_time == tempo:
            self.estado = 'ativo'
            eventos_ativos.append(self)
        elif self.estado == 'ativo' and self.dur >= self.estimated_dur:
            self.estado = 'acabado'

            if tempo not in historico.keys():
                historico[tempo] = [self]
            else:
                historico[tempo].append(self)

            eventos_ativos.remove(self)
        return eventos_ativos, historico


    def __str__(self):
        return 'Localização: '+ str(self.localizacao) + '\n' + 'Número de trabalhadores: '+ str(self.num_elems) + '\n' +  str(self.dur) + '\n' + 'Estado: ' +str(self.estado)

    def get_localizacao(self):
        return self.localizacao

    def get_num_elems(self):
        return self.num_elems

    def get_start_time(self):
        return self.start_time

    def get_estimated_dur(self):
        return self.estimated_dur

    def get_estado(self):
        return self.estado

    def get_elems_on(self):
        return self.elems_on

    def get_dur(self):
        return self.dur

    def add_to_elems_on(self, num_elems:int):
        self.elems_on += num_elems

    def set_elems_on(self, num_elems:int):
        self.elems_on = num_elems

    def inc_dur(self):
        self.dur +=1

    def set_estado(self, estado :str):
        self.estado = estado

