import heapq

def dijkstra(graph, src, dest, routing='SHP', visited=[], distances={}, predecessors={} ):
    """ calculates a shortest path tree routed in src
    """
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
        # print('shortest path: ' + str(path) + " cost=" + str(distances[dest]))

        path = []
        pred = dest
        while pred != None:
            path.append(pred)
            pred = predecessors.get(pred, None)

        return (path, distances[dest])
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
                    new_distance = distances[src] + distance_neighbor
                elif routing == 'SDP':
                    distance_neighbor = graph[src][neighbor]['delay']
                    new_distance = distances[src] + distance_neighbor
                else: #LLP
                    distance_neighbor = float(graph[src][neighbor]['used'])/graph[src][neighbor]['cap']
                    #print (src,neighbor,distance_neighbor,graph[src][neighbor]['used'],graph[src][neighbor]['cap'])
                    if distance_neighbor > distances[src]:
                        new_distance = distance_neighbor
                    else:
                        new_distance = distances[src]

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
        final_path, final_distances = dijkstra(graph, x, dest, routing, visited, distances, predecessors)

    return (final_path, final_distances)


def grouper(input_list, n = 2):
    for i in xrange(len(input_list) - (n - 1)):
        yield input_list[i:i+n]

def check_capacity(graph, path, usage):
    for fr, to in grouper(path, 2):
        if graph[fr][to]['used'] + usage > graph[fr][to]['cap']:
            return False
    return True

def release_capacity(graph, path, usage):
    for fr, to in grouper(path, 2):
        graph[fr][to]['used'] -= usage
        graph[to][fr]['used'] -= usage
    return graph

def use_capacity(graph, path, usage):
    for fr, to in grouper(path, 2):
        graph[fr][to]['used'] += usage
        graph[to][fr]['used'] += usage
    return graph

def get_path_hops(path):
    return len(path) - 1

def get_path_delay(path):
    delay = 0
    for fr, to in grouper(path, 2):
        delay += graph[fr][to]['delay']
    return delay

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
    workload = []
    with open(workload_file) as work_file:
        for line in work_file:
            [start, fr, to, dur] = line.split()
            start = float(start)
            dur = float(dur)
            heapq.heappush(workload, (start, fr, to, dur))
    return workload


if __name__ == "__main__":

    # Command line variables
    network_scheme = sys.argv[1]
    routing_scheme = sys.argv[2]
    topology_file = sys.argv[3]
    workload_file = sys.argv[4]
    packet_rate = int(sys.argv[5])
    
    network_scheme = 'PACKET'
    routing_scheme = 'SHP'
    topology_file = 'topology.txt'
    workload_file = 'workload.txt'
    packet_rate = 2
    link_usage = 1

    # Statistic variables
    total_no_requests = 0
    total_no_packets = 0

    no_success_packets = 0
    percentage_success_packets = 0

    no_block_packets = 0
    percentage_block_packets = 0

    total_hops = 0
    total_delay = 0

    average_hops = 0
    average_delay = 0

    # read graph and workload files
    graph = read_topology(topology_file)
    workload = read_workload(workload_file)

    release_queue = []

    packet_propagation = 1/float(2)

    total_no_requests += len(workload)

    while len(workload) > 0:
        (start_request, fr_request, to_request, dur_request) = heapq.heappop(workload)

        total_no_packets += 1

        if network_scheme == "PACKET":
            if dur_request > packet_propagation:
                heapq.heappush(workload, (start_request + packet_propagation, fr_request, to_request,
                                          dur_request - packet_propagation))
                dur_request = packet_propagation




        # release finished work
        while len(release_queue) > 0:
            if start_request >= release_queue[0][0]:
                released_work = heapq.heappop(release_queue)
                released_path = released_work[1]
                release_capacity(graph, released_path, link_usage)
            else:
                break

        # routing path for new packet or circuit
        (path, _) = dijkstra(graph, fr_request, to_request, routing_scheme, [], {}, {})
        if check_capacity(graph, path, link_usage):
            use_capacity(graph, path, link_usage)
            end_time = start_request + dur_request
            heapq.heappush(release_queue, (end_time, path))

            total_hops += get_path_hops(path)
            total_delay += get_path_delay(path)

            no_success_packets += 1




        else:
            no_block_packets +=1

            #print 'BLOCKKKKK!!!'


    percentage_success_packets = no_success_packets / float(total_no_packets)*100
    percentage_block_packets = no_block_packets / float(total_no_packets)*100
    average_hops = total_hops/ float(no_success_packets)
    average_delay = total_delay / float(no_success_packets)

    print "total number of virtual circuit requests:", total_no_requests
    print "total number of packets:", total_no_packets
    print "number of successfully routed packets:", no_success_packets
    print "percentage of successfully routed packets:", percentage_success_packets
    print "number of blocked packets:", no_block_packets
    print "percentage of blocked packets:", percentage_block_packets
    print "average number of hops per circuit:", average_hops
    print "average cumulative propagation delay per circuit:", average_delay


    # print_graph(graph)
    #print workload

    #print dijkstra(graph, 'A', 'D', visited=[], distances={}, predecessors={}, routing='LLP')

    # print dijkstra(graph, 'B', 'C')

    # print path
    # print cost
    # print_graph(graph)
    # print check_capacity(graph,path)
    # use_capacity(graph,path)
    # print_graph(graph)
    #print read_workload(workload_file)

    # a=heapq.heappop(workload)
    # print a




