### Darren McCann 30/04/2025
### Data Load for Tokyo Metro Neo4j Graph DB

print('Importing Required Packages...')
try:
    import requests
    import json
    import pandas as pd
    import re
    from neo4j import GraphDatabase
    print("Packages loaded successfully.")
except Exception as e:
    print(f"Failed to load packages: {e}")



### Load Data from sources
print('Loading Data............')
print('Sourcing stations.json from github')
url = "https://raw.githubusercontent.com/Jugendhackt/tokyo-metro-data/refs/heads/master/stations.json"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()  # Automatically parses JSON content
    print("Successfully loaded 'stations.json'.")
else:
    print(f"Failed to fetch file. Status code: {response.status_code}")

try:
    df = pd.read_csv('tokyo_stations_dataset.txt')  # Default sep=','
    print("Successfully loaded 'tokyo_stations_dataset.txt'.")
except Exception as e:
    print(f"Failed to load 'tokyo_stations_dataset.txt': {e}")
df_subset = df[['English Station Name', 'Latitude', 'Longitude']]
# Remove possible duplicates
df_unique = df_subset.drop_duplicates()


##Format stations data for Neo4j Load
#Get Overall Lines Data
print('Merging and Formatting Stations for Load to NEO4j Graph DB')
lines = data['lines']
stations = []

for code, name in data['stations'].items():
    # Handle special case for 'Mb' (two-letter prefix)
    if code.startswith('Mb'):
        line_key = 'Mb'
        line_name = lines['Mb']['name_en']
    else:
        line_key = code[0]
        line_name = lines.get(line_key, {}).get('name_en', 'Unknown Line')

    #Append (code, station name, line name, line key)
    stations.append((code, name['name_en'], line_name, line_key))


#alter all stations to lowercase and add '-' instead of space for accurate matching
lookup = {
    name.lower().replace(' ', '-'): (lat, lon)
    for name, lat, lon in zip(df_unique['English Station Name'], df_unique['Latitude'], df_unique['Longitude'])
}

station_list = []
for code, name,line_name, line in stations:
    lookup_name = name.lower().replace(' ', '-')
    coords = lookup.get(lookup_name, (None, None))  # default (None, None) if not found
    station_list.append((code, name, line,line_name, coords[0], coords[1]))

# output
for station in station_list:
    print(station)
print("Extracting all Connections from stations.json")
# Initialize an empty list to store all connections
all_connections = []

# Iterate through each station in 'stations'
for station_code, station_info in data['stations'].items():
    # Extract connections for the current station
    connections = station_info.get('connections', [])
    
    # Extract relevant details for each connection
    extracted_connections = [
        {
            'source_id': station_code,  # The current station as the source_id
            'type': connection['type'],
            'distance': connection['distance'],
            'target_id': connection['target_id'],
            'line': lines[re.sub(r'\d+', '', connection['target_id'])]['name_en'],
            'line_code': re.sub(r'\d+', '', connection['target_id'])
        }
        for connection in connections
    ]
    
    # Append the extracted connections to the main list
    all_connections.extend(extracted_connections)

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
#Define Station Input query
query = 'CREATE (n:Station {id: $id, name:$name, line:$line, line_name:$line_name, lat: $lat, long:$long}) RETURN n'
print('Loading Station data to NEO4J')
for station_id, station_name, line_id, line, latitude, longitude in station_list:
    driver.execute_query(query, id=station_id, name=station_name, line=line_id, line_name=line, lat=latitude, long=longitude)

#Define Connection Input query
query = 'MATCH (s1:Station {id:$s1}), (s2:Station {id:$s2}) CREATE (s1)-[r:CONNECT {type:$type,distance:$distance,line:$line,line_code:$line_code}]->(s2)'
print('Loading Connections data to NEO4J')
for connection in all_connections:
    driver.execute_query(query, s1=connection.get('source_id', 'N/A'),s2=connection.get('target_id', 'N/A'),type=connection.get('type', 'N/A'),distance=connection.get('distance', 'N/A'),line=connection.get('line', 'N/A'),line_code=connection.get('line_code', 'N/A'))

print('**************Data Load Successful**************')    