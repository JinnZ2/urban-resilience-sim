"""
network.py — Inter-Community Corridor Network
Urban Resilience Simulator
License: CC0

Models connections between communities in a corridor,
trade capacity, and mutual aid potential.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import math


class ConnectionType(Enum):
    HIGHWAY = "highway"
    COUNTY_ROAD = "county_road"
    RAIL = "rail"
    TRAIL = "trail"
    RADIO = "radio"
    RUNNER = "runner"  # on foot


class TradeGood(Enum):
    FOOD = "food"
    WATER = "water"
    FUEL = "fuel"
    MEDICINE = "medicine"
    SEED = "seed"
    LABOR = "labor"
    KNOWLEDGE = "knowledge"
    TOOLS = "tools"


@dataclass
class CommunityNode:
    """A community in the corridor network."""
    name: str
    population: int
    lat: float
    lon: float
    surplus: list[TradeGood] = field(default_factory=list)
    needs: list[TradeGood] = field(default_factory=list)
    has_radio: bool = False
    has_medical: bool = False
    food_security_pct: float = 0.0  # local production % of need


@dataclass
class Connection:
    """Link between two communities."""
    community_a: str
    community_b: str
    connection_type: ConnectionType
    distance_miles: float
    passable: bool = True
    notes: str = ""


class CorridorNetwork:
    """Network of communities in a recovery corridor."""

    def __init__(self, name: str):
        self.name = name
        self.nodes: dict[str, CommunityNode] = {}
        self.connections: list[Connection] = []

    def add_community(self, node: CommunityNode):
        self.nodes[node.name] = node

    def add_connection(self, conn: Connection):
        self.connections.append(conn)

    def get_neighbors(self, community_name: str) -> list[tuple[CommunityNode, Connection]]:
        """Get all connected communities."""
        neighbors = []
        for conn in self.connections:
            if not conn.passable:
                continue
            if conn.community_a == community_name:
                neighbor = self.nodes.get(conn.community_b)
                if neighbor:
                    neighbors.append((neighbor, conn))
            elif conn.community_b == community_name:
                neighbor = self.nodes.get(conn.community_a)
                if neighbor:
                    neighbors.append((neighbor, conn))
        return neighbors

    def find_resource(self, community_name: str, need: TradeGood) -> list[dict]:
        """Find nearest community with surplus of needed resource."""
        results = []
        for name, node in self.nodes.items():
            if name == community_name:
                continue
            if need in node.surplus:
                # Find connection distance
                distance = self._shortest_distance(community_name, name)
                results.append({
                    "community": name,
                    "distance_miles": distance,
                    "population": node.population,
                    "has_radio": node.has_radio,
                })
        return sorted(results, key=lambda x: x["distance_miles"])

    def _shortest_distance(self, a: str, b: str) -> float:
        """Simple geographic distance (not path distance)."""
        node_a = self.nodes.get(a)
        node_b = self.nodes.get(b)
        if not node_a or not node_b:
            return float("inf")
        # Haversine approximation
        dlat = math.radians(node_b.lat - node_a.lat)
        dlon = math.radians(node_b.lon - node_a.lon)
        a_val = (math.sin(dlat / 2) ** 2 +
                 math.cos(math.radians(node_a.lat)) *
                 math.cos(math.radians(node_b.lat)) *
                 math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a_val), math.sqrt(1 - a_val))
        return round(3959 * c, 1)  # miles

    def corridor_resilience(self) -> dict:
        """Assess overall corridor resilience."""
        total_pop = sum(n.population for n in self.nodes.values())
        radio_nodes = sum(1 for n in self.nodes.values() if n.has_radio)
        medical_nodes = sum(1 for n in self.nodes.values() if n.has_medical)
        passable = sum(1 for c in self.connections if c.passable)

        # Food security across corridor
        weighted_food = sum(
            n.food_security_pct * n.population for n in self.nodes.values()
        )
        avg_food_security = weighted_food / total_pop if total_pop > 0 else 0

        # Connectivity score
        max_connections = len(self.nodes) * (len(self.nodes) - 1) / 2
        connectivity = passable / max_connections * 100 if max_connections > 0 else 0

        return {
            "communities": len(self.nodes),
            "total_population": total_pop,
            "connections_total": len(self.connections),
            "connections_passable": passable,
            "connectivity_pct": round(connectivity, 1),
            "radio_coverage": f"{radio_nodes}/{len(self.nodes)}",
            "medical_coverage": f"{medical_nodes}/{len(self.nodes)}",
            "avg_food_security_pct": round(avg_food_security, 1),
        }


def network_report(network: CorridorNetwork) -> str:
    """Full corridor network report."""
    resilience = network.corridor_resilience()

    lines = [
        f"{'=' * 60}",
        f"CORRIDOR NETWORK REPORT: {network.name}",
        f"{'=' * 60}",
        f"Communities:    {resilience['communities']}",
        f"Population:     {resilience['total_population']:,}",
        f"Connectivity:   {resilience['connectivity_pct']}%",
        f"Radio coverage: {resilience['radio_coverage']}",
        f"Medical:        {resilience['medical_coverage']}",
        f"Avg food sec:   {resilience['avg_food_security_pct']}%",
        f"",
        f"── COMMUNITIES ──",
    ]

    for name, node in sorted(network.nodes.items()):
        neighbors = network.get_neighbors(name)
        lines.append(f"\n  {name} (pop. {node.population:,})")
        lines.append(f"    Food security: {node.food_security_pct}%")
        if node.surplus:
            lines.append(f"    Surplus: {', '.join(g.value for g in node.surplus)}")
        if node.needs:
            lines.append(f"    Needs:   {', '.join(g.value for g in node.needs)}")
        lines.append(f"    Radio: {'Yes' if node.has_radio else 'No'} | Medical: {'Yes' if node.has_medical else 'No'}")
        lines.append(f"    Connections: {len(neighbors)}")
        for neighbor, conn in neighbors:
            lines.append(f"      → {neighbor.name} ({conn.distance_miles} mi, {conn.connection_type.value})")

    # Trade opportunities
    lines += [f"", f"── TRADE MATCHES ──"]
    for name, node in network.nodes.items():
        for need in node.needs:
            sources = network.find_resource(name, need)
            if sources:
                closest = sources[0]
                lines.append(f"  {name} needs {need.value} → {closest['community']} ({closest['distance_miles']} mi)")

    lines.append(f"{'=' * 60}")
    return "\n".join(lines)


if __name__ == "__main__":
    # Southern MN corridor example
    corridor = CorridorNetwork("Southern MN Recovery Corridor")

    corridor.add_community(CommunityNode(
        "Fairmont", 10000, 43.6386, -94.1035,
        surplus=[TradeGood.KNOWLEDGE],
        needs=[TradeGood.SEED, TradeGood.LABOR],
        has_radio=True, has_medical=True,
        food_security_pct=5.0,
    ))
    corridor.add_community(CommunityNode(
        "Blue Earth", 3200, 43.6386, -94.0988,
        surplus=[TradeGood.TOOLS],
        needs=[TradeGood.MEDICINE, TradeGood.FOOD],
        has_radio=False, has_medical=True,
        food_security_pct=8.0,
    ))
    corridor.add_community(CommunityNode(
        "Truman", 1100, 43.8278, -94.4369,
        surplus=[TradeGood.FOOD, TradeGood.SEED],
        needs=[TradeGood.MEDICINE, TradeGood.TOOLS],
        has_radio=False, has_medical=False,
        food_security_pct=15.0,
    ))
    corridor.add_community(CommunityNode(
        "Welcome", 700, 43.6675, -94.6181,
        surplus=[TradeGood.LABOR],
        needs=[TradeGood.FOOD, TradeGood.MEDICINE],
        has_radio=False, has_medical=False,
        food_security_pct=3.0,
    ))

    corridor.add_connection(Connection("Fairmont", "Blue Earth", ConnectionType.HIGHWAY, 15))
    corridor.add_connection(Connection("Fairmont", "Truman", ConnectionType.COUNTY_ROAD, 18))
    corridor.add_connection(Connection("Fairmont", "Welcome", ConnectionType.HIGHWAY, 22))
    corridor.add_connection(Connection("Blue Earth", "Truman", ConnectionType.COUNTY_ROAD, 20))

    print(network_report(corridor))
