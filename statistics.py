from neo4j import GraphDatabase
import pandas as pd
import plotly.express as px

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

print("*********************Gathering Statistics**************************")

stations=driver.execute_query("MATCH (s:Station) RETURN count(s) AS station_count")
print(f"There are {stations.records[0]['station_count']} stations within the Tokyo Metro System")
lines = driver.execute_query("MATCH (s:Station) RETURN count(DISTINCT s.line) AS number_of_lines")
print(f"There are {lines.records[0]['number_of_lines']} lines within the Tokyo Metro System")
print("")
print("")
line_stations = driver.execute_query("""MATCH (s:Station) WITH s.line AS line, s.line_name AS line_name, 
                                     count(*) AS station_count RETURN line, line_name, station_count ORDER BY station_count DESC""")
print("Count of Stations per Line")
for record in line_stations.records:
    print(f"Line: {record['line']}, Line Name: {record['line_name']}, Station Count: {record['station_count']}")
print("")
connects=driver.execute_query("MATCH ()-[r:CONNECT]-() RETURN count(r) AS connects_count")
print(f"There are {connects.records[0]['connects_count']} multi-directional station connections within the Tokyo Metro System")
connects_stations = driver.execute_query("""MATCH (s:Station)-[r:CONNECT]->()
WITH s.name AS station_name, count(r) AS outbound_connections
RETURN station_name, outbound_connections
ORDER BY outbound_connections DESC
LIMIT 10""")
print(f"The station with the most connections is {connects_stations.records[0]['station_name']} with {connects_stations.records[0]['outbound_connections']} outbound connections")
print("")
print("Top Ten Stations by number of outbound connections")
for i, record in enumerate(connects_stations.records, start=1):
    print(f"{i}. Station: {record['station_name']}, Outbound Connects: {record['outbound_connections']}")
connect_type = driver.execute_query("MATCH (a)-[r:CONNECT]->(b) RETURN r.type AS relationship_type, count(*) AS type_count ORDER BY type_count DESC")
print("")
print(f"There are {len(connect_type.records)} types of connections")
print("Connection Types Outbound Count")
for record in connect_type.records:
    print(f"Type: {record['relationship_type']}, Outbound Connects: {record['type_count']}")
print("")
avg_distance=driver.execute_query("""MATCH (a:Station)-[r:CONNECT]->(b:Station)
WHERE r.distance IS NOT NULL
RETURN avg(r.distance) AS average_distance""")
print(f"The average distance for connections is {avg_distance.records[0]['average_distance']:.2f}km")
print("")
line_distance=driver.execute_query("""MATCH (a:Station)-[r:CONNECT]->(b:Station)
WHERE r.line IS NOT NULL AND r.distance IS NOT NULL
RETURN r.line_code AS line_code, r.line AS line, sum(r.distance) AS total_distance
ORDER BY total_distance DESC""")
print(f"The line with the longest track distance is the {line_distance.records[0]['line']} with {line_distance.records[0]['total_distance']:.2f}km of track")
print("Lines by Distance")
for record in line_distance.records:
    print(f"Line: {record['line_code']}, Line Name: {record['line']}, Distance: {record['total_distance']:.2f}km")


#Map of Tokyo Metro
stations = driver.execute_query("MATCH (s:Station) RETURN s")
data = []

for record in stations.records:
    node = record['s']
    data.append({
        'id': node['id'],
        'name': node['name'],
        'line': node['line'],
        'line_name': node['line_name'],
        'lat': node['lat'],
        'long': node['long']
    })

stations_df = pd.DataFrame(data)
print(stations_df)

fig = px.scatter_mapbox(
    stations_df,
    lat="lat",
    lon="long",
    color="line_name",
    hover_name="name",
    hover_data={"id": True, "lat": False, "long": False},
    size_max=60,
    zoom=11,
    height=800
)

fig.update_layout(
    mapbox_style="open-street-map",  
    mapbox_zoom=11,
    mapbox_center={"lat": stations_df["lat"].mean(), "lon": stations_df["long"].mean()},
    margin={"r":0, "t":0, "l":0, "b":0}
)

fig.show() 