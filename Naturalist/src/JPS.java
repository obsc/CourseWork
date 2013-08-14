
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.PriorityQueue;
import java.util.Stack;


/** An instance contains method run() for a player that attempts to retrieve all animals.
    The algorithm the naturalist uses is documented in the README file */
public class MyNaturalist extends Naturalist {

	private Node ship;
	private HashMap<Pos, Node> map = new HashMap<Pos, Node>(); //A map of the nodes that the naturalist sees along his travels.
	private PriorityQueue<Node> animalNodes = new PriorityQueue<Node>(11, new Comparator<Node>(){
		public int compare(Node n1, Node n2) {
			return manhattanDist(ship, n2) - manhattanDist(ship, n1);
		}
	});

	/** Method to run the naturalist program. Called by the Simulator. */
	public void run() {
		ship = getLocation();
		exploreGraph();
//		collectAnimals();
	}

	/** Method to first explore the graph to map the island and locate all the animals */
	private void exploreGraph() {
		Stack<Node> open = new Stack<Node>();
		HashSet<Node> closed = new HashSet<Node>();

		Node start = getLocation();
		open.push(start);
		map.put(new Pos(start), start);
		start.setUserData(new NodeData());

		while (!open.empty()) {
			Node next = open.pop();
			closed.add(next);
			
			Node cur = getLocation();
			
			travelTo(next);

			if (listAnimalsPresent().size() > 0) {
				animalNodes.add(next);
			}
			for (Node n : getExits()) {
				if (!closed.contains(n) && !open.contains(n)) {
					n.setUserData(new NodeData(next));
					open.push(n);
					map.put(new Pos(n), n);
				}
			}
		}
	}
	
	private void collectAnimals() {
		while (!animalNodes.isEmpty()) {
			travelTo(animalNodes.poll());
		}
	}

	/** Travels to a specific node from the current position */
	private void travelTo(Node n) {
		if (getLocation().isAdjacent(n)) {
			moveTo(n);
		}
		else {
			Stack<Node> path = pathFindJPS(getLocation(),n);
			while (!path.isEmpty()) {
				goTo(path.pop());
			}
//			moveTo(getLocation().<NodeData>getUserData().prev);
//			travelTo(n);
		}
	}

	private void goTo(Node n) {
		try {
			moveTo(n);
		}
		catch (IllegalMoveException e) {
			Node pos = getLocation();
			int x = pos.getX();
			int y = pos.getY();
			int dx = n.getX() - pos.getX();
			int dy = n.getY() - pos.getY();
			
			dx /= Math.max(Math.abs(dx),1);
			dy /= Math.max(Math.abs(dy),1);
			
			if (dx == 0) {
				moveTo(map.get(new Pos(x, y + dy)));
				goTo(n);
			}
			else if (dy == 0) {
				moveTo(map.get(new Pos(x + dx, y)));
				goTo(n);
			}
			else {
				if (map.get(new Pos(x + dx, y)) != null) {
					moveTo(map.get(new Pos(x + dx, y)));
				}
				else {
					moveTo(map.get(new Pos(x, y + dy)));
				}
				moveTo(map.get(new Pos(x + dx, y + dy)));
				goTo(n);
			}
		}
	}

	/** Path finds using a jump point search */
	private Stack<Node> pathFindJPS(Node start, Node end) {
		// Priority Queue default size is 11, there aren't any constructors that let you use a comparator without specifying size
		PriorityQueue<Node> pq = new PriorityQueue<Node>(11, new Comparator<Node>() {
			public int compare(Node n1, Node n2) {
				return n1.<NodeData>getUserData().f - n2.<NodeData>getUserData().f;
			}
		});
		HashSet<Node> open = new HashSet<Node>();
		HashSet<Node> closed = new HashSet<Node>();

		start.<NodeData>getUserData().clear();
		pq.add(start);
		open.add(start);

		while (!pq.isEmpty()) {
			Node n = pq.poll();
			closed.add(n);

			if (n == end) {
				return backTrace(end);
			}

			findJumpNodes(n, pq, open, closed, end);
		}
		return new Stack<Node>();
	}

	private void findJumpNodes(Node n, PriorityQueue<Node> pq, HashSet<Node> open, HashSet<Node> closed, Node end) {
		Node[] neighbors = getDiagNeighbors(n.getX(),n.getY());
		neighbors = pruneNeighbors(n, neighbors);

		for (Node neighbor : neighbors) {
			Node jumpPoint = jump(neighbor.getX(), neighbor.getY(), n.getX(), n.getY(), end);
			
			if (jumpPoint != null && !closed.contains(jumpPoint)) {
				int d = manhattanDist(n, jumpPoint);
				int new_g = n.<NodeData>getUserData().g + d;
				
				if (!open.contains(jumpPoint) || new_g < jumpPoint.<NodeData>getUserData().g) {
					jumpPoint.<NodeData>getUserData().g = new_g;
					jumpPoint.<NodeData>getUserData().f = new_g + manhattanDist(jumpPoint, end);
					jumpPoint.<NodeData>getUserData().prev = n;
					
					if (open.contains(jumpPoint)) {
						pq.remove(jumpPoint);
					}
					pq.add(jumpPoint);
					open.add(jumpPoint);
					
				}
				
			}
		}

	}

	private Node jump(int x, int y, int px, int py, Node end) {
		int dx = x-px;
		int dy = y-py;

		Node cur = map.get(new Pos(x,y));
		
		if (map.get(new Pos(x,y)) == null) {
			return null;
		}

		if (cur == end) {
			return cur;
		}

		if (dx != 0 && dy != 0) {
			if ((map.get(new Pos(x - dx, y + dy)) != null && map.get(new Pos(x - dx, y)) == null) || 
					(map.get(new Pos(x + dx, y - dy)) != null && map.get(new Pos(x, y - dy)) == null)) {
				return cur;
			}			
		}
		else if (dx != 0) {
			if ((map.get(new Pos(x + dx, y + 1)) != null && map.get(new Pos(x, y + 1)) == null) || 
					(map.get(new Pos(x + dx, y - 1)) != null && map.get(new Pos(x, y - 1)) == null)) {
				return cur;
			}	
		}
		else {
			if ((map.get(new Pos(x + 1, y + dy)) != null && map.get(new Pos(x + 1, y)) == null) || 
					(map.get(new Pos(x - 1, y + dy)) != null && map.get(new Pos(x - 1, y)) == null)) {
				return cur;
			}
		}
		
		if (dx != 0 && dy != 0) {
			Node jx = jump(x + dx, y, x, y, end);
			Node jy = jump(x, y + dy, x, y, end);
			if (jx != null || jy != null) {
				return cur;
			}
		}
		if (map.get(new Pos(x + dx, y)) != null || map.get(new Pos(x, y + dy)) != null) {
			return jump(x + dx, y + dy, x, y, end);
		}
		
		return null;
	}

	private Node[] pruneNeighbors(Node n, Node[] neighbors) {
		if (n.<NodeData>getUserData().prev != null) {
			int dx = n.getX() - n.<NodeData>getUserData().prev.getX();
			int dy = n.getY() - n.<NodeData>getUserData().prev.getY();

			dx /= Math.max(Math.abs(dx),1);
			dy /= Math.max(Math.abs(dy),1);
			int i;

			if (dy == 1) {
				i = 1 - dx;
			}
			else if (dy == -1) {
				i = 5 + dx;
			}
			else {
				i = 5 + 2 * dx;
			}

			if (i%2==0) {
				if (neighbors[(i+1)%8] != null) {
					neighbors[(i+2)%8] = null;
				}
				if (neighbors[(i+7)%8] != null) {
					neighbors[(i+6)%8] = null;
				}
				neighbors[i] = null;
			}
			else {
				if (neighbors[(i+2)%8] != null) {
					neighbors[(i+3)%8] = null;
				}
				if (neighbors[(i+6)%8] != null) {
					neighbors[(i+5)%8] = null;
				}
				neighbors[i] = null;
				neighbors[(i+1)%8] = null;
				neighbors[(i+7)%8] = null;
			}
		}

		ArrayList<Node> prune = new ArrayList<Node>();
		for (int j=0; j<8; j++) {
			if (neighbors[j] != null) {
				prune.add(neighbors[j]);
			}
		}
		neighbors = new Node[prune.size()];
		prune.toArray(neighbors);
		return neighbors;
	}

	private Node[] getDiagNeighbors(int x, int y) {
		Node[] neighbors = new Node[8];
		boolean[] adj = new boolean[4];
		for (int i=0,dx=0,dy=-1; i<4; i++) {
			Pos pos = new Pos(x+dx,y+dy);
			if (map.get(pos) != null) {
				neighbors[2*i + 1] = map.get(pos);
				adj[i] = true;
			}
			int tmp = -dy;
			dy = dx;
			dx = tmp;
		}
		for (int i=0,dx=-1,dy=-1; i<4; i++) {
			Pos pos = new Pos(x+dx,y+dy);
			if ((adj[i] || adj[(i+3)%4]) && map.get(pos) != null) {
				neighbors[2*i] = map.get(pos);
			}
			int tmp = -dy;
			dy = dx;
			dx = tmp;
		}
		return neighbors;
	}

	private Stack<Node> backTrace(Node end) {
		Stack<Node> path = new Stack<Node>();
		Node n = end;
		while (n.<NodeData>getUserData().prev != null) {
			path.push(n);
			n = n.<NodeData>getUserData().prev;
		}
		return path;
	}

	/** Returns the manhattan distance between two points */
	private int manhattanDist(int x1, int y1, int x2, int y2) {
		return Math.abs(x2 - x1) + Math.abs(y2 - y1);
	}

	
	private int manhattanDist(Node n1, Node n2) {
		return manhattanDist(n1.getX(), n1.getY(), n2.getX(), n2.getY());
	}


	/** Nested class used to encapsulate the data for storing in nodes */
	private class NodeData {

		public Node parent;
		public int dist;
		public Node prev; //Holds the previous node for use in path finding.
		public int f; //Holds the sum of the distance from a start node and a heuristic function.
		public int g; //Holds the distance from a start node.
		
		/** Constructor for this data */
		public NodeData() {
		}

		public NodeData(Node n, int d) {
			parent = n;
			dist = d;
		}
		
		public NodeData(Node n) {
			prev = n;
		}
		
		public void clear() {
			prev = null;
			f = 0;
			g = 0;
		}
	}

	
	
	private class Pos {

		public int x;
		public int y;

		public Pos(int x, int y) {
			this.x = x;
			this.y = y;
		}

		public Pos(Node n) {
			x = n.getX();
			y = n.getY();
		}

		public @Override boolean equals(Object o) {
			if (!(o instanceof Pos)) {
				return false;
			}
			return (x == ((Pos)o).x) && (y == ((Pos)o).y);
		}

		public @Override int hashCode() {
			int hash = 17;
			hash = 31 * hash + ((Integer)x).hashCode();
			hash = 31 * hash + ((Integer)y).hashCode();
			return hash;
		}
	}

}
