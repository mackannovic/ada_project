from neo4j import GraphDatabase
# Establish NEO4J Connection
print("Connecting to Neo4j database...")

URI = "neo4j://localhost"
AUTH = ("neo4j", "Ev3rysec0nd#s")

try:
    driver = GraphDatabase.driver(URI, auth=AUTH)
    driver.verify_connectivity()
    print("Successfully connected to the Neo4j database.")
except Exception as e:
    print(f"Failed to connect to the Neo4j database: {e}")
print("Projecting Graph for Dijkstra Algorithm")
driver.execute_query("""MATCH (source:Station)-[r:CONNECT]->(target:Station)
RETURN gds.graph.project(
  'tokyo',
  source,
  target,
  { relationshipProperties: r { .distance} }
)""")

route=driver.execute_query("""MATCH (source:Station {name: 'Takaracho'}), (target:Station {name: 'Kudanshita'})
CALL gds.shortestPath.dijkstra.stream('tokyo', {
    sourceNode: source,
    targetNodes: target,
    relationshipWeightProperty: 'distance'
})
YIELD index, sourceNode, targetNode, totalCost, nodeIds, costs, path
RETURN
    index,
    gds.util.asNode(sourceNode).name AS sourceNodeName,
    gds.util.asNode(targetNode).name AS targetNodeName,
    totalCost,
    [nodeId IN nodeIds | gds.util.asNode(nodeId).name] AS nodeNames,
    costs,
    nodes(path) as path
ORDER BY index""")

print(route[0]['path'])
