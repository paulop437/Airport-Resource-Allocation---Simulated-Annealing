import json

import nodes

def print_frontier_nodes(description,frontier_nodes: list):

    print("+++++++++++++++++")
    print(description)
    for node in frontier_nodes:
        print("Name:",node.get_name())
        print("Parent:",node.get_parent().get_name())
        print("Total cost:",node.get_total_cost())
        print("-*-")
    print("+++++++++++++++++")


def main():
    with open("./graph.conf") as config_file:
        # Reading the configuration file
        config = json.load(config_file)
        # Test: printing config file
        print("Configuração:", config)

        root = nodes.Node("Gate 9", None, 0)
        # All connections to Lisboa
        frontier_nodes = []
        open_nodes = []
        for connection in config["connections"]:
            if connection["node1"] == "Balcao de Vendas":
                new_node = nodes.Node(connection["node2"], root, connection["cost"])
                frontier_nodes.append(new_node)
        open_nodes.append(root)
        print_frontier_nodes("Lista de nos fronteira após abrir Lisboa", frontier_nodes)

        end = False
        goal_node_name = "Gate 10"
        while end == False:
            end = True
            new_frontier_nodes = []
            for node in frontier_nodes:
                new_node_added = False
                for connection in config["connections"]:
                    if node.get_name() == connection["node1"]:
                        new_node = nodes.Node(connection["node2"], node, connection["cost"])
                        new_frontier_nodes.append(new_node)
                        # Test
                        print("Novo nó para a nova lista:", new_node.get_name())
                        new_node_added = True
                        # A new node was added, so we won't stop
                        end = False
                if new_node_added == False:
                    # Test
                    print("Nó não aberto para a nova lista:", node.get_name())
                    new_frontier_nodes.append(node)
                else:
                    open_nodes.append(node)
            # Test if the node is the goal
            for node in new_frontier_nodes:
                if node.get_name() == goal_node_name:
                    print("Encontra o objetivo. Termina a construção da árvore.")
                    end = True
            frontier_nodes = new_frontier_nodes

        print_frontier_nodes("Lista final dos nós fronteira", frontier_nodes)




main()
