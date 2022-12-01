import json
import time
import networkx as nx
import matplotlib.pyplot as plt


import nodes
from Evento import Evento
from Trabalhador import Trabalhador


def print_frontier_nodes(description,frontier_nodes: list):

    print("+++++++++++++++++")
    print(description)
    for node in frontier_nodes:
        print("Name:",node.get_name())
        print("Parent:",node.get_parent().get_name())
        print("Total cost:",node.get_total_cost())
        print("-*-")
    print("+++++++++++++++++")

def escolha_custos(equipa: list, eventos: list ):

    return eventos, equipa



def main():
    with open("./graph.conf") as config_file:
        # Reading the configuration file
        config = json.load(config_file)
        # Test: printing config file
        print("Configuração:", config)

        equipa = []
        for membro in config['equipa']:
            equipa.append(Trabalhador(membro['nome'], membro['node0']))

        eventos = {
            1:{'localizacao':'Gate 1', 'num_elems':2, 'start_time':5,'estimated_dur':2, 'estado':'aguarda', 'elem_on':0, 'dur':0},
            2:{'localizacao':'Gate 1', 'num_elems':2, 'start_time':10,'estimated_dur':2, 'estado':'aguarda', 'elem_on':0, 'dur':0},
            3:{'localizacao':'Gate 1', 'num_elems':2, 'start_time':15,'estimated_dur':2, 'estado':'aguarda', 'elem_on':0, 'dur':0}
                   }
        historico = {}

        for key in eventos.keys():
            eventos[key] = Evento(eventos[key]['localizacao'], eventos[key]['num_elems'], eventos[key]['start_time'], eventos[key]['estimated_dur'], eventos[key]['estado'], eventos[key]['elem_on'], eventos[key]['dur'])


        x=0
        eventos_ativos = []
        nomes_nodes = []
        lista_edges = []

        for node in config['connections']:
            nomes_nodes.append(node['node1'])
            lista_edges.append((node['node1'],node['node2']))

        g = nx.DiGraph()
        g.add_nodes_from(nomes_nodes)
        g.add_edges_from(lista_edges)

        nx.draw_networkx(g, arrows=True, node_shape= "s", node_color = "white")
        plt.show()



        while (x<100):

            for evento in eventos.values():
                eventos_ativos, historico = evento.update_status(x, eventos_ativos,historico)

            #Chama método de escolha e distribuição de trabalhadores
            escolha_custos(equipa, eventos)

            print('Eventos ativos:',eventos_ativos)
            print('Tempo atual', x)
            print('Histórico',historico)
            print()


            time.sleep(1)
            x+=1





main()
