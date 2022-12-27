import json
import random

from math import exp
import matplotlib.pyplot as plt

import time



import networkx as nx
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
    """
    Obtém a soma de tempo que cada evento teve de esperar para começar.
    Se a soma for 0, devolve o valor 9999, pois este é demasiado alto para ser escolhido por simulated annealing.
    :param current_solution: Dicionário de todos os eventos num espaço de tempo.
    :return: A soma de tempo que cada evento teve de esperar para começar.
    """
    soma = 0
    for lista_eventos in current_solution.values():
        for evento in lista_eventos:
            soma += evento.waiting_time
    if soma == 0:
        soma = 9999
    return soma



def simulated_annealing(T_initial, T_min, alpha):

    with open("./graph.conf") as config_file:
        # Reading the configuration file
        config = json.load(config_file)
        # Test: printing config file
        # print("Configuração:", config)

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

        #Primeira solução
        current_solution = neighbor_evento(lista_vertex)
        current_obj_value = evaluate_eventos(current_solution)
        final_solution_value = current_obj_value
        T = T_initial

         # Initialize an empty list to store the objective function values
        obj_values = []
        temps = []
        x = 0

        while T > T_min:
            new_solution = neighbor_evento(lista_vertex)
            new_obj_value = evaluate_eventos(new_solution)
            print("Nova solução:", new_obj_value)
            delta = new_obj_value - current_obj_value

            if new_obj_value< final_solution_value:
                final_solution = new_solution
                final_solution_value = new_obj_value
            #Se o delta for negativo, o tempo de espera da nova solução é menor, por isso é aceite.
            if (delta < 0) and (new_obj_value > 0):
                current_solution = new_solution
                current_obj_value = new_obj_value
            else:
                p = exp(-delta / T)
                #Se a probabilidade for maior então muda de solução atual.
                if rand() < p and new_obj_value > 0:
                    current_solution = new_solution
                    current_obj_value = new_obj_value
            T = T * alpha
            obj_values.append(current_obj_value)
            # Store the temperature at each iteration
            temps.append(T)

            print("Solução atual:", evaluate_eventos(current_solution))
        print("Finnished")

        return final_solution, temps, obj_values


def neighbor_evento(lista_vertex):
    with open("./graph.conf") as config_file:
        # Reading the configuration file
        config = json.load(config_file)
        # Test: printing config file
        # print("Configuração:", config)

        equipa = []
        for membro in config['equipa']:
            equipa.append(Trabalhador(membro['id'],membro['nome'], membro['node0']))

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

        #São 45 eventos na amostra recolhida.
        while (len(historico) < 46):

            if stuck_number == len(eventos_ativos):
                stuck_counter += 1
            else:
                stuck_number = len(eventos_ativos)
            # Update eventos que começam/acabam agora
            for evento in eventos:
                eventos_ativos, historico, busy_locations = evento.update_status(x, eventos_ativos, historico
                                                                                 , busy_locations)

            #Verifica se a função está presa num loop sem solução e termina-o com um dicionário vazio.
            if stuck_counter > 1000:
                historico = {}
                break

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
                        evento.team = simulated_annealing_workers(equipa, evento, lista_vertex, 1000, 1, 0.99,x)

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
                            for worker_list in evento.team.values():
                                for worker in worker_list:
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
            else:
                idle_counter = 0
                for evento in eventos:
                    # Verificar o próximo evento a acontecer
                    if evento.estimated_start_time >= x:
                        x = (evento.estimated_start_time + skip_margin)
                        break

        return historico


def evaluate_worker(current_solution):
    """
    Soma todas as distâncais que os trabalhadores têm de precorrer até ao destino.
    :param current_solution: Lista de trabalhadores
    :return: Soma das distâncias até ao destino de cada trabalhador.
    """
    soma = 0
    for worker_list in current_solution.values():
        for worker in worker_list:
            soma += worker.time_till_arrival
    return soma


def neighbor_worker(current_solution, equipa, n_elems, evento, lista_vertex, tempo_atual):
    """
    Se o evento não tiver trabalhadores suficientes e houver trabalhadores disponíveis, este adiciona um.
    Se o trabalhador não estiver na solução, escolhe-se um à sorte, elimina-se e adiciona-se o anteriormente escolhido.
    Senão, randomiza-se a ordem da lista.
    :param current_solution: Lista de trabalhadores atual de um determinado evento.
    :param equipa: Lista total de trabalhadores.
    :param n_elems: Número de trabalhadores necessários para o evento.
    :param evento: Evento a ser trabalhado
    :param lista_vertex: Lista de vertices
    :return: Uma lista com a solução nova.
    """
    for worker in equipa:
        if len(current_solution)<n_elems and worker.estado == 'aguarda':
            worker.estado = "moving"
            worker.moving_to = evento
            worker.time_till_arrival = calcular_time_till_point(lista_vertex, worker, evento)
            if tempo_atual in current_solution.keys():
                current_solution[tempo_atual].append(worker)
            else:
                current_solution[tempo_atual] = [worker]
        elif worker.estado == "aguarda":
            if not worker in current_solution:
                worker_to_delete = random.randint(0,len(current_solution)-1)
                current_solution[tempo_atual][worker_to_delete].estado = "aguarda"
                current_solution[tempo_atual].pop(worker_to_delete)
                worker.estado = "moving"
                worker.moving_to = evento
                worker.time_till_arrival = calcular_time_till_point(lista_vertex, worker, evento)
                if tempo_atual in current_solution.keys():
                    current_solution[tempo_atual].append(worker)
                else:
                    current_solution[tempo_atual] = [worker]
            else:
                if tempo_atual in current_solution.keys():
                    random.shuffle(current_solution[tempo_atual])
        if tempo_atual in current_solution.keys():
            if len(current_solution[tempo_atual]) == n_elems:
                break

    return current_solution


def simulated_annealing_workers(equipa, evento, lista_vertex, T_initial, T_min, alpha, tempo_atual):
    n_necessary_workers = evento.num_elems
    assigned_workers = 0
    for worker in equipa:
        # Encontrar o melhor trabalhador livre
        if worker.estado == "aguarda":
            worker.estado = "moving"
            worker.moving_to = evento
            worker.time_till_arrival = calcular_time_till_point(lista_vertex, worker, evento)
            if tempo_atual in evento.team.keys():
                evento.team[tempo_atual].append(worker)
            else:
                evento.team[tempo_atual] = [worker]


            assigned_workers += 1
        # All the necessary workers have been assigned to the event they are on the way
        if assigned_workers >= n_necessary_workers:
            evento.estado = "wait_workers"
            break

    #Primeira solução
    current_solution = evento.team
    current_obj_value = evaluate_worker(current_solution)
    T = T_initial
    while T > T_min:
        new_solution = neighbor_worker(current_solution, equipa, n_necessary_workers, evento, lista_vertex, tempo_atual)
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


def walthrought_simulation():
    with open("./graph.conf") as config_file:
        # Reading the configuration file
        config = json.load(config_file)
        # Test: printing config file
        # print("Configuração:", config)

        equipa = []
        for membro in config['equipa']:
            equipa.append(Trabalhador(membro['id'],membro['nome'], membro['node0']))

        eventos = data_Process("./data.csv").get_events()

        #print(eventos[len(eventos)-1].estimated_start_time)

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
                                evento.team[x] = worker
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
                            for worker in evento.team.values():
                                worker['worker'].time_till_arrival = 5000
                                worker['worker'].estado = "aguarda"
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
                    for worker in evento.team.values():
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
                print("For simulation purposes, time was skipped to " , datetime.datetime.fromtimestamp(x) , ".")


def assign_workers(historico, equipa):
    for evento_list in historico.values():
        for evento in evento_list:
            for tempo in evento.team:
                for worker in evento.team[tempo]:
                    for final_worker in equipa:
                        if worker.id == final_worker.id:
                            final_worker.work_log[tempo] = evento
    return equipa

def worker_menu(equipa, historico, temps, obj_values, T_initial, T_min):
    while(True):
        print("1- Mostrar histórico.")
        print("2- Mostrar Work Log de um trabalhador.")
        print("3- Stats da solução.")
        print("4- Mostrar gráfico.")
        option = int(input("Selecione a opção que quer ->:"))
        if option == 1:
            print_historico(historico)
        elif option == 2:
            for index in range(len(equipa)):
                print(index+1,"-",equipa[index].nome)
            option = int(input("Selecione a opção que quer ->:"))+1
            print_work_log(equipa[option-1].work_log)
        elif option == 3:
            print_status(historico, equipa)
        elif option == 4:
            show_graph(temps, obj_values, T_initial, T_min)


def print_work_log(dicionario):
    for key in dicionario.keys():
        print("Data:",datetime.datetime.fromtimestamp(key))
        print("Localizacao:", dicionario[key].localizacao)


def print_historico(historico):
    for evento_list in historico.values():
        for evento in evento_list:
            print("ID do Evento:", evento.id)
            print("Hora de começar:", datetime.datetime.fromtimestamp(evento.start_time))
            print("Localização", evento.localizacao)
            print("------------")

def print_status(historico, equipa):
    soma = 0
    for lista_eventos in historico.values():
        for evento in lista_eventos:
            soma += evento.waiting_time

    print("Tempo total de espera:", soma)
    print("")
    media = 0
    num_trabs = 0
    print("Stats por trabalhador")
    for trabalhador in equipa:
        print("Nome:",trabalhador.nome)
        print("Número de eventos trabalhados:", len(trabalhador.work_log))
        dur = 0
        for evento in trabalhador.work_log.values():
            dur += evento.dur
        media += dur
        num_trabs +=1
        print("Tempo trabalhado", dur)
        print("---------------------")
    media = media/num_trabs
    print("Média total de tempo de trabalho por trabalhador:", media)


def show_graph(temps, obj_values, T_initial, T_min):
    # Create a figure and a subplot
    fig, ax = plt.subplots()

    temps.reverse()

    # Plot the data
    ax.plot(temps, obj_values)

    # Add a title, labels, and a legend
    ax.set_title("Simulated Annealing")
    ax.set_xlabel("Temperatura")
    ax.set_ylabel("Tempo total de espera")

    # Reverse the x-axis
    plt.xlim(right=T_initial, left=T_min)

    # Show the plot
    plt.show()

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
    T_initial, T_min = 1000, 1
    with open("./graph.conf") as config_file:
        # Reading the configuration file
        config = json.load(config_file)
        # Test: printing config file
        # print("Configuração:", config)

        equipa = []
        for membro in config['equipa']:
            equipa.append(Trabalhador(membro['id'],membro['nome'], membro['node0']))

        historico ,temps,obj_values = simulated_annealing( T_initial, T_min, 0.95)
        assign_workers(historico, equipa)

    worker_menu(equipa, historico, temps, obj_values, T_initial, T_min)




main()
