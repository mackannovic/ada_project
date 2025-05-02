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

print("*********************Gathering Statistics**************************")

stations=driver.execute_query("MATCH (s:Station) RETURN count(s) AS station_count")
print(f"There are {stations.records[0]['station_count']} stations within the Tokyo Metro System")
lines = driver.execute_query("MATCH (s:Station) RETURN count(DISTINCT s.line) AS number_of_lines")
print(f"There are {lines.records[0]['number_of_lines']} lines within the Tokyo Metro System")
line_stations = driver.execute_query("""MATCH (s:Station) WITH s.line AS line, s.line_name AS line_name, 
                                     count(*) AS station_count RETURN line, line_name, station_count ORDER BY station_count DESC""")
print("Count of Stations per Line")
for record in line_stations.records:
    print(f"Line: {record['line']}, Line Name: {record['line_name']}, Station Count: {record['station_count']}")