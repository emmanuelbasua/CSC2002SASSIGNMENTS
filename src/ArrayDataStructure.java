import java.io.File;
import java.util.Scanner;
import java.io.FileNotFoundException;

public class ArrayDataStructure {
        public static void main(String[] args) throws FileNotFoundException {
            String[] database = new String[17];
            Scanner scnr = new Scanner(System.in);

            int choice = 0;  // Initialize choice variable

            while (choice != 5) {  // Continue looping until the user selects option 5
                System.out.println("Choose an action from the menu:");
                System.out.println("1. Load a knowledge base from a file");
                System.out.println("2. Add a new statement to the knowledge base");
                System.out.println("3. Search for a statement in the knowledge base by term");
                System.out.println("4. Search for a statement in the knowledge base by term and sentence");
                System.out.println("5. Quit");

                choice = scnr.nextInt();  // Read user's choice

                switch (choice) {
                    case 1:
                        System.out.println("Enter a file name:");
                        String fileName = scnr.next();
                        File file = new File("C:/Users/basua/OneDrive/Desktop/" + fileName);
                        Scanner scan = new Scanner(file);

                        int i = 0;
                        while (scan.hasNextLine() && i < database.length) {
                            database[i] = scan.nextLine();
                            i++;
                        }
                        scan.close();
                        System.out.println("Knowledge base loaded successfully.");
                        break;
                    case 2:
                        scnr.nextLine();
                        System.out.println("Enter the term:");
                        String term = scnr.nextLine();
                        System.out.println("Enter the statement:");
                        String sentence = scnr.nextLine();
                        System.out.println("Enter the confidence score:");
                        String confScore = scnr.next();

                        if (readKey(term, database)) {
                            update(term,sentence,confScore, database);
                            System.out.println("Statement for term " + term+  " has been updated.");}
                        else{
                            System.out.println(term + " does not exist.");
                        }

                        break;
                    case 3:
                        scnr.nextLine();
                        System.out.println("Enter the term to search:");
                        // Clear any leftover newline
                        String term2 = scnr.nextLine();

                         boolean result = readKey(term2,database);
                         String definition = print(term2,database);
                         //System.out.println(definition);
                        if (result) {
                            System.out.println("Statement found: " + definition.replaceAll("^[^A-Z]*", "").replaceAll("\\d*", "").replaceAll("\\.*", "").trim()
                                    + ". (Confidence score: " + definition.replaceAll("^[^0-9]*", "") + " )");

                            System.out.println("Would you like an enhanced search? (Y/N)");
                            char answer = scnr.next().charAt(0);
                            if (answer == 'Y') {
                                if (readKeyPartial(term2, database)) {
                                    System.out.println("The following terms contain the keyword you are searching for: ");
                                    printPartial(term2,database);
                                }
                                else{
                                    System.out.println("No other term contains the keyword you are searching for: ");
                                }
                            }
                            else{
                                System.out.println("Okay, bucko!");
                            }
                        } else  {

                            System.out.println("No exact match found. Searching for partial matches...");
                            if (readKeyPartial(term2,database)){
                                System.out.println("Partial match(es) found:");
                                printPartial(term2,database);

                            }
                            else {System.out.println(term2 + "No partial matches found does not exist.");};

                        }
                        break;
                    case 4:
                        System.out.println("Enter the term:");
                        scnr.nextLine();  // Clear the buffer
                        String term3 = scnr.nextLine();
                        System.out.println("Enter the statement to search for:");
                        String sentence2 = scnr.nextLine();
                        if (readKey(term3, database) && readString(sentence2, term3, database)) {
                        String definition2 = print(term3,database);
                           System.out.println("The statement was found and has a confidence score of "
                                   + definition2.replaceAll("^[^0-9]*", ""))
                                   ;}
                        break;
                    case 5:
                        System.out.println("Goodbye!");
                        break;
                    default:
                        System.out.println("Invalid option. Please try again.");
                        break;
                }
            }

            scnr.close();
        }

    public static boolean readKey(String key, String[] database) {
        for (int i = 0; i < database.length; i++) {
            int index = database[i].indexOf(database[i].replaceAll("^[^A-Z]*", "").charAt(0));
            String exact = database[i].substring(0,index).trim().toLowerCase();
            //System.out.println(exact);
            // Avoid null pointers if array isn't full
            if (database[i] != null) {
                if (key.trim().toLowerCase().equals(exact)) {
                    //System.out.println(exact);
                    // Check if space exists
                    //System.out.println(database[i]);
                    return true;
                }
            }  }
        return false;
    }
    public static boolean readKeyPartial(String key, String[] database) {
        boolean found = false;  // Flag to check if any matches are found
        for (int i = 0; i < database.length; i++) {
            int index = database[i].indexOf(database[i].replaceAll("^[^A-Z]*", "").charAt(0));
            String exact = database[i].substring(0,index).trim().toLowerCase();
            if (database[i] != null){
            if (exact.trim().matches(".*" + "\\b" + key.toLowerCase().trim() + "\\b" + ".*")) {
                    // Print the sentence if the key matches
                    //System.out.println(exact);
                    found = true; // Set found flag to true
                }
            }}

        return found; // Return true if at least one match is found, false otherwise
    }


    public static boolean readString(String key, String word, String[] database) {
        for (String s : database) {
            String exact = s.replaceAll("^[^A-Z]*", "").trim();
            // Avoid null pointers if array isn't full
            if (word.toLowerCase().trim().matches(".*" + "\\b" + exact + "\\b" + ".*")) {
                if (s.toLowerCase().contains(key.toLowerCase())) {
                    // Print the remaining part of the string
                    // System.out.println("The statement appears in array and has a confidence level of " + database[i].substring(database[i].indexOf(database[i].replaceAll("^[^0-9]*", "").charAt(0)), database[i].length()));
                    return true;
                }
            }
        }
        return false;
    }


    public static void update(String key, String definition, String confidence, String[] database) {

        for (int i = 0; i < database.length; i++) {
            int index = database[i].indexOf(database[i].replaceAll("^[^A-Z]*", "").charAt(0));
            String exact = database[i].substring(0,index).trim().toLowerCase();
            if (database[i] != null) { // Avoid null pointers if array isn't full
                if (key.toLowerCase().trim().matches(".*"+ "\\b" + exact + "\\b" + ".*")) {
                    database[i] = key + " " + definition + " " + confidence;
                    return;

                }

            }}
    }

    public static String print(String key, String[] database) {
        for (int i = 0; i < database.length; i++) {
            int index = database[i].indexOf(database[i].replaceAll("^[^A-Z]*", "").charAt(0));
            String exact = database[i].substring(0, index).trim().toLowerCase();
            //System.out.println(exact);
            // Avoid null pointers if array isn't full
            if (database[i] != null) {
                if (key.trim().toLowerCase().equals(exact)) {
                    //System.out.println(exact);
                    // Check if space exists
                    //System.out.println(database[i]);
                    return database[i];
                }


            }
        } return null;}
    public static void printPartial(String key, String[] database) {
        for (int i = 0; i < database.length; i++) {
            int index = database[i].indexOf(database[i].replaceAll("^[^A-Z]*", "").charAt(0));
            String exact = database[i].substring(0,index).trim().toLowerCase();
            // Avoid null pointers if array isn't full
            if (exact.trim().matches(".*" + "\\b" + key.toLowerCase().trim() + "\\b" + ".*")) {
                // Print the sentence if the key matches
                System.out.println(database[i]);
        }

    }

}}
