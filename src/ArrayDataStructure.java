import java.io.File;
import java.util.Scanner;
import java.io.FileNotFoundException;

public class ArrayDataStructure {
    public static void main(String[] args) throws FileNotFoundException {

        File file = new File("C:/Users/basua/OneDrive/Desktop/GenericsKB.txt");
        Scanner scan = new Scanner(file);
        String[] array = new String[100000];
        int i = 0;
        while (scan.hasNextLine() && i < array.length) {
            array[i] = scan.nextLine();
            i++;
        }
        scan.close();
        readKey("public nuisance", array);
        readString("Lighting bugs have wings", "lighting bug", array);
        update("chatterbox", "Chatterbox is a youtuber", 0.77, array);
        readKey("chatterbox", array);
    }
    //public read(File data, )
    public static void readKey(String key, String[] database) {
        boolean found = false;

        for (int i = 0; i < database.length; i++) {
            if (database[i] != null) { // Avoid null pointers if array isn't full
                int index = database[i].indexOf(database[i].replaceAll("^[^A-Z]*", "").charAt(0));
                ; // Find first space
                if (index != -1) { // Check if space exists
                    String keyword = database[i].substring(0, index).trim();
                    if (keyword.equalsIgnoreCase(key)) {
                        System.out.println(database[i]);
                        found = true;

                    }

                }
            }
        }

        if (!found) { // Only print this once after all lines are checked
            System.out.println("The word is not in the database");
        }

    }

    public static void readString(String key, String word, String[] database) {
        boolean found = false;

        boolean found2 = false;

        for (int i = 0; i < database.length; i++) {
            if (database[i] != null) { // Avoid null pointers if array isn't full
                int index = database[i].indexOf(database[i].replaceAll("^[^A-Z]*", "").charAt(0));
                ; // Find first space
                if (index != -1) { // Check if space exists
                    String keyword = database[i].substring(0, index).trim();
                    if (keyword.equalsIgnoreCase(word)) {
                        String sentence = database[i].replaceAll("^[^A-Z]*", "").replaceAll("\\.*", "").replaceAll("\\d*", "");
                        ;

                        if (sentence.trim().equals(key)) {
                            // Print the remaining part of the string
                            System.out.println("The staement appears in array and has a confidence level of " + database[i].substring(database[i].indexOf(database[i].replaceAll("^[^0-9]*", "").charAt(0)), database[i].length()));
                            found = true;
                            break; // Exit once the key is found
                        }
                        found2 = true;

                    }

                }
            }
        }


        if (!found) { // Only print this once after all lines are checked
            System.out.println("The word is not in the database");
        }

    }

    public static void update(String key, String definition, double confidence, String[] database) {
        boolean found = false;

        for (int i = 0; i < database.length; i++) {
            if (database[i] != null) { // Avoid null pointers if array isn't full
                int index = database[i].indexOf(database[i].replaceAll("^[^A-Z]*", "").charAt(0));
                ; // Find first space
                if (index != -1) { // Check if space exists
                    String keyword = database[i].substring(0, index).trim();
                    if (keyword.equalsIgnoreCase(key)) {
                        database[i] = key + " " + definition + " " + confidence;
                        found = true;

                    }

                }
            }
        }
    }
}