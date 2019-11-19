import random

def main():
    generate_graphs(200,100)
    returnList = generate_vertices(200,100)

    print(returnList[0])
    print(returnList[1])
    print(returnList[2])

def generate_graphs(numVertices, numHomes):
    graph = [[0 for i in range(numVertices)] for j in range(numVertices)]
    #first generates the connected graph
    for i in range(numVertices):
        for j in range(i, numVertices):
            if i!=j:
                val = random.random() * 10
                graph[i][j] = val
                graph[j][i] = val
            else:
                graph[i][j] = 0

    #Using Floyd Warshall to satisfy triangle inequality
    for k in range(numVertices):
        for i in range(numVertices):
            for j in range(numVertices):
                graph[i][j] = min(graph[i][j], graph[i][k] + graph[k][j])

    #adds x's in, and rounds the values to 5 decimal places
    for i in range(numVertices):
        for j in range(i, numVertices):
            xFactor = random.random()
            if i == j or xFactor > 0.6:
                graph[i][j] = 'x';
                graph[j][i] = 'x';
            else:
                graph[i][j] = round(graph[i][j], 5)
                graph[j][i] = round(graph[j][i], 5)

    print('\n'.join([''.join(['{:9}'.format(item) for item in row]) for row in graph]))
    return;


def generate_vertices(numVertices, numHomes):
    vertices = set()
    returnList = []

    for i in range(numVertices):
        vertex = 'x' + str(i)
        vertices.add(vertex)
    returnList.append(vertices)

    homes = random.sample(vertices, numHomes)
    returnList.append(homes)

    # for home in homes:
    #     print(home)

    start = random.sample(vertices.difference(homes), 1)[0]
    returnList.append(start)
    # print(start)
    return returnList;

main()
