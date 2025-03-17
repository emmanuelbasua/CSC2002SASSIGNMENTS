// Emmanuel Basua's Binary Tree derived from Hussein's Binary Search Tree
// 14 March 2025
// Emmanuel Basua

import java.io.*;
import java.util.Scanner;

public class GenericsKbBSTApp<dataType extends Comparable<? super dataType>> extends BinaryTree<dataType> {

   public static void main(String[] args) throws FileNotFoundException {
      GenericsKbBSTApp<String> tree = new GenericsKbBSTApp<>(); // Create a binary search tree for strings
      Scanner scn = new Scanner(System.in); // Scanner for user input

      int choice = 0;  // Initialize choice variable to store user's menu selection

      // Main loop to display the menu and handle user choices
      while (choice != 5) {  // Continue looping until the user selects option 5 (Quit)
         System.out.println("\nChoose an action from the menu:");
         System.out.println("1. Load a knowledge base from a file");
         System.out.println("2. Add a new statement to the knowledge base");
         System.out.println("3. Search for a statement in the knowledge base by term");
         System.out.println("4. Search for a statement in the knowledge base by term and sentence");
         System.out.println("5. Quit");

         choice = scn.nextInt();  // Read user's choice from the input

         // Switch statement to handle the user's choice
         switch (choice) {
            case 1:
               // Option 1: Load a knowledge base from a file
               System.out.println("Enter a file name:");
               String fileName = scn.next();
               File file = new File("src/" + fileName);

               // Try to read the file and insert each line into the tree
               try (BufferedReader reader = new BufferedReader(new FileReader(file))) {
                  String line;
                  while ((line = reader.readLine()) != null) {
                     line = line.trim(); // Remove leading/trailing whitespace
                     if (!line.isEmpty()) { // Skip empty lines
                        tree.insert(line);  // Insert non-empty lines into the tree
                     }
                  }
                  System.out.println("Knowledge base loaded successfully.");
               } catch (IOException e) {
                  System.err.println("Error reading file: " + e.getMessage());  // Handle file reading errors
               }
               break;

            case 2:
               // Option 2: Add a new statement to the knowledge base
               scn.nextLine();  // Clear the buffer to avoid any leftover newline characters
               System.out.println("Enter the term:");
               String term = scn.nextLine(); // Read the term
               System.out.println("Enter the statement:");
               String sentence = scn.nextLine(); // Read the statement
               System.out.println("Enter the confidence score:");
               String confScore = scn.next(); // Read the confidence score

               // Combine the term, sentence, and confidence score into a single string
               String newLine = term + " " + sentence + " " + confScore;

               // Check if the term already exists in the tree
               BinaryTreeNode<String> termNode = tree.find(term.trim());
               if (termNode == null) {  // If term is not found, insert it as a new entry
                  tree.insert(newLine);
                  System.out.println("The term " + term + " was unique. Knowledge base has been successfully updated.");
               } else {  // If term exists, update the existing entry
                  tree.insert(newLine);
                  System.out.println("The term for " + term + " has been updated.");
               }
               break;

            case 3:
               // Option 3: Search for a statement in the knowledge base by term
               scn.nextLine();  // Clear any leftover newline characters
               System.out.println("Enter the term to search:");
               String term2 = scn.nextLine(); // Read the term to search for
               BinaryTreeNode<String> result = tree.find(term2.trim()); // Search for the term in the tree

               if (result != null) {
                  // If the term is found, display the statement and confidence score
                  String definition = result.data;
                  System.out.println("Statement found: " + definition.replaceAll("^[^A-Z]*", "").replaceAll("\\d*", "").replaceAll("\\.*", "").trim()
                          + ". (Confidence score: " + definition.replaceAll("^[^0-9]*", "") + " )");

                  // Ask the user if they want to perform an enhanced search for partial matches
                  System.out.println("Would you like an enhanced search? (Y/N)");
                  char answer = scn.next().charAt(0); // Read the user's response
                  if (answer == 'Y' || answer == 'y') {
                     boolean hasPartialMatches = tree.findPartial(term2); // Call findPartial and check for matches
                     if (!hasPartialMatches) {
                        System.out.println("The only partial match found is the term itself."); // Print if no partial matches are found
                     }
                  } else {
                     System.out.println("Okay!");
                  }
               } else {
                  // If no exact match is found, search for partial matches
                  System.out.println("No exact match found. Searching for partial matches...");
                  boolean hasPartialMatches = tree.findPartial(term2); // Call findPartial and check for matches
                  if (!hasPartialMatches) {
                     System.out.println("No partial matches found."); // Print if no partial matches are found
                  }
               }
               break;

            case 4:
               // Option 4: Search for a statement in the knowledge base by term and sentence
               scn.nextLine();  // Clear the buffer to avoid any leftover newline characters
               System.out.println("Enter the term:");
               String term3 = scn.nextLine(); // Read the term
               System.out.println("Enter the statement to search for:");
               String sentence2 = scn.nextLine(); // Read the sentence
               BinaryTreeNode<String> sentenceResult = tree.findSentence(sentence2); // Search for the sentence in the tree

               // If the sentence is found and contains the term, display the confidence score
               if (sentenceResult != null && sentenceResult.data.contains(term3)) {
                  System.out.println("The statement was found and has a confidence score of "
                          + sentenceResult.data.replaceAll("^[^0-9]*", ""));
               } else {
                  System.out.println("No matching statement found.");
               }
               break;

            case 5:
               // Option 5: Quit the program
               System.out.println("Goodbye!");
               break;

            default:
               // Handle invalid menu options
               System.out.println("Invalid option. Please try again.");
               break;
         }
      }

      scn.close();  // Close the scanner to free up resources
   }

   /**
    *
    * @param d
    */
   // Insert method - compare strings using compareTo to maintain BST property
   public void insert(dataType d) {
      if (root == null)
         root = new BinaryTreeNode<dataType>(d, null, null);  // If the tree is empty, create a new root node
      else
         insert(d, root);  // Otherwise, insert the data into the tree
   }

   /**
    *
    * @param d
    * @param node
    */
   public void insert(dataType d, BinaryTreeNode<dataType> node) {
      // Extract the term from the data
      String term = d.toString().replaceAll("[A-Z].*", "").trim();
      String nodeTerm = node.data.toString().replaceAll("[A-Z].*", "").trim();
      int comparison = term.compareTo(nodeTerm);  // Compare the terms to determine the insertion position
      if (comparison < 0) {
         if (node.left == null)
            node.left = new BinaryTreeNode<dataType>(d, null, null);  // Insert to the left if the term is smaller
         else
            insert(d, node.left);
      } else if (comparison > 0) {
         if (node.right == null)
            node.right = new BinaryTreeNode<dataType>(d, null, null);  // Insert to the right if the term is larger
         else
            insert(d, node.right);
      } else {
         // If the term already exists, update the node with the new data
         node.data = d;
      }
   }

   /**
    *
    * @param d
    * @return
    */
   // Find method - compare strings using compareTo
   public BinaryTreeNode<dataType> find(dataType d) {
      return find(d, root);  // Start the search from the root node
   }

   /**
    *
    * @param d
    * @param node
    * @return
    */
   public BinaryTreeNode<dataType> find(dataType d, BinaryTreeNode<dataType> node) {
      if (node == null)
         return null;  // If the node is null, the term is not found

      String term = d.toString().trim().toLowerCase();
      int index = node.data.toString().indexOf(node.data.toString().replaceAll("^[^A-Z]*", "").charAt(0));
      String nodeTerm = node.data.toString().substring(0, index).trim().toLowerCase();

      int comparison = d.toString().trim().toLowerCase().compareTo(nodeTerm);
      if (comparison == 0) {
         return node;  // Return the node if the term matches
      }
      BinaryTreeNode<dataType> leftChild = find(d, node.left);
      if (comparison < 0) {
         return find(d, leftChild);  // Search in the left subtree if the term is smaller
      } else {
         return find(d, node.right);  // Search in the right subtree if the term is larger
      }
   }

   /**
    *
    * @param d
    * @return
    */
   // Find partial matches
   public boolean findPartial(dataType d) {
      return findPartial(d, root); // Call the recursive method and return its result
   }

   /**
    *
    * @param d
    * @param node
    * @return
    */
   public boolean findPartial(dataType d, BinaryTreeNode<dataType> node) {
      if (node == null) {
         return false; // No matches found in this subtree
      }

      String term = d.toString().toLowerCase();
      int index = node.data.toString().indexOf(node.data.toString().replaceAll("^[^A-Z]*", "").charAt(0));
      String nodeTerm = node.data.toString().substring(0, index).trim();

      boolean foundMatch = false; // Flag to track if any partial match is found

      if (nodeTerm.matches(".*" + "\\b" + term + "\\b" + ".*")) {
         if (!term.equals(nodeTerm)) { // Exclude the exact term itself
            System.out.println("Term: " + node.data.toString().replaceAll("[A-Z].*", "") + "   Statement: "
                    + node.data.toString().replaceAll("^[^A-Z]*", "").replaceAll("\\d*", "").replaceAll("\\.*", "").trim() +
                    ".  (Confidence score: " + node.data.toString().replaceAll("^[^0-9]*", "") + ")");
            foundMatch = true; // Set flag to true if a partial match is found
         }
      }

      // Recursively search in the left and right subtrees
      boolean leftMatch = findPartial(d, node.left);
      boolean rightMatch = findPartial(d, node.right);

      // Return true if any partial match was found in the current node or its subtrees
      return foundMatch || leftMatch || rightMatch;
   }

   /**
    *
    * @param d The statement being searched for
    * @return Returns the node if the statement is found
    */
   // Find sentence method
   public BinaryTreeNode<dataType> findSentence(dataType d) {
      return findSentence(d, root);  // Start the sentence search from the root node
   }

   /**
    *
    * @param d The statement being searched for
    * @param node The current node in the BST
    * @return Returns the node if the statement is found
    */
   public BinaryTreeNode<dataType> findSentence(dataType d, BinaryTreeNode<dataType> node) {
      if (node == null)
         return null;  // If the node is null, the sentence is not found

      String sentence = d.toString().toLowerCase();
      String nodeSentence = node.data.toString().toLowerCase();

      // Check if the node's sentence contains the search sentence
      if (nodeSentence.contains(sentence)) {
         return node;  // Return the node if the sentence is found
      }

      BinaryTreeNode<dataType> leftResult = findSentence(d, node.left);
      if (leftResult != null) return leftResult;  // Search in the left subtree

      return findSentence(d, node.right);  // Search in the right subtree
   }
}