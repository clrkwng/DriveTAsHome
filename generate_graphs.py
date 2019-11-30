import random

def main():
    generate_graphs(200, 100)

def generate_graphs(numVertices, numHomes):
    f = open("inputs/200.in", "w+")

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
    startVertex = int(returnList[2][0][-1])
    for i in range(numVertices):
        for j in range(i, numVertices):
            xFactor = random.random()
            if i == j:
                graph[i][j] = 'x';
                graph[j][i] = 'x';
            if i == startVertex or j == startVertex:
                if xFactor > 0.9:
                    graph[i][j] = 'x';
                    graph[j][i] = 'x';
            elif xFactor > 0.3:
                graph[i][j] = 'x';
                graph[j][i] = 'x';

    #removes 70% of direct edges from S to vertices in H
    for i in returnList[1]:
        h = int(i[-1])
        randFactor = random.random()
        if randFactor > 0.3:
            graph[h][startVertex] = 'x'
            graph[startVertex][h] = 'x'


    #write the graph in to the text file
    for i in range(numVertices):
        for j in range(numVertices):
            f.write(str(graph[i][j]) + " ")
        f.write("\n")

    edgeCount = 0
    for i in range(numVertices):
        for j in range(i, numVertices):
            if graph[i][j] != 'x':
                edgeCount += 1
    print(edgeCount)

    f.close()
    return;


def generate_vertices(numVertices, numHomes):
    verticesSet = set()
    verticesList = []
    returnList = []

    for i in range(numVertices):
        vertex = 'x' + str(i)
        verticesSet.add(vertex)
        verticesList.append(vertex)
    returnList.append(verticesList)

    homes = random.sample(verticesSet, numHomes)
    returnList.append(homes)

    # for home in homes:
    #     print(home)

    start = random.sample(verticesSet, 1)
    returnList.append(start)
    # print(start)
    return returnList;

main()