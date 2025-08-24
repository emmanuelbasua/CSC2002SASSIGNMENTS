/**
 * DungeonHunterParallel.java
 *
 * Parallel version of the Dungeon Hunter assignment using ForkJoin framework.
 * This program initializes the dungeon map and performs a series of parallel searches
 * to locate the global maximum.
 *
 * Usage:
 *   java DungeonHunterParallel <gridSize> <numSearches> <randomSeed>
 *
 */

import java.util.Random;
import java.util.concurrent.ForkJoinPool;
import java.util.concurrent.RecursiveAction;

class DungeonSearch extends RecursiveAction {
    private static final int SEQUENTIAL_CUTOFF = 1600; // Adjust based on testing

    private HuntParallel[] searches;
    private int lo, hi;
    private int[] results;

    public DungeonSearch(HuntParallel[] searches, int lo, int hi, int[] results) {
        this.searches = searches;
        this.lo = lo;
        this.hi = hi;
        this.results = results;
    }

    @Override
    protected void compute() {
        if (hi - lo < SEQUENTIAL_CUTOFF) {
            // Sequential execution for small ranges
            for (int i = lo; i < hi; i++) {
                results[i] = searches[i].findManaPeak();
            }
        } else {
            // Divide and conquer
            int mid = (lo + hi) / 2;
            DungeonSearch left = new DungeonSearch(searches, lo, mid, results);
            DungeonSearch right = new DungeonSearch(searches, mid, hi, results);

            left.fork();
            right.compute();
            left.join();
        }
    }
}

class DungeonHunterParallel {
    static final boolean DEBUG = false;
    private static final ForkJoinPool fjPool = new ForkJoinPool();

    // Timers for how long it all takes
    static long startTime = 0;
    static long endTime = 0;
    private static void tick() { startTime = System.currentTimeMillis(); }
    private static void tock() { endTime = System.currentTimeMillis(); }

    public static void main(String[] args) {

        double xmin, xmax, ymin, ymax; // Dungeon limits - dungeons are square
        DungeonMapParallel dungeon;  // Object to store the dungeon as a grid

        int numSearches = 10, gateSize = 10;
        HuntParallel[] searches;  // Array of searches

        Random rand = new Random();  // The random number generator
        int randomSeed = 0;  // Set seed to have predictability for testing

        if (args.length != 3) {
            System.out.println("Incorrect number of command line arguments provided.");
            System.exit(0);
        }

        /* Read argument values */
        try {
            gateSize = Integer.parseInt(args[0]);
            if (gateSize <= 0) {
                throw new IllegalArgumentException("Grid size must be greater than 0.");
            }

            numSearches = (int) (Double.parseDouble(args[1]) * (gateSize * 2) * (gateSize * 2) * DungeonMapParallel.RESOLUTION);

            randomSeed = Integer.parseInt(args[2]);
            if (randomSeed < 0) {
                throw new IllegalArgumentException("Random seed must be non-negative.");
            } else if (randomSeed > 0) {
                rand = new Random(randomSeed);
            }
        } catch (NumberFormatException e) {
            System.err.println("Error: All arguments must be numeric.");
            System.exit(1);
        } catch (IllegalArgumentException e) {
            System.err.println("Error: " + e.getMessage());
            System.exit(1);
        }

        xmin = -gateSize;
        xmax = gateSize;
        ymin = -gateSize;
        ymax = gateSize;
        dungeon = new DungeonMapParallel(xmin, xmax, ymin, ymax, randomSeed); // Initialize dungeon

        int dungeonRows = dungeon.getRows();
        int dungeonColumns = dungeon.getColumns();
        searches = new HuntParallel[numSearches];

        // Initialize searches at random locations in dungeon
        for (int i = 0; i < numSearches; i++) {
            searches[i] = new HuntParallel(i + 1, rand.nextInt(dungeonRows),
                    rand.nextInt(dungeonColumns), dungeon);
        }

        // Do all the searches in parallel
        int[] results = new int[numSearches];

        tick();  // Start timer

        // Execute parallel search using ForkJoin
        fjPool.invoke(new DungeonSearch(searches, 0, numSearches, results));

        // Find the maximum result and which search found it
        int max = Integer.MIN_VALUE;
        int finder = -1;

        for (int i = 0; i < numSearches; i++) {
            if (results[i] > max) {
                max = results[i];
                finder = i; // Keep track of who found it
            }
            if (DEBUG) {
                System.out.println("Shadow " + searches[i].getID() + " finished at " + results[i] + " in " + searches[i].getSteps());
            }
        }

        tock(); // End timer

        System.out.printf("\t dungeon size: %d,\n", gateSize);
        System.out.printf("\t rows: %d, columns: %d\n", dungeonRows, dungeonColumns);
        System.out.printf("\t x: [%f, %f], y: [%f, %f]\n", xmin, xmax, ymin, ymax);
        System.out.printf("\t Number searches: %d\n", numSearches);

        /* Total computation time */
        System.out.printf("\n\t time: %d ms\n", endTime - startTime);
        int tmp = dungeon.getGridPointsEvaluated();
        System.out.printf("\tnumber dungeon grid points evaluated: %d  (%2.0f%s)\n", tmp, (tmp * 1.0 / (dungeonRows * dungeonColumns * 1.0)) * 100.0, "%");

        /* Results */
        System.out.printf("Dungeon Master (mana %d) found at:  ", max);
        System.out.printf("x=%.1f y=%.1f\n\n", dungeon.getXcoord(searches[finder].getPosRow()), dungeon.getYcoord(searches[finder].getPosCol()));
        dungeon.visualisePowerMap("visualiseSearch.png", false);
        dungeon.visualisePowerMap("visualiseSearchPath.png", true);
    }
}