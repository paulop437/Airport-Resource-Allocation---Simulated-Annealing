import json
import time
import networkx as nx
import matplotlib.pyplot as plt
import datetime

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
    print(worker.nome, initial_position, destination)
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
    eventos = sorted(eventos, key=lambda x: x.start_time, reverse=True)
    return eventos


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

        #print(eventos[len(eventos)-1].start_time)

        historico = {}


        idle_counter = 0
        max_idle = 10
        skip_margin = -5

        x = eventos[0].start_time + skip_margin
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
                            worker.moving_to.add_to_elems_on()
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
                #print('Histórico', historico)
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
                    if evento.start_time >= x:
                        x = (evento.start_time + skip_margin)
                        break
                print("For simulation purposes, time was skipped to " , datetime.datetime.fromtimestamp(x) , ".")



main()
