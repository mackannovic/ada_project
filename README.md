# 🚇 Tokyo Metro Routefinder

> **An Applied Data Architecture project that models the Tokyo Metro as a Neo4j graph and finds the shortest route between any two stations — complete with line transfers, network statistics, and an interactive map.**

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Neo4j](https://img.shields.io/badge/Neo4j-Graph%20DB-4581C3?logo=neo4j&logoColor=white)](https://neo4j.com/)
[![GDS](https://img.shields.io/badge/Neo4j-Graph%20Data%20Science-008CC1)](https://neo4j.com/docs/graph-data-science/current/)
[![Plotly](https://img.shields.io/badge/Plotly-Mapbox-3F4F75?logo=plotly&logoColor=white)](https://plotly.com/python/)
[![Algorithm](https://img.shields.io/badge/Algorithm-Dijkstra-orange)]()
[![Platform](https://img.shields.io/badge/Tested%20on-Windows%2011-0078D6?logo=windows&logoColor=white)]()

---

## 📋 Overview

This project demonstrates an end-to-end **graph data architecture** workflow built around the Tokyo Metro network. Raw station and connection data is ingested into a **Neo4j** graph database, where stations become nodes and the links between them become weighted relationships. From that graph the project delivers three things:

1. **A loader** that builds the database from public + local data sources.
2. **A statistics module** that profiles the network and plots every station on an interactive map.
3. **A route planner** that uses **Dijkstra's algorithm** (via the Neo4j Graph Data Science library) to compute the shortest path between two stations, reporting distance, number of stops, and where to change lines.

| | |
|---|---|
| **Author** | Darren McCann |
| **Project** | Applied Data Architecture (ADA) Project |
| **Stack** | Neo4j + Python |
| **Developed on** | Python 3.11, Windows 11 Pro |

---

## 📑 Table of Contents

- [Architecture](#-architecture)
- [Features](#-features)
- [Repository Structure](#-repository-structure)
- [Graph Data Model](#-graph-data-model)
- [Data Sources](#-data-sources)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Usage](#-usage)
- [Example Output](#-example-output)
- [Configuration & Security Notes](#-configuration--security-notes)
- [Future Work](#-future-work)
- [Acknowledgements](#-acknowledgements)

---

## 🏗 Architecture

```
   Data Sources                Ingestion                Graph DB               Applications
 ┌───────────────┐         ┌──────────────┐         ┌─────────────┐       ┌──────────────────┐
 │ stations.json │────────▶│              │         │             │──────▶│ statistics.py    │
 │  (GitHub)     │         │ data_load.py │────────▶│   Neo4j     │       │ network stats +  │
 ├───────────────┤         │ parse/clean/ │  CREATE │  (Station)  │       │ Plotly map       │
 │ tokyo_        │────────▶│ merge/load   │  nodes &│  -[CONNECT]-│       ├──────────────────┤
 │ stations.txt  │         │              │  rels   │  ▶(Station) │──────▶│ planner.py       │
 │  (local CSV)  │         └──────────────┘         └─────────────┘       │ Dijkstra shortest│
 └───────────────┘                                                        │ path + transfers │
                                                                          └──────────────────┘
```

---

## ✨ Features

- **Graph-based modelling** of the Tokyo Metro using Neo4j nodes and relationships.
- **Automated data ingestion** that pulls station/connection data from GitHub and enriches it with local latitude/longitude coordinates.
- **Network analytics** — station counts, lines, connections, busiest interchange stations, connection types, average hop distance, and total track length per line.
- **Interactive geographic map** of every station, colour-coded by line, rendered with Plotly on an OpenStreetMap base.
- **Shortest-path route planning** with Dijkstra's algorithm weighted by inter-station distance.
- **Human-readable directions** that detect when you stay on a line versus when you need to transfer.
- **Flexible input** — pass stations as command-line arguments or enter them interactively with validation.

---

## 📁 Repository Structure

```
ada_project/
├── data_load.py                 # Builds the Neo4j graph from source data
├── statistics.py                # Network statistics + interactive Plotly map
├── planner.py                   # Dijkstra route planner with transfer detection
├── tokyo_stations_dataset.txt   # Local CSV: station names + coordinates
├── tokyo.png                    # Tokyo Metro reference map (shown by planner)
├── git_errors.txt               # Development log / notes
└── README.md
```

---

## 🗂 Graph Data Model

**Nodes — `Station`**

| Property | Description |
|---|---|
| `id` | Station code (e.g. line prefix + number) |
| `name` | English station name |
| `line` | Line code |
| `line_name` | Full English line name |
| `lat` / `long` | Geographic coordinates |

**Relationships — `(:Station)-[:CONNECT]->(:Station)`**

| Property | Description |
|---|---|
| `type` | Mode/type of connection |
| `distance` | Distance between the two stations (km) — used as the Dijkstra weight |
| `line` | Line name for the connection |
| `line_code` | Line code (target station prefix, digits stripped) |

---

## 🌐 Data Sources

- **`stations.json`** — fetched at runtime from the open [Jugendhackt/tokyo-metro-data](https://github.com/Jugendhackt/tokyo-metro-data) repository, providing lines, stations, and their connections.
- **`tokyo_stations_dataset.txt`** — a local CSV supplying English station names with latitude/longitude, used to geo-enrich the nodes.

Station names are normalised (lowercased, spaces → hyphens) to reliably match coordinates between the two sources.

---

## ✅ Prerequisites

- **Python 3.11**
- **Neo4j** (Desktop or Server) running locally at `neo4j://localhost`
- **Neo4j Graph Data Science (GDS) library** installed — required by `planner.py` for graph projection and Dijkstra
- Python packages:

```bash
pip install neo4j pandas requests matplotlib plotly
```

---

## 🚀 Installation

```bash
# 1. Clone the repository
git clone https://github.com/mackannovic/ada_project.git
cd ada_project

# 2. Install dependencies
pip install neo4j pandas requests matplotlib plotly

# 3. Start your local Neo4j database (with the GDS plugin enabled)
#    and update the connection credentials in each script (see notes below)

# 4. Build the graph
python data_load.py
```

---

## 🕹 Usage

### 1. Load the data

Builds all `Station` nodes and `CONNECT` relationships in Neo4j.

```bash
python data_load.py
```

### 2. Explore network statistics

Prints summary statistics to the console and opens an interactive station map in your browser.

```bash
python statistics.py
```

### 3. Plan a route

Displays the Tokyo Metro map, then computes the shortest path. You can supply stations as arguments or be prompted interactively:

```bash
# With arguments
python planner.py --start "Shibuya" --end "Asakusa"

# Interactive (validates against the station list)
python planner.py
```

---

## 📊 Example Output

**Statistics module** reports figures such as:

- Total number of stations and distinct lines
- Station count per line (descending)
- Total `CONNECT` relationships in the network
- Top 10 stations by outbound connections (busiest interchanges)
- Breakdown of connection types
- Average connection distance (km)
- Lines ranked by total track distance

…and renders an interactive Plotly map of every station, coloured by line.

**Route planner** prints a journey summary and step-by-step directions, for example:

```
Shortest Route Generated for Shibuya to Asakusa - Total Distance: 12.34km - Stops: 9
Step 1. G01:Shibuya ➡ G02:Omote-sando by train for 1.30km - Stay on Current Line
Step 2. G02:Omote-sando ➡ C04:... by train for 0.90km - Transfer to Chiyoda Line
...
Press Enter to exit...
```

*(Values illustrative — actual output depends on the loaded data.)*

---

## 🔐 Configuration & Security Notes

The Neo4j connection is currently defined inline near the top of each script:

```python
URI = "neo4j://localhost"
AUTH = ("neo4j", "<password>")
```

> ⚠️ **Heads-up:** the database password is presently hard-coded in the source files. Before sharing or deploying, it's strongly recommended to move credentials into **environment variables** (or a `.env` file loaded with `python-dotenv`) and rotate the existing password, since committed secrets remain visible in the repository's git history.

```python
import os
AUTH = (os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"])
```

A couple of other practical notes:

- `planner.py` projects an in-memory GDS graph named `tokyoV2`. If it already exists, the script skips re-projection — drop it (`CALL gds.graph.drop('tokyoV2')`) if you reload the data and want a fresh projection.
- `statistics.py` and `planner.py` both expect `data_load.py` to have been run first so the graph is populated.

---

## 🔮 Future Work

- Externalise configuration (credentials, file paths) and add a `requirements.txt`.
- Add multi-criteria routing (fewest transfers / fastest time, not just shortest distance).
- Wrap the planner in a simple web or GUI front end with a clickable map.
- Add automated tests and validation for the data-load pipeline.
- Cache the GDS projection lifecycle and handle reloads cleanly.

---

## 🙏 Acknowledgements

- Tokyo Metro station and connection data from the open-source [Jugendhackt/tokyo-metro-data](https://github.com/Jugendhackt/tokyo-metro-data) project.
- Built with [Neo4j](https://neo4j.com/), the [Graph Data Science](https://neo4j.com/docs/graph-data-science/current/) library, [Plotly](https://plotly.com/python/), and [Matplotlib](https://matplotlib.org/).

---

<p align="center"><i>Built as part of an Applied Data Architecture project — turning a metro map into a queryable graph.</i></p>
