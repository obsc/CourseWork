import java.util.Random;

/** An instance contains method run() for a player that does a random walk of the island.
    The player picks up any animals it finds. If its bag gets full, it drops everything
    and starts again. At each step, with 50% probability it will drop everything it has.  */
public class RandomWalkNaturalist extends Naturalist {
	public void run() {
	    while (true) { 
			Node[] exits= getExits();  // List of nodes that cane be reached from present location

			// Pick a random node and move there
			Random rng= getRandom();  // get the random number generator
			Node choice= exits[rng.nextInt(exits.length)];  // pick a random exit node

			moveTo(choice);

			// If there are any animals at this location, pick them up
			for (String animalName : listAnimalsPresent()) {  
				try {
					collect(animalName);
				} catch (CapacityExceededException e) {
					dropAll(); // Out of space! Drop everything and try again
					collect(animalName);
				}
			}
			
			// If anything is being carried, drop it with 50% probability
			if (getInventory().size() > 0 && rng.nextBoolean()) {
				dropAll();
			}
			
		} 
	}

}
