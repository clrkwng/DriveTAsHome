import random

def main():
    generate_graphs(100, 50)

def generate_graphs(numVertices, numHomes):
    f = open("inputs/100.in", "w+")

    f.write(str(numVertices)+"\n")
    f.write(str(numHomes)+"\n")

    returnList = generate_vertices(numVertices,numHomes)
    for l in returnList:
        for i in l:
            f.write(i + " ")
        f.write("\n")

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
            graph[i][j] = round(graph[i][j], 5)
            graph[j][i] = round(graph[j][i], 5)

    #Using Floyd Warshall to satisfy triangle inequality
    for k in range(numVertices):
        for i in range(numVertices):
            for j in range(numVertices):
                graph[i][j] = min(graph[i][j], graph[i][k] + graph[k][j])
                graph[i][j] = round(graph[i][j], 5)

    #adds x's in
    for i in range(numVertices):
        for j in range(i, numVertices):
            xFactor = random.random()
            if i == j or xFactor > 0.6:
                graph[i][j] = 'x';
                graph[j][i] = 'x';

    #write the graph in to the text file
    for i in range(numVertices):
        for j in range(numVertices):
            f.write(str(graph[i][j]) + " ")
        f.write("\n")

    #print('\n'.join([''.join(['{:9}'.format(item) for item in row]) for row in graph]))
    f.close()
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

    start = random.sample(vertices, 1)
    returnList.append(start)
    # print(start)
    return returnList;

main()
