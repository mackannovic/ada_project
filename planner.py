from neo4j import GraphDatabase
import re
import argparse
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

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
    exit()

#Get Station List
r =  driver.execute_query('MATCH (m:Station) RETURN m')
station_names = [station['m']['name'] for station in r.records]
#print(station_names)




print("See Map for Station Locations")
#Tokyo Metro Map
img = mpimg.imread('tokyo.png')

plt.imshow(img)
plt.axis('off') 
plt.show(block=False)

# Argument Parser
parser = argparse.ArgumentParser(description="Route planner between Tokyo stations.")
parser.add_argument('--start', type=str, help='Start Journey Station')
parser.add_argument('--end', type=str, help='End Journey Station')
args = parser.parse_args()

#validate station name
def get_valid_station(prompt):
    while True:
        station = input(prompt).strip()
        if station in station_names:
            return station
        else:
            print("Invalid station name. Please enter a valid station from the list.")

if not args.start:
    args.start = get_valid_station("Enter Start Journey Station: ")
elif args.start not in station_names:
    print(f"Start station '{args.start}' is invalid.")
    args.start = get_valid_station("Enter Start Journey Station: ")

if not args.end:
    args.end = get_valid_station("Enter End Journey Station: ")
elif args.end not in station_names:
    print(f"End station '{args.end}' is invalid.")
    args.end = get_valid_station("Enter End Journey Station: ")

# Project the graph
print("Projecting Graph for Dijkstra Algorithm")

try:
    driver.execute_query("""MATCH (source:Station)-[r:CONNECT]->(target:Station)
    RETURN gds.graph.project(
    'tokyoV2',
     source,
     target,
    { relationshipProperties: r { .distance} }
    )""")
    print("Graph projection created.")
except Exception as e:
    if "already exists" in str(e):
        print("Graph 'tokyoV2' already exists. Skipping projection.")
    else:
        print(f"Failed to create graph projection: {e}")
        exit()   

# Run Dijkstra's algorithm
print("Running Dijkstra algorithm...")

records, summary, keys = driver.execute_query("""MATCH (source:Station {name: $start}), (target:Station {name: $end})
CALL gds.shortestPath.dijkstra.stream('tokyoV2', {
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
ORDER BY index""", start=args.start, end=args.end)

print(f"Shortest Route Generated for {records[0]['sourceNodeName']} to {records[0]['targetNodeName']} - Total Distance: {records[0]['totalCost']} - Stops: {len(records[0]['nodeNames'])-1}")

ids = [stop['id'] for stop in records[0]['path']]

# Create pairs list for connections
pairs = [(ids[i], ids[i+1]) for i in range(len(ids) - 1)]

connects_query = """MATCH (a:Station {id: $s1})-[r:CONNECT]->(b:Station {id: $s2})
RETURN a.name AS fromStation, r, b.name AS toStation"""

def strip_numbers(text):
    return re.sub(r'\d+', '', text)

for idx, (a, b) in enumerate(pairs, start=1):
    connect = driver.execute_query(connects_query, s1=a, s2=b)
    record = connect.records[0]

    if strip_numbers(a) == strip_numbers(b):
        extra_info = "Stay on Current Line"
    else:
        extra_info = f"Transfer to {record['r']['line']}"

    print(f"Step {idx}. {a}:{record['fromStation']} ➡ {b}:{record['toStation']} by {record['r']['type']} for {record['r']['distance']}km - {extra_info}")