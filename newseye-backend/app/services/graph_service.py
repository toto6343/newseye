from neo4j import GraphDatabase
from app.core.config import settings
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class GraphService:
    def __init__(self):
        self.uri = settings.NEO4J_URI
        self.user = settings.NEO4J_USER
        self.password = settings.NEO4J_PASSWORD
        self.driver = None
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            logger.info("Successfully connected to Neo4j")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")

    def close(self):
        if self.driver:
            self.driver.close()

    def add_news_to_graph(self, news_id: int, title: str, crime_type: str, entities: Dict[str, List[str]], source: str):
        """
        Creates nodes and relationships for a news article in Neo4j.
        """
        if not self.driver:
            logger.warning("Neo4j driver not initialized. Skipping graph update.")
            return

        with self.driver.session() as session:
            session.execute_write(self._create_graph_elements, news_id, title, crime_type, entities, source)

    @staticmethod
    def _create_graph_elements(tx, news_id, title, crime_type, entities, source):
        # 1. Create News node
        tx.run("MERGE (n:News {id: $id}) SET n.title = $title", id=news_id, title=title)
        
        # 2. Create and link Source
        if source:
            tx.run("""
                MERGE (s:Source {name: $source})
                WITH s
                MATCH (n:News {id: $id})
                MERGE (s)-[:PUBLISHED]->(n)
            """, source=source, id=news_id)

        # 3. Create and link CrimeType
        if crime_type:
            tx.run("""
                MERGE (ct:CrimeType {name: $crime_type})
                WITH ct
                MATCH (n:News {id: $id})
                MERGE (n)-[:REPORTS_ON]->(ct)
            """, crime_type=crime_type, id=news_id)

        # 4. Create and link Entities (PER, ORG, LOC)
        entity_label_map = {
            "PER": "Person",
            "ORG": "Organization",
            "LOC": "Location"
        }

        for category, names in entities.items():
            label = entity_label_map.get(category)
            if not label: continue
            
            for name in names:
                # Sanitize name to avoid empty nodes
                if not name.strip(): continue
                tx.run(f"""
                    MERGE (e:{label} {{name: $name}})
                    WITH e
                    MATCH (n:News {{id: $id}})
                    MERGE (n)-[:MENTIONS]->(e)
                """, name=name, id=news_id)

    def get_graph_data(self, limit: int = 50) -> Dict[str, List[Dict[str, Any]]]:
        """
        Retrieves graph data in a format suitable for react-force-graph.
        """
        if not self.driver:
            return {"nodes": [], "links": []}

        query = """
        MATCH (n)
        OPTIONAL MATCH (n)-[r]->(m)
        RETURN n, r, m
        LIMIT $limit
        """
        
        nodes = {}
        links = []
        
        with self.driver.session() as session:
            result = session.run(query, limit=limit)
            for record in result:
                # Process source node
                source_node = record["n"]
                if source_node.element_id not in nodes:
                    nodes[source_node.element_id] = {
                        "id": source_node.element_id,
                        "label": list(source_node.labels)[0] if source_node.labels else "Unknown",
                        "name": source_node.get("title") or source_node.get("name") or "Unnamed"
                    }
                
                # Process target node and relationship
                if record["m"] and record["r"]:
                    target_node = record["m"]
                    if target_node.element_id not in nodes:
                        nodes[target_node.element_id] = {
                            "id": target_node.element_id,
                            "label": list(target_node.labels)[0] if target_node.labels else "Unknown",
                            "name": target_node.get("title") or target_node.get("name") or "Unnamed"
                        }
                    
                    links.append({
                        "source": source_node.element_id,
                        "target": target_node.element_id,
                        "type": record["r"].type
                    })
        
        return {
            "nodes": list(nodes.values()),
            "links": links
        }

graph_service = GraphService()
