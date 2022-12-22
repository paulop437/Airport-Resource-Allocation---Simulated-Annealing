
class WorkLog:
    def __init__(self, dictionary = {}):
        self.dictionary = dictionary

    def add_event(self, event, workers):
        self.dictionary[event.id]['evento'] = event
        x= 1
        for worker in workers:
            self.dictionary[event.id][str('Trabalhador' , str(x))] = worker.nome
            self.dictionary[event.id]['inicio_evento'] = event.estimated_start_time
            self.dictionary[event.id]['fim_evento'] = event.estimated_start_time
            x+=1
