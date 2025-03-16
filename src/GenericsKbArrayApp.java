// Emmanuel Basua's Array Database
// Emmanuel Basua

import java.io.*;
import java.util.Scanner;


public class GenericsKbArrayApp {
    public static void main(String[] args) throws FileNotFoundException {
        String[] database = new String[50000]; // Array to store the knowledge base (max 50,000 entries)
        Scanner scnr = new Scanner(System.in); // Scanner to read user input from the console

        int choice = 0;  // Variable to store the user's menu choice

        // Main loop to keep the program running until the user chooses to quit (option 5)
        while (choice != 5) {
            // Display the menu options to the user

            System.out.println("\nChoose an action from the menu:");
            System.out.println("1. Load a knowledge base from a file");
            System.out.println("2. Add a new statement to the knowledge base");
            System.out.println("3. Search for a statement in the knowledge base by term");
            System.out.println("4. Search for a statement in the knowledge base by term and sentence");
            System.out.println("5. Quit");

            choice = scnr.nextInt();  // Read the user's choice from the console

            // Switch statement to handle the user's choice
            switch (choice) {
                case 1:
                    // Option 1: Load a knowledge base from a file
                    System.out.println("Enter a file name:");
                    String fileName = scnr.next(); // Read the file name from the user
                    try (BufferedReader reader = new BufferedReader(new FileReader("src/" + fileName))) {
                        // Open the file for reading using a BufferedReader
                        String line;
                        int i = 0;
                        // Read each line from the file until the end is reached
                        while ((line = reader.readLine()) != null) {
                            database[i] = line; // Store each line in the database array
                            i++; // Increment the index for the next line
                        }
                        System.out.println("Knowledge base loaded successfully."); // Confirm successful loading
                    } catch (IOException e) {
                        // Handle any errors that occur while reading the file
                        System.err.println("Error reading file: " + e.getMessage());
                    }
                    break;

                case 2:
                    // Option 2: Add a new statement to the knowledge base
                    scnr.nextLine(); // Clear the input buffer to avoid skipping the next input
                    System.out.println("Enter the term:");
                    String term = scnr.nextLine(); // Read the term from the user
                    System.out.println("Enter the statement:");
                    String sentence = scnr.nextLine(); // Read the statement from the user
                    System.out.println("Enter the confidence score:");
                    String confScore = scnr.next(); // Read the confidence score from the user

                    // Check if the term already exists in the database
                    if (find(term, database)) {
                        update(term, sentence, confScore, database); // Update the existing term with the new data
                        System.out.println("Statement for term " + term + " has been updated.");
                    } else {
                        // If the term doesn't exist, inform the user
                        System.out.println(term + " does not exist.");
                    }
                    break;

                case 3:
                    // Option 3: Search for a statement in the knowledge base by term
                    scnr.nextLine(); // Clear the input buffer
                    System.out.println("Enter the term to search:");
                    String term2 = scnr.nextLine(); // Read the term to search for

                    boolean result = find(term2, database); // Check if the term exists in the database
                    String definition = print(term2, database); // Retrieve the statement if the term is found

                    if (result) {
                        // If the term is found, display the statement and confidence score
                        System.out.println("Statement found: " + definition.replaceAll("^[^A-Z]*", "").replaceAll("\\d*", "").replaceAll("\\.*", "").trim()
                                + ". (Confidence score: " + definition.replaceAll("^[^0-9]*", "") + ")");

                        // Ask the user if they want to perform an enhanced search for partial matches
                        System.out.println("Would you like an enhanced search? (Y/N)");
                        char answer = scnr.next().charAt(0); // Read the user's response
                        if (answer == 'Y' || answer == 'y') {
                            if (findPartial(term2, database)) {
                                // If partial matches are found, display them
                                System.out.println("The following terms contain the keyword you are searching for: ");
                                printPartial(term2, database);
                            } else {
                                // If no partial matches are found,
                                System.out.println("The only partial match found is the term itself.");
                            }
                        } else {
                            // If the user declines enhanced search, display a message
                            System.out.println("Okay!");
                        }
                    } else {
                        // If no exact match is found, search for partial matches
                        System.out.println("No exact match found. Searching for partial matches...");
                        if (findPartial(term2, database)) {
                            // If partial matches are found, display them
                            System.out.println("Partial match(es) found:");
                            printPartial(term2, database);
                        } else {
                            // If no partial matches are found
                            System.out.println("No partial matches found.");
                        }
                    }
                    break;

                case 4:
                    // Option 4: Search for a statement by term and sentence
                    System.out.println("Enter the term:");
                    scnr.nextLine();  // Clear the input buffer
                    String term3 = scnr.nextLine(); // Read the term from the user
                    System.out.println("Enter the statement to search for:");
                    String sentence2 = scnr.nextLine(); // Read the statement from the user

                    // Check if both the term and statement exist in the database
                    if (find(term3, database) && findStatement(sentence2, term3, database)) {
                        String definition2 = print(term3, database); // Retrieve the statement if found
                        System.out.println("The statement was found and has a confidence score of "
                                + definition2.replaceAll("^[^0-9]*", "")); // Display the confidence score
                    }
                    break;

                case 5:
                    // Option 5: Quit the program
                    System.out.println("Goodbye!");
                    break;

                default:
                    // Handle invalid menu choices
                    System.out.println("Invalid option. Please try again.");
                    break;
            }
        }

        scnr.close(); // Close the scanner to free resources
    }

    /**
     *
     * @param key
     * @param database
     * @return
     */
    // Method to check if a term exists in the database
    public static boolean find(String key, String[] database) {
        for (int i = 0; i < database.length; i++) {
            if (database[i] != null) { // Skip null entries in the database
                // Extract the term from the database entry (removing non-alphabetic prefixes)
                int index = database[i].indexOf(database[i].replaceAll("^[^A-Z]*", "").charAt(0));
                String exact = database[i].substring(0, index).trim().toLowerCase(); // Get the term in lowercase
                if (key.trim().toLowerCase().equals(exact)) { // Compare the search term with the database term
                    return true; // Return true if a match is found
                }
            }
        }
        return false; // Return false if no match is found
    }

    /**
     *
     * @param key
     * @param database
     * @return
     */
    // Method to check for partial matches of a term in the database
    public static boolean findPartial(String key, String[] database) {
        boolean found = false; // Flag to track if any partial matches are found
        for (int i = 0; i < database.length; i++) {
            if (database[i] != null) { // Skip null entries
                // Extract the term from the database entry
                int index = database[i].indexOf(database[i].replaceAll("^[^A-Z]*", "").charAt(0));
                String exact = database[i].substring(0, index).trim().toLowerCase(); // Get the term in lowercase
                String searchTerm = key.toLowerCase().trim();

                // Check if the search term is a partial match for the database term (excluding exact match)
                if (exact.matches(".*" + "\\b" + searchTerm + "\\b" + ".*") && !exact.equals(searchTerm)) {
                    found = true; // Set the flag to true if a partial match is found
                }
            }
        }
        return found; // Return the flag value
    }

    /**
     *
     * @param key
     * @param word
     * @param database
     * @return
     */
    // Method to check if a specific statement exists for a given term
    public static boolean findStatement(String key, String word, String[] database) {
        for (String s : database) {
            if (s != null) { // Skip null entries
                // Extract the term from the database entry
                String exact = s.replaceAll("[A-Z].*", "").trim(); // Remove non-alphabetic prefixes
                if (word.toLowerCase().trim().matches(".*" + "\\b" + exact + "\\b" + ".*")) {
                    // Check if the search term matches the database term
                    if (s.toLowerCase().contains(key.toLowerCase())) {
                        // Check if the statement contains the search sentence
                        return true; // Return true if both conditions are met
                    }
                }
            }
        }
        return false; // Return false if no match is found
    }

    /**
     *
     * @param key
     * @param definition
     * @param confidence
     * @param database
     */
    // Method to update a term's statement and confidence score in the database
    public static void update(String key, String definition, String confidence, String[] database) {
        for (int i = 0; i < database.length; i++) {
            if (database[i] != null) { // Skip null entries
                // Extract the term from the database entry
                int index = database[i].indexOf(database[i].replaceAll("^[^A-Z]*", "").charAt(0));
                String exact = database[i].substring(0, index).trim().toLowerCase(); // Get the term in lowercase
                if (key.toLowerCase().trim().matches(".*" + "\\b" + exact + "\\b" + ".*")) {
                    // Check if the search term matches the database term
                    database[i] = key + " " + definition + " " + confidence; // Update the entry with new data
                    return; // Exit the method after updating
                }
            }
        }
    }

    /**
     *
     * @param key
     * @param database
     * @return
     */
    // Method to retrieve and return a term's statement from the database
    public static String print(String key, String[] database) {
        for (int i = 0; i < database.length; i++) {
            if (database[i] != null) { // Skip null entries
                // Extract the term from the database entry
                int index = database[i].indexOf(database[i].replaceAll("^[^A-Z]*", "").charAt(0));
                String exact = database[i].substring(0, index).trim().toLowerCase(); // Get the term in lowercase
                if (key.trim().toLowerCase().equals(exact)) { // Compare the search term with the database term
                    return database[i]; // Return the matching entry
                }
            }
        }
        return null; // Return null if no match is found
    }

    /**
     *
     * @param key
     * @param database
     */
    // Method to print all partial matches for a given term
    public static void printPartial(String key, String[] database) {
        for (int i = 0; i < database.length; i++) {
            if (database[i] != null) { // Skip null entries
                // Extract the term from the database entry
                int index = database[i].indexOf(database[i].replaceAll("^[^A-Z]*", "").charAt(0));
                String exact = database[i].substring(0, index).trim().toLowerCase(); // Get the term in lowercase
                String searchTerm = key.toLowerCase().trim();

                // Check if the search term is a partial match for the database term (excluding exact match)
                if (exact.matches(".*" + "\\b" + searchTerm + "\\b" + ".*") && !exact.equals(searchTerm)) {
                    System.out.println("Term: " + database[i].replaceAll("[A-Z].*", "") + "   Statement: "
                            + database[i].replaceAll("^[^A-Z]*", "").replaceAll("\\d*", "").replaceAll("\\.*", "").trim() +
                            ".  (Confidence score: " + database[i].replaceAll("^[^0-9]*", "") + ")");
                }
            }
        }
    }
}