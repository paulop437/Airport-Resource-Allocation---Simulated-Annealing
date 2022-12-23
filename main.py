import json
import random
import time
from math import exp

import networkx as nx
import matplotlib.pyplot as plt
import datetime

from numpy.random import rand

import nodes
import vertexs


from Trabalhador import Trabalhador
from data_process import data_Process


def print_frontier_nodes(description, frontier_nodes: list):
    print("+++++++++++++++++")
    print(description)
    for node in frontier_nodes:
        print("Name: ", node.get_name())
        print("Parent: ", node.get_parent().get_name())
        print("Total cost: ", node.get_total_cost())
        print("-*-")
    print("+++++++++++++++++")

def calcular_time_till_point(lista_vertex, worker, evento):
    # USING DIRECT PATH, NOT SHORTEST
    initial_position = worker.localizacao
    destination = evento.localizacao
    if initial_position == destination:
        return 0
    #print(worker.nome, initial_position, destination)
    for vertex in lista_vertex:
        if vertex.name == initial_position:
            if vertex.destination == destination:
                return vertex.cost
        elif vertex.name == destination:
            if vertex.destination == initial_position:
                return vertex.cost


def priority_order(eventos_ativos):
    eventos_ativos = sorted(eventos_ativos, key=lambda x: x.priority, reverse=True)
    return eventos_ativos

def starttime_order(eventos):
    eventos = sorted(eventos, key=lambda x: x.estimated_start_time, reverse=True)
    return eventos


def evaluate_eventos(current_solution):
    soma = 0
    for lista_eventos in current_solution.values():
        for evento in lista_eventos:
            soma += evento.waiting_time
    if soma == 0:
        soma = 9999
    return soma



def simulated_annealing(eventos, equipa,T_initial, T_min, alpha):

    with open("./graph.conf") as config_file:
        # Reading the configuration file
        config = json.load(config_file)
        # Test: printing config file
        # print("Configuração:", config)

        equipa = []
        for membro in config['equipa']:
            equipa.append(Trabalhador(membro['nome'], membro['node0']))

        eventos = data_Process("./data.csv").get_events()

        historico = {}

        idle_counter = 0
        max_idle = 10
        skip_margin = -5

        x = eventos[0].estimated_start_time + skip_margin
        eventos_ativos = []
        busy_locations = []

        nomes_nodes = []
        lista_edges = []

        lista_nos = []
        lista_vertex = []

        for node in config['connections']:
            lista_nos.append(nodes.Node(node['node1']))
            lista_vertex.append(vertexs.Vertex(node['node1'], node['node2'], node['cost']))

            nomes_nodes.append(node['node1'])
            lista_edges.append((node['node1'], node['node2']))

        g = nx.DiGraph()
        g.add_nodes_from(nomes_nodes)
        g.add_edges_from(lista_edges)

        #nx.draw_networkx(g, arrows=True, node_shape="s", node_color="white")
        # plt.show()


        # while (x < 1667954750):
        while (len(historico) < 46):

            # Update eventos que começam/acabam agora
            for evento in eventos:
                eventos_ativos, historico, busy_locations = evento.update_status(x, eventos_ativos, historico,
                                                                                 busy_locations)

            # Ordenar lista de eventos_ativos por priority
            eventos_ativos = priority_order(eventos_ativos)




            # Não há eventos ativos, não é preciso fazer qualquer decisão ou movimento
            if len(eventos_ativos) == 0:
                idle_counter += 1
            else:
                idle_counter = 0
                # Escolher trabalhadores que precisam de iniciar um movimento e dar-lhes assign a um evento
                for evento in eventos_ativos:
                    if evento.estado == "need_workers":
                        evento.team = simulated_annealing_workers(equipa, evento, lista_vertex, 5000,1,0.99)

                # Mover Trabalhadores, e atualizar evento se eles chegaram
                for worker in equipa:
                    if worker.estado == "moving":
                        worker.time_till_arrival -= 1
                        # Chegou ao destino
                        if worker.time_till_arrival <= 0:
                            worker.localizacao = worker.moving_to.localizacao
                            worker.moving_to.add_to_elems_on(x)
                            worker.time_till_arrival = 0
                            worker.estado = "working"
                            worker.moving_to = ""

                # Trabalhar eventos que teem todos os trabalhadores necessários, aka +1 tick
                for evento in eventos_ativos:
                    if evento.estado == "active":

                        evento.dur += 1
                        # Terminou o evento
                        if evento.dur >= evento.estimated_dur:
                            # Atualizar estado de trabalhadores quando evento acaba
                            for worker in evento.team:
                                worker.time_till_arrival = 5000
                                worker.estado = "aguarda"

                            # Atualizar estado do evento e adicionar ao historico
                            eventos_ativos, historico, busy_locations = evento.update_status(x, eventos_ativos, historico,
                                                                                             busy_locations)
                    elif evento.estado == "locationinuse":
                        if not evento.localizacao in busy_locations:
                            # Faz a verificação se o evento estiver na "lista de espera" e o local já não estiver a ser
                            # utilizado, coloca o evento seguinte na lista para need_workers
                            evento.estado = "need_workers"
                            busy_locations += [evento.localizacao]


            # Passagem de tempo ou time skip
            if idle_counter <= max_idle:
                x += 1
                # temp = input("Press enter to continue. \n")
            else:
                idle_counter = 0
                for evento in eventos:
                    # Verificar o próximo evento a acontecer
                    if evento.estimated_start_time >= x:
                        x = (evento.estimated_start_time + skip_margin)
                        break

        current_solution = historico
        current_obj_value = evaluate_eventos(current_solution)
        T = T_initial

        while T > T_min:
            new_solution = neighbor_evento(current_solution,nomes_nodes, lista_nos, lista_vertex)
            new_obj_value = evaluate_eventos(new_solution)
            print("Nova solução:", new_obj_value)
            print("Obj:", current_obj_value)
            delta = new_obj_value - current_obj_value
            if delta < 0 and new_obj_value > 0:
                current_solution = new_solution
                current_obj_value = new_obj_value
            else:
                p = exp(-delta / T)
                if rand() < p and new_obj_value > 0:
                    current_solution = new_solution
                    current_obj_value = new_obj_value
            T = T * alpha
            print("Solução atual:", evaluate_eventos(current_solution))
        print("Finnished")
        print(current_solution)
        return current_solution


def neighbor_evento(current_solution, nomes_nodes, lista_nos, lista_vertex):
    with open("./graph.conf") as config_file:
        # Reading the configuration file
        config = json.load(config_file)
        # Test: printing config file
        # print("Configuração:", config)

        equipa = []
        for membro in config['equipa']:
            equipa.append(Trabalhador(membro['nome'], membro['node0']))

        eventos = data_Process("./data.csv").get_events()


        historico = {}

        idle_counter = 0
        max_idle = 10
        skip_margin = -5

        x = eventos[0].estimated_start_time + skip_margin
        eventos_ativos = []
        busy_locations = []

        stuck_counter = 0
        stuck_number = 0
        #while (x < 1667954750):
        while (len(historico) < 45):

            #print("Tamanho do histórico:",len(historico))
            #print("Tamanho dos eventos ativos:",len(eventos_ativos))
            if stuck_counter >= 20:
                pass
            if stuck_number == len(eventos_ativos):
                stuck_counter += 1
            else:
                stuck_number = len(eventos_ativos)
            # Update eventos que começam/acabam agora
            for evento in eventos:
                eventos_ativos, historico, busy_locations = evento.update_status(x, eventos_ativos, historico,
                                                                                 busy_locations)
            if stuck_counter >1000:
                historico = {}
                break
                """for evento in eventos:
                    if not evento in historico.values():
                        #print("Tempo atual", x)
                        #print("Espectável",evento.estimated_start_time)
                        if x>evento.estimated_start_time:
                            #print("DEVIA INICIAR RIGHT?")
                            if evento.estado == 'ended':
                                historico[evento.id] = evento
                            print("Eventos ativos:",len(eventos_ativos))
                            if len(eventos_ativos) ==0:
                                print("Histórico:",len(historico))
                                print("Locais ocupados:", len(busy_locations))
                            print("Membros no evento:", len(evento.team))
                            if len(evento.team) == 0:
                                for membro in equipa:
                                    print("Estado dos membros da equipa total:",membro.estado)
                                    print("Localização do membro da equipa total:", membro.localizacao)
                            print("Localização do evento:",evento.localizacao)
                            print("Número de membros esperados:", evento.num_elems)
                            print("Duração atual do evento:",evento.dur)
                            print("Duração estimada:",evento.estimated_dur)
                            for member in evento.team:
                                print(member)"""

            # Ordenar lista de eventos_ativos por random
            n = len(eventos_ativos)
            if n:
                i = random.randint(0, n - 1)
                j = random.randint(0, n - 1)
                evento_temp = eventos_ativos[i]
                eventos_ativos[i] = eventos_ativos[j]
                eventos_ativos[j] = evento_temp


            # Não há eventos ativos, não é preciso fazer qualquer decisão ou movimento
            if len(eventos_ativos) == 0:
                idle_counter += 1
            else:
                idle_counter = 0
                # Escolher trabalhadores que precisam de iniciar um movimento e dar-lhes assign a um evento
                for evento in eventos_ativos:
                    if evento.estado == "need_workers":
                        evento.team = simulated_annealing_workers(equipa, evento, lista_vertex, 1000, 1, 0.99)

                # Mover Trabalhadores, e atualizar evento se eles chegaram
                for worker in equipa:
                    if worker.estado == "moving":
                        worker.time_till_arrival -= 1
                        # Chegou ao destino
                        if worker.time_till_arrival <= 0:
                            worker.localizacao = worker.moving_to.localizacao
                            worker.moving_to.add_to_elems_on(x)
                            worker.time_till_arrival = 0
                            worker.estado = "working"
                            worker.moving_to = ""

                # Trabalhar eventos que teem todos os trabalhadores necessários, aka +1 tick
                for evento in eventos_ativos:
                    if evento.estado == "active":
                        evento.dur += 1
                        # Terminou o evento
                        if evento.dur >= evento.estimated_dur:
                            # Atualizar estado de trabalhadores quando evento acaba
                            for worker in evento.team:
                                worker.time_till_arrival = 5000
                                worker.estado = "aguarda"

                            # Atualizar estado do evento e adicionar ao historico
                            eventos_ativos, historico, busy_locations = evento.update_status(x, eventos_ativos,
                                                                                             historico,
                                                                                             busy_locations)
                    elif evento.estado == "locationinuse":
                        if not evento.localizacao in busy_locations:
                            # Faz a verificação se o evento estiver na "lista de espera" e o local já não estiver a ser
                            # utilizado, coloca o evento seguinte na lista para need_workers
                            evento.estado = "need_workers"
                            busy_locations += [evento.localizacao]

            # Passagem de tempo ou time skip
            if idle_counter <= max_idle:
                x += 1
                # temp = input("Press enter to continue. \n")
            else:
                idle_counter = 0
                for evento in eventos:
                    # Verificar o próximo evento a acontecer
                    if evento.estimated_start_time >= x:
                        x = (evento.estimated_start_time + skip_margin)
                        break

        return historico


def evaluate_worker(current_solution):
    soma = 0
    for worker in current_solution:
        soma += worker.time_till_arrival
    return soma


def neighbor_worker(current_solution, equipa, n_elems, evento, lista_vertex):
    for worker in equipa:
        if len(current_solution)<n_elems and worker.estado == 'aguarda':
            worker.estado = "moving"
            worker.moving_to = evento
            worker.time_till_arrival = calcular_time_till_point(lista_vertex, worker, evento)
            current_solution+=[worker]
        elif worker.estado == "aguarda":
            if not worker in current_solution:
                worker_to_delete = random.randint(0,len(current_solution)-1)
                current_solution[worker_to_delete].estado = "aguarda"
                current_solution.pop(worker_to_delete)
                worker.estado = "moving"
                worker.moving_to = evento
                worker.time_till_arrival = calcular_time_till_point(lista_vertex, worker, evento)
                current_solution += [worker]
            else:
                random.shuffle(current_solution)
        if len(current_solution) == n_elems:
            break
    return current_solution


def simulated_annealing_workers(equipa, evento, lista_vertex, T_initial, T_min, alpha):
    n_necessary_workers = evento.num_elems
    assigned_workers = 0
    for worker in equipa:
        # Encontrar o melhor trabalhador livre
        if worker.estado == "aguarda":
            worker.estado = "moving"
            worker.moving_to = evento
            worker.time_till_arrival = calcular_time_till_point(lista_vertex, worker, evento)
            evento.team += [worker]
            assigned_workers += 1
        # All the necessary workers have been assigned to the event they are on the way
        if assigned_workers >= n_necessary_workers:
            evento.estado = "wait_workers"
            break

    # All the team has been checked, no workers are available, wait till next tick to try again
    current_solution = evento.team
    current_obj_value = evaluate_worker(current_solution)
    T = T_initial
    while T > T_min:
        new_solution = neighbor_worker(current_solution, equipa, n_necessary_workers, evento, lista_vertex)
        new_obj_value = evaluate_worker(new_solution)
        delta = new_obj_value - current_obj_value
        if delta < 0 and len(new_solution) == n_necessary_workers:
            current_solution = new_solution
            current_obj_value = new_obj_value
        else:
            p = exp(-delta / T)
            if rand() < p and len(new_solution) == n_necessary_workers:
                current_solution = new_solution
                current_obj_value = new_obj_value
        T = T * alpha
    return current_solution




def main():
    # Notes
    # Todo prework events

    # Todo limit number of events running on each location to 1 at a time

    # Todo randomize time needed and size of team needed based on event elements

    # Active events are reoordered based on priority, these will be assigned workers first
    # TODO Events on hold at a position should have top priority, followed by start time

    # Team currently been chosen by initial config order, not by distance or randomization

    # Workers do not return to base, they stay at their last position

    # Workers travel directly to their destination, the shortest path is not attempted

    # No graphical visualization

    #

    with open("./graph.conf") as config_file:
        # Reading the configuration file
        config = json.load(config_file)
        # Test: printing config file
        # print("Configuração:", config)

        equipa = []
        for membro in config['equipa']:
            equipa.append(Trabalhador(membro['nome'], membro['node0']))

        eventos = data_Process("./data.csv").get_events()

        #print(eventos[len(eventos)-1].estimated_start_time)
        simulated_annealing(eventos,equipa, 1000, 1, 0.99)

        """historico = {}


        idle_counter = 0
        max_idle = 10
        skip_margin = -5

        x = eventos[0].estimated_start_time + skip_margin
        eventos_ativos = []
        busy_locations = []

        nomes_nodes = []
        lista_edges = []

        lista_nos = []
        lista_vertex = []

        for node in config['connections']:
            lista_nos.append(nodes.Node(node['node1']))
            lista_vertex.append(vertexs.Vertex(node['node1'], node['node2'], node['cost']))

            nomes_nodes.append(node['node1'])
            lista_edges.append((node['node1'], node['node2']))

        g = nx.DiGraph()
        g.add_nodes_from(nomes_nodes)
        g.add_edges_from(lista_edges)

        nx.draw_networkx(g, arrows=True, node_shape="s", node_color="white")
        #plt.show()

        print("Size of event list : " + str(len(eventos)))
        #while (x < 1667954750):
        while (len(historico.values())<len(eventos)):

            # Update eventos que começam/acabam agora
            for evento in eventos:
                eventos_ativos, historico ,busy_locations = evento.update_status(x, eventos_ativos, historico, busy_locations)

            # Ordenar lista de eventos_ativos por priority
            eventos_ativos = priority_order(eventos_ativos)

            # Não há eventos ativos, não é preciso fazer qualquer decisão ou movimento
            if len(eventos_ativos) == 0:
                print("System on hold for events, the workers can rest.")
                idle_counter += 1
            else:
                idle_counter = 0
                # Escolher trabalhadores que precisam de iniciar um movimento e dar-lhes assign a um evento
                for evento in eventos_ativos:
                    if evento.estado == "need_workers":
                        n_necessary_workers = evento.num_elems
                        assigned_workers = 0
                        # TODO Ordenar equipa based on best statistics
                        for worker in equipa:
                            # Encontrar o melhor trabalhador livre
                            if worker.estado == "aguarda":
                                worker.estado = "moving"
                                worker.moving_to = evento
                                worker.time_till_arrival = calcular_time_till_point(lista_vertex, worker, evento)
                                evento.team += [worker]
                                assigned_workers += 1
                            # All the necessary workers have been assigned to the event they are on the way
                            if assigned_workers >= n_necessary_workers:
                                evento.estado = "wait_workers"
                                break
                        # All the team has been checked, no workers are available, wait till next tick to try again

                # Mover Trabalhadores, e atualizar evento se eles chegaram
                for worker in equipa:
                    if worker.estado == "moving":
                        worker.time_till_arrival -= 1
                        # Chegou ao destino
                        if worker.time_till_arrival <= 0:
                            worker.localizacao = worker.moving_to.localizacao
                            worker.moving_to.add_to_elems_on(x)
                            worker.time_till_arrival = 0
                            worker.estado = "working"
                            worker.moving_to = ""

                # Trabalhar eventos que teem todos os trabalhadores necessários, aka +1 tick
                for evento in eventos_ativos:
                    if evento.estado == "active":
                        evento.dur += 1
                        # Terminou o evento
                        if evento.dur >= evento.estimated_dur:
                            # Atualizar estado de trabalhadores quando evento acaba
                            print("Equipa atualizada")
                            for worker in evento.team:
                                worker.time_till_arrival = 5000
                                worker.estado = "aguarda"
                                print(worker)
                            # Atualizar estado do evento e adicionar ao historico
                            eventos_ativos, historico , busy_locations= evento.update_status(x, eventos_ativos, historico, busy_locations)
                    elif evento.estado == "locationinuse":
                        if not evento.localizacao in busy_locations:
                            #Faz a verificação se o evento estiver na "lista de espera" e o local já não estiver a ser
                            # utilizado, coloca o evento seguinte na lista para need_workers
                            evento.estado = "need_workers"
                            busy_locations += [evento.localizacao]

                # Mostrar console log de informação
                print('Eventos ativos:', )
                for evento in eventos_ativos:
                    print(evento)
                    for worker in evento.team:
                        print(worker)
                print('Current Time', datetime.datetime.fromtimestamp(x))
                print("History Size: " + str(len(historico.values())))
                print()

            # Passagem de tempo ou time skip
            if idle_counter <= max_idle:
                time.sleep(1)
                x += 1
                #temp = input("Press enter to continue. \n")
            else:
                idle_counter = 0
                for evento in eventos:
                    #Verificar o próximo evento a acontecer
                    if evento.estimated_start_time >= x:
                        x = (evento.estimated_start_time + skip_margin)
                        break
                print("For simulation purposes, time was skipped to " , datetime.datetime.fromtimestamp(x) , ".")"""




main()
