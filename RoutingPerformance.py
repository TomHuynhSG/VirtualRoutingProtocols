import heapq


def dijkstra(graph, src, dest, visited=[], distances={}, predecessors={}, routing='SHP'):
    """ calculates a shortest path tree routed in src
    """
    print visited
    print distances
    print predecessors
    print routing
    # a few sanity checks
    if src not in graph:
        raise TypeError('The root of the shortest path tree cannot be found')
    if dest not in graph:
        raise TypeError('The target of the shortest path cannot be found')
        # ending condition
    if src == dest:
        #We build the shortest path and display it
        # path = []
        # pred = dest
        # while pred != None:
        #     path.append(pred)
        #     pred = predecessors.get(pred, None)
        #
        # print('shortest path: ' + str(path) + " cost=" + str(distances[dest]))
        pass
    else:
        # if it is the initial  run, initializes the cost
        if not visited:
            distances[src] = 0
        # visit the neighbors
        for neighbor in graph[src]:
            if neighbor not in visited:
                if routing == 'SHP':
                    distance_neighbor = 1
                elif routing == 'SDP':
                    distance_neighbor = graph[src][neighbor]['delay']
                else: #LLP
                    distance_neighbor = 1

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


    path = []
    pred = dest
    while pred != None:
        path.append(pred)
        pred = predecessors.get(pred, None)
    return (path, distances[dest])


def grouper(input_list, n = 2):
    for i in xrange(len(input_list) - (n - 1)):
        yield input_list[i:i+n]

def check_capacity(graph, path):
    for fr, to in grouper(path, 2):
        if graph[fr][to]['used'] >= graph[fr][to]['cap']:
            return False
    return True

def release_capacity(graph, path):
    for fr, to in grouper(path, 2):
        graph[fr][to]['used'] -= 1
        graph[to][fr]['used'] -= 1
    return graph

def use_capacity(graph, path):
    for fr, to in grouper(path, 2):
        graph[fr][to]['used'] += 1
        graph[to][fr]['used'] += 1
    return graph

def print_graph(graph):
    for fr in graph:
        print fr, graph[fr]

def read_topology(topology_file):
    graph ={}
    with open(topology_file) as topo_file:
        for line in topo_file:
            [fr, to, delay, cap] = line.split()
            delay = int(delay)
            cap = int(cap)
            if fr in graph:
                graph[fr][to] = {'delay': delay, 'cap': cap, 'used': 0}
            else:
                graph[fr] = {to: {'delay': delay, 'cap': cap, 'used': 0}}

            if to in graph:
                graph[to][fr] = {'delay': delay, 'cap': cap, 'used': 0}
            else:
                graph[to] = {fr: {'delay': delay, 'cap': cap, 'used': 0}}
    return graph

def read_workload(workload_file):
    workload =[]
    with open(workload_file) as work_file:
        for line in work_file:
            [start, fr, to, dur] = line.split()
            start = float(start)
            dur = float(dur)
            heapq.heappush(workload, (start, fr, to, dur))
    return workload


if __name__ == "__main__":

    # Command line variables
    network_scheme = 'CIRCUIT'
    routing_scheme = 'SHP'
    topology_file = 'topology_small.txt'
    workload_file = 'workload_small.txt'
    packet_rate = 2

    # Statistic variables
    total_no_requests= 0
    total_no_packets= 0

    no_success_packets= 0
    percentage_success_packets= 0.0

    no_block_packets= 0
    percentage_block_packets= 0.0

    average_hops=0.0
    average_delay=0.0

    graph = read_topology(topology_file)
    workload = read_workload(workload_file)

    release_queue = []

    while len(workload) > 0:
        (start_request, fr_request, to_request, dur_request) = heapq.heappop(workload)

        print (start_request, fr_request, to_request, dur_request)
        while len(release_queue) > 0:
            if start_request >= release_queue[0][0]:
                released_work = heapq.heappop(release_queue)
                release_capacity(graph, released_work[1])
            else:
                break

        (path, _) = dijkstra(graph, fr_request, to_request, visited=[],visited=[], distances={}, predecessors={})
        if check_capacity(graph, path):
            use_capacity(graph, path)

            end_time = start_request + dur_request
            heapq.heappush(release_queue, (end_time, path))
        else:
            print 'BLOCKKKKK!!!'

        # print ("Workload", workload)
        # print ("Released", release_queue)
        # print_graph(graph)
        # print

    #print workload

    # print dijkstra(graph, 'A', 'D')
    # print
    # print
    # print
    # print
    #
    # print dijkstra(graph, 'B', 'C')
    def temp(d=[]):
        c = list(d)
        print c
        c.append("a")

    temp()

    temp()

    # print path
    # print cost
    # print_graph(graph)
    # print check_capacity(graph,path)
    # use_capacity(graph,path)
    # print_graph(graph)
    #print read_workload(workload_file)


    # a=heapq.heappop(workload)
    # print a




