import heapq
import sys

def dijkstra(graph, frm, to, routing='SHP', visited=[], distances={}, predecessors={} ):
    """ dijkstra algorithm to find the shortest path
    """

    assert frm in graph
    assert to in graph

    if frm == to:
        # reach distination so return the path and cost
        path = []
        pred = to
        while pred != None:
            path.append(pred)
            pred = predecessors.get(pred, None)

        return (path, distances[to])
        pass
    else:
        # if it is the initial  run, initializes the cost
        if not visited:
            distances[frm] = 0
        # visit the neighbors
        for neighbor in graph[frm]:
            if neighbor not in visited:
                if routing == 'SHP':
                    distance_neighbor = 1
                    new_distance = distances[frm] + distance_neighbor
                elif routing == 'SDP':
                    distance_neighbor = graph[frm][neighbor]['delay']
                    new_distance = distances[frm] + distance_neighbor
                else: #LLP
                    distance_neighbor = float(graph[frm][neighbor]['used'])/graph[frm][neighbor]['cap']
                    if distance_neighbor > distances[frm]:
                        new_distance = distance_neighbor
                    else:
                        new_distance = distances[frm]

                if new_distance < distances.get(neighbor, float('inf')):
                    distances[neighbor] = new_distance
                    predecessors[neighbor] = frm
        # mark as visited
        visited.append(frm)

        #select the node with lowest cost
        unvisited = {}
        for k in graph:
            if k not in visited:
                unvisited[k] = distances.get(k, float('inf'))
        optimal_frm = min(unvisited, key=unvisited.get)
        final_path, final_distances = dijkstra(graph, optimal_frm, to, routing, visited, distances, predecessors)

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
    # network_scheme = sys.argv[1]
    # routing_scheme = sys.argv[2]
    # topology_file = sys.argv[3]
    # workload_file = sys.argv[4]
    # packet_rate = int(sys.argv[5])
    
    network_scheme = 'PACKET'
    routing_scheme = 'LLP'
    topology_file = 'topology.txt'
    workload_file = 'workload.txt'
    packet_rate = 4

    link_usage = 25

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

    packet_propagation = 1/float(packet_rate)
    total_no_requests += len(workload)

    #experiment code to check out total packet in workload
    # _total_packets=0
    # import sys
    # while len(workload) > 0:
    #     (start_request, fr_request, to_request, dur_request) = heapq.heappop(workload)
    #     _total_packets+=int(packet_rate*dur_request)
    #
    # print _total_packets
    # sys.exit()

    while len(workload) > 0:

        dropped_packet=False

        (start_request, fr_request, to_request, dur_request) = heapq.heappop(workload)
        #print ("Pop",(start_request, fr_request, to_request, dur_request) )

        if network_scheme == "PACKET":
            no_packet_per_work=1
        else:
            no_packet_per_work =int(packet_rate*dur_request)

        total_no_packets += no_packet_per_work

        if network_scheme == "PACKET":
            #break down a large request to smaller packets
            if dur_request > packet_propagation:
                heapq.heappush(workload, (start_request + packet_propagation, fr_request, to_request,
                                          dur_request - packet_propagation))
                dur_request = packet_propagation
            else:
                dropped_packet=True


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

            #check if the packet suppose to drop due to lack of time
            if (dropped_packet==False):
                total_hops += get_path_hops(path)* no_packet_per_work
                total_delay += get_path_delay(path)* no_packet_per_work
                no_success_packets += no_packet_per_work
            else:
                total_no_packets-= no_packet_per_work

        else: #no capacity available so block
            if (dropped_packet==False):
                no_block_packets += no_packet_per_work
            else:
                total_no_packets-= no_packet_per_work

    #calculate statistics
    percentage_success_packets = no_success_packets / float(total_no_packets)*100
    percentage_block_packets = no_block_packets / float(total_no_packets)*100
    average_hops = total_hops/ float(no_success_packets)
    average_delay = total_delay / float(no_success_packets)

    print "total number of virtual connection requests:", total_no_requests
    print "total number of packets:", total_no_packets
    print "number of successfully routed packets:", no_success_packets
    print "percentage of successfully routed packets:", "{0:.2f}".format(percentage_success_packets)
    print "number of blocked packets:", no_block_packets
    print "percentage of blocked packets:", "{0:.2f}".format(percentage_block_packets)
    print "average number of hops per circuit:", "{0:.2f}".format(average_hops)
    print "average cumulative propagation delay per circuit:", "{0:.2f}".format(average_delay)
