
import java.util.Arrays;
import java.util.Comparator;
import java.util.LinkedList;
import java.util.Queue;

public class MyNaturalist extends Naturalist {

	private Node ship; // Node of the ship
	private Node[] animals = new Node[100]; //Array of animals, will expand if number of animals exceeds 100.
	private int animalCheck; // Index of the current animal being checked at the moment.
	private int numAnimals; // Total number of animals that the Naturalist has found so far.
	private int holding; // The number of animals that the Naturalist is holding.
	private Node[] path; // The current path that the naturalist has calculated to follow
	private Comparator<Node> nodeCompare = new nodeComparator(); // Comparator used to compare nodes by distances to ship

	private Queue<Node> bfs = new LinkedList<Node>();

	/** Method called by simulator to run the program */
	public void run() {
		exploreGraph();
		returnToShip();
		dropAll();
		calculatePaths();
		collectAnimals();
	}

	/** Explores the entire graph in a depth first search setting the userdata of nodes along the way */
	private void exploreGraph() {
		ship = getLocation();
		ship.setUserData(new NodeData(null, 0));
		exploreNode();
	}

	/** Explores a single node.
	 * 	Is called recursively to be able to check every node on the map.
	 * 	Also sets the user data for the nodes that it encounters for the first time. 
	 */
	private void exploreNode() {
		Node[] neighbors = getExits();
		Node[] open = new Node[4];
		Node cur = getLocation();
		if (listAnimalsPresent().size() > 0) {
			addAnimal(cur);
		}
		cur.<NodeData>getUserData().neighbors = neighbors;

		int new_dist = cur.<NodeData>getUserData().dist + 1;

		int tot = 0;

		for (Node n : neighbors) {
			if (n.<NodeData>getUserData() == null) {
				n.setUserData(new NodeData(cur, new_dist));
				open[tot] = n;
				tot++;
			}
			else {
				if (n.<NodeData>getUserData().dist > new_dist) {
					n.<NodeData>getUserData().parent = cur;
					n.<NodeData>getUserData().dist = new_dist;
				}
			}
		}
		if (tot == 0) {
			return;
		}
		for (int i=0; i<tot; i++) {
			travelTo(open[i]);
			exploreNode();
		}
	}

	/** Returns to the ship following parent nodes.
	 * 	If it encounters animals along the way, it picks them up if it has enough room to do so.
	 */
	private void returnToShip() {

		while(getLocation().<NodeData>getUserData().parent != null) {
			if (holding < MAX_ANIMAL_CAPACITY) {
				if (listAnimalsPresent().size() > 0) {
					collectNode();
				}
			}
			Node prev = getLocation();
			moveTo(prev.<NodeData>getUserData().parent);
			Node cur = getLocation();
			if (holding < MAX_ANIMAL_CAPACITY && getExits().length > 2) {
				for (Node n : getExits()) {
					if (n != prev && n != getLocation().<NodeData>getUserData().parent) {
						if (n.<NodeData>getUserData().hasAnimals) {
							moveTo(n);
							collectNode();
							moveTo(cur);
						}
					}
				}
			}
		}
	}

	/** Collects all the animals on the map.
	 *  Chooses to collect the farthest animal first and also pick up any animals it finds along the way back.
	 */
	private void collectAnimals() {
		Arrays.sort(animals, nodeCompare);
		path = new Node[animals[0].<NodeData>getUserData().dist];
		animalCheck = 0;
		holding = 0;
		while (animalCheck < numAnimals) {
			if (!animals[animalCheck].<NodeData>getUserData().hasAnimals) {
				animalCheck++;
				continue;
			}
			backTrace(animals[animalCheck]);
			int start = 0;
			while (path[start] == null) {
				start++;
			}
			for (int j=start; j<animals[animalCheck].<NodeData>getUserData().dist; j++) {
				moveTo(path[j]);
			}
			returnToShip();
			dropAll();
			holding = 0;
		}
	}

	/** Collects all the animals at the current node */
	private void collectNode() {
		if (holding + listAnimalsPresent().size() <= MAX_ANIMAL_CAPACITY) {
			Node cur = getLocation();
			if (cur.<NodeData>getUserData().hasAnimals) {
				cur.<NodeData>getUserData().hasAnimals = false;
			}
		}
		for (String a : listAnimalsPresent()) {
			if (holding >= MAX_ANIMAL_CAPACITY) {
				break;
			}
			collect(a);
			holding++;
		}
	}

	/** Travels to a node even if not adjacent
	 *  Assumes that the node it wants to travel to is along the path back to the ship.
	 */
	private void travelTo(Node n) {
		Node pos = getLocation();
		if (pos.isAdjacent(n)) {
			moveTo(n);
		}
		else {
			moveTo(pos.<NodeData>getUserData().parent);
			travelTo(n);
		}
	}

	/** Calculates the path from the ship to a node by using each node's parents. */
	private void backTrace(Node n) {
		int i = n.<NodeData>getUserData().dist - 1;
		while (n.<NodeData>getUserData().parent != null) {
			path[i] = n;
			i--;
			n = n.<NodeData>getUserData().parent;
		}
		while (i >= 0) {
			path[i] = null;
			i--;
		}
	}

	/** Adds a single node to the list of animals
	 *  If it exceeds the size of the array, then it increases the size by 100.
	 */
	private void addAnimal(Node n) {
		if (numAnimals >= animals.length) {
			Node[] old = animals;
			animals = new Node[animals.length + 100];
			for (int i=0; i<old.length; i++) {
				animals[i] = old[i];
			}
		}
		animals[numAnimals] = n;
		n.<NodeData>getUserData().hasAnimals = true;
		numAnimals++;
	}

	/** Uses a BFS in order to calculate the minimal paths from the ship to every animal. */
	private void calculatePaths() {
		bfs.add(ship);
		ship.<NodeData>getUserData().done = true;
		while (!bfs.isEmpty()) {
			Node n = bfs.poll();
			for (Node neighbor : n.<NodeData>getUserData().neighbors) {
				if (!neighbor.<NodeData>getUserData().done){
					neighbor.<NodeData>getUserData().done = true;
					neighbor.<NodeData>getUserData().dist = n.<NodeData>getUserData().dist + 1;
					neighbor.<NodeData>getUserData().parent = n;
					bfs.add(neighbor);
				}
			}
		}
	}



	/** Class used to compare two nodes based on its distance to a third node.
	 *  By default, compares to nodes based on their distance to the ship
	 *  If comparing distance to ship, gives farther nodes first, otherwise gives closer nodes first.
	 */
	private class nodeComparator implements Comparator<Node> { 

		/** Overridden function for comparison of nodes */
		public int compare(Node n1, Node n2) {
			if (n1 == null && n2 == null) {
				return 0;
			}
			if (n1 == null) {
				return 1;
			}
			if (n2 == null) {
				return -1;
			}
			return n2.<NodeData>getUserData().dist - n1.<NodeData>getUserData().dist;
		}

	}

	/** Class used to store data in each node */
	private class NodeData {

		public Node parent; // Parent of current node, is node closer to ship than the current one.
		public int dist; // Approximate distance calculated to the ship. 
		public boolean hasAnimals = false; // A flag for if the node has animals or not.
		public Node[] neighbors; // List of the neighbors of the node.
		public boolean done = false; // A flag for if the node has had the shortest path calculated or not.

		/** Constructor for the node data */
		public NodeData(Node n, int d) {
			parent = n;
			dist = d;
		}

	}


}
