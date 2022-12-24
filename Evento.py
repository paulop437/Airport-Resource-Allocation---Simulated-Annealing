class Evento:
    def __init__(self, id :int ,localizacao: str, num_elems: int, estimated_start_time: int, estimated_dur: int, estado: str,
        elems_on: int, dur: int, priority:int,type):
        self.id = id
        self.localizacao = localizacao # Gate
        self.num_elems = num_elems # Elementos necessários
        self.estimated_start_time = estimated_start_time
        self.estimated_dur = estimated_dur # Ticks necessários
        self.estado = estado # notstarttime ,  locationinuse , need_workers , wait_workers , active , ended
        self.elems_on = elems_on # Elementos no evento right now
        self.team = {}
        self.dur = dur # Ticks worked
        self.priority = priority
        self.type = type # DEPARTURE, ARRIVAL
        self.start_time = 0 #Tempo esperado para começar pode alterar se não houverem trabalhadores disponiveís
        self.estimated_end_time = estimated_start_time + estimated_dur
        self.waiting_time = 0
        self.end_time = 0

    def update_status(self, tempo: int, eventos_ativos: list, historico: dict, busy_locations: list):
        # Começou a hora
        if tempo == self.estimated_start_time:
            if self.localizacao in busy_locations:
                #Location is in use, must wait
                self.estado = "locationinuse"
                self.priority=4
            else:
                busy_locations += [self.localizacao]
                self.estado = 'need_workers'
            eventos_ativos.append(self)
        # Se tá á espera no local mas já ta livre
        elif self.estado == "locationinuse" and (self.localizacao not in busy_locations):
            busy_locations+=[self.localizacao]
            self.estado = 'need_workers'
        # Se estava ativo e já foi trabalhado, acabar e adicionar ao historico
        elif self.estado == 'active' and self.dur >= self.estimated_dur:
            self.estado = 'ended'
            self.end_time = tempo
            self.waiting_time = self.end_time - self.start_time
            busy_locations.remove(self.localizacao)
            if tempo not in historico.keys():
                historico[tempo] = [self]
            else:
                historico[tempo].append(self)
            eventos_ativos.remove(self)

        return eventos_ativos, historico, busy_locations

    def __str__(self):
        return "\033[30;44m"+"-----EVENTO_LOG-----\n" + 'ID: ' + str(self.id) + '\n'+ 'Localização: ' + str(self.localizacao) + '\n' \
               + 'Workers Needed: ' + str(
            self.num_elems) + '\n' + 'Current Workers:' + str(self.elems_on) + '\n' + 'Worked ticks: ' + str(self.dur) + '\n' + 'Ticks needed: ' + str(self.estimated_dur) + '\n' + 'State: ' + str(self.estado) \
               +'\n' + 'Waiting time: ' + str(self.waiting_time) + "\n--------------------\n" + "\033[m"

    def get_localizacao(self):
        return self.localizacao

    def get_num_elems(self):
        return self.num_elems

    def get_estimated_start_time(self):
        return self.estimated_start_time

    def get_estimated_dur(self):
        return self.estimated_dur

    def get_estado(self):
        return self.estado

    def get_elems_on(self):
        return self.elems_on

    def get_dur(self):
        return self.dur

    def add_to_elems_on(self, dur_atual):
        self.elems_on += 1
        if self.elems_on >= self.num_elems:
            self.estado = "active"
            self.start_time = dur_atual


    def set_elems_on(self, num_elems: int):
        self.elems_on = num_elems

    def inc_dur(self):
        self.dur += 1

    def set_estado(self, estado: str):
        self.estado = estado
