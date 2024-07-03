import copy
import random
import networkx as nx
from database.DAO import DAO
from geopy.distance import distance


class Model:
    def __init__(self):
        self._providers = DAO.getAllProviders()
        self._graph = nx.Graph()

    def getCammino(self, target, substring):
        sources = self.getNodesMostVicini()
        source = sources[random.randint(0, len(sources)-1)][0]

        if not nx.has_path(self._graph, source, target):
            print(f"{source} e {target} non sono connessi.")
            return [], source

        self._bestPath = []
        self._bestLen = 0
        parziale = [source]

        self._ricorsione(parziale, target, substring)
        return self._bestPath, source

    def _ricorsione(self, parziale, target, substring):
        if parziale[-1] == target:
            # Devo uscire ma prima controllo che sia una soluzione ottima
            if len(parziale) > self._bestLen:
                self._bestLen = len(parziale)
                self._bestPath = copy.deepcopy(parziale)
            return

        for v in self._graph.neighbors(parziale[-1]):
            if v not in parziale and substring not in v.Location:
                parziale.append(v)
                self._ricorsione(parziale, target, substring)
                parziale.pop()


    def buildGraph(self, provider, soglia):
        self._nodes = DAO.getLocationsOfProviderV2(provider)
        self._graph.add_nodes_from(self._nodes)

        # Add edges
        # Modo 1: faccio una query che mi restituisce gli archi.
        #allEdges = DAO.getAllEdges(provider)
        #for edge in allEdges:
        #    l1 = edge[0]
        #    l2 = edge[1]
        #    dist = distance((l1.latitude, l1.longitude), (l2.latitude, l2.longitude)).km
        #    if dist < soglia:
        #        self._graph.add_edge(l1, l2, weight=dist)
        #print(f"Modo 1: N nodes: {len(self._graph.nodes)} - N edges: {len(self._graph.edges)}")

        #self._graph.clear_edges()
        # Modo 2: modifico il metodo del DAO che legge i nodi,
        #  e ci aggiungo le coordinate di ogni location.
        #  Dopo, doppio ciclo sui nodi, e mi calcolo le distanze in python
        for u in self._nodes:
            for v in self._nodes:
                if u != v:
                    dist = distance((u.latitude, u.longitude), (v.latitude, v.longitude)).km
                    if dist < soglia:
                        self._graph.add_edge(u, v, weight=dist)

        print(f"Modo 2: N nodes: {len(self._graph.nodes)} - N edges: {len(self._graph.edges)}")

        # Modo 3: doppio ciclo sui nodi, e per ogni "possibile" arco faccio una query.

    def getNodesMostVicini(self):
        listTuples = []
        for v in self._nodes:
            listTuples.append((v, len(list(self._graph.neighbors(v)))))
        listTuples.sort(key=lambda x: x[1], reverse=True)

        #result1 = list(filter(lambda x: x[1] == listTuples[0][1], listTuples))

        result2 = [x for x in listTuples if x[1] == listTuples[0][1]]

        #print(len(result2))
        return result2

    def getAllProviders(self):
        return self._providers

    def getAllLocations(self):
        return self._graph.nodes

    def getGraphDetails(self):
        return len(self._graph.nodes), len(self._graph.edges)
