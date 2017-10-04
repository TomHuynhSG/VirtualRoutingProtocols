def dijkstra(graph, src, dest, visited=[], distances={}, predecessors={}, routing='SHP'):
    """ calculates a shortest path tree routed in src
    """
    # a few sanity checks
    if src not in graph:
        raise TypeError('The root of the shortest path tree cannot be found')
    if dest not in graph:
        raise TypeError('The target of the shortest path cannot be found')
        # ending condition
    if src == dest:
        # We build the shortest path and display it
        path = []
        pred = dest
        while pred != None:
            path.append(pred)
            pred = predecessors.get(pred, None)
        print('shortest path: ' + str(path) + " cost=" + str(distances[dest]))
    else:
        # if it is the initial  run, initializes the cost
        if not visited:
            distances[src] = 0
        # visit the neighbors
        for neighbor in graph[src]:
            if neighbor not in visited:
                if routing == 'SHP':
                    distance_neighbor = graph[src][neighbor][0]
                else:
                    distance_neighbor = graph[src][neighbor][1]

                new_distance = distances[src] + distance_neighbor

                if new_distance < distances.get(neighbor, float('inf')):
                    distances[neighbor] = new_distance
                    predecessors[neighbor] = src
        # mark as visited
        visited.append(src)
        # now that all neighbors have been visited: recurse
        # select the non visited node with lowest distance 'x'
        # run Dijskstra with src='x'
        unvisited = {}
        for k in graph:
            if k not in visited:
                unvisited[k] = distances.get(k, float('inf'))
        x = min(unvisited, key=unvisited.get)
        dijkstra(graph, x, dest, visited, distances, predecessors)




def read_topology(topology_file):
    graph ={}
    with open(topology_file) as topo_file:
        for line in topo_file:
            [fr, to, delay, cap] = line.split()
            delay = int(delay)
            cap = int(cap)
            if fr in graph:
                graph[fr][to] = (delay, cap)
            else:
                graph[fr]= {to: (delay, cap)}

            if to in graph:
                graph[to][fr] = (delay, cap)
            else:
                graph[to] = {fr: (delay, cap)}

    return graph

if __name__ == "__main__":

    network_scheme = 'CIRCUIT'
    routing_scheme = 'SHP'
    topology_file = 'topology.txt'
    workload_file = 'workload.txt'
    packet_rate = 2

    graph = read_topology(topology_file)
    dijkstra(graph, 'A', 'P')




