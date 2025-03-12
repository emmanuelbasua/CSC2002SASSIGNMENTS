// Hussein's Binary Search Tree
// 27 March 2017
// Hussein Suleman

import java.io.File;
import java.io.FileNotFoundException;
import java.util.Scanner;

public class BinarySearchTree<dataType extends Comparable<? super dataType>> extends BinaryTree<dataType> {

   public static void main(String[] args) throws FileNotFoundException {
      BinarySearchTree<String> tree = new BinarySearchTree<String>();
      Scanner scn = new Scanner(System.in);

      int choice = 0;  // Initialize choice variable

      while (choice != 5) {  // Continue looping until the user selects option 5
         System.out.println("Choose an action from the menu:");
         System.out.println("1. Load a knowledge base from a file");
         System.out.println("2. Add a new statement to the knowledge base");
         System.out.println("3. Search for a statement in the knowledge base by term");
         System.out.println("4. Search for a statement in the knowledge base by term and sentence");
         System.out.println("5. Quit");

         choice = scn.nextInt();  // Read user's choice

         switch (choice) {
            case 1:
               System.out.println("Enter a file name:");
               String fileName = scn.next();
               File file = new File("C:/Users/basua/OneDrive/Desktop/" + fileName);
               Scanner scan = new Scanner(file);

               while (scan.hasNextLine()) {
                  tree.insert(scan.nextLine());
               }
               scan.close();
               System.out.println("Knowledge base loaded successfully.");
               break;
            case 2:
               System.out.println("Enter the term:");
               String term = scn.nextLine();
               scn.nextLine();  // Clear the buffer
               System.out.println("Enter the statement:");
               String sentence = scn.nextLine();
               System.out.println("Enter the confidence score:");
               String confScore = scn.next();

               // Combine input into a new statement
               String newLine = term + " " + sentence + " " + confScore;
               System.out.println(newLine);

               // Find the term once and reuse it
               BinaryTreeNode<String> termNode = tree.find(term);
               if (termNode == null) {  // If term is not found, insert it
                  tree.insert(newLine);
               } else {  // If term exists, update it
                  tree.update(newLine);
               }
               break;
            case 3:
               System.out.println("Enter the term to search:");
               scn.nextLine();  // Clear any leftover newline
               String term2 = scn.nextLine();
               BinaryTreeNode<String> result = tree.find(term2);
               BinaryTreeNode<String> partial = tree.findPartial(term2);
               if (result != null) {
                  String definition = result.data;
                  System.out.println("Statement found: " + definition.replaceAll("^[^A-Z]*", "").replaceAll("\\.*", "").replaceAll("\\d*", "")
                          + ". (Confidence score: " + definition.substring(definition.indexOf(definition.replaceAll("^[^0-9]*", "")
                          .charAt(0)), definition.length()));
               } else {
                  System.out.println("No exact match found. Searching for partial matches...");
                  tree.findPartial(term2, tree.root);

               }
               break;
            case 4:
               System.out.println("Enter the term:");
               scn.nextLine();  // Clear the buffer
               String term3 = scn.nextLine();
               System.out.println("Enter the statement to search for:");
               String sentence2 = scn.nextLine();
               if (tree.find(term3) != null && tree.findSentence(sentence2) !=null) {
                  System.out.println("The statement was found and has a confidence score of "
                          + tree.findSentence(sentence2).data.toString()
                          .substring(tree.findSentence(sentence2).data.toString()
                                          .indexOf(tree.findSentence(sentence2).data.toString()
                                                  .replaceAll("^[^0-9]*", "").charAt(0)),
                                  tree.findSentence(sentence2).data.toString().length()));
                  break;
               }
               break;
            case 5:
               System.out.println("Goodbye!");
               break;
            default:
               System.out.println("Invalid option. Please try again.");
               break;
         }
      }

      scn.close();
   }

   // Insert method - compare strings using compareTo to maintain BST property
   public void insert(dataType d) {
      if (root == null)
         root = new BinaryTreeNode<dataType>(d, null, null);
      else
         insert(d, root);
   }

   public void insert(dataType d, BinaryTreeNode<dataType> node) {
      // Compare strings using compareTo
      String keyword = node.data.toString().replaceAll("[A-Z].*", "").trim();
      System.out.println(keyword);
      int comparison = d.toString().compareTo(keyword);
      if (comparison == 0) {
         return;  // Don't insert duplicates
      } else if (comparison < 0) {
         if (node.left == null)
            node.left = new BinaryTreeNode<dataType>(d, null, null);
         else
            insert(d, node.left);
      } else {
         if (node.right == null)
            node.right = new BinaryTreeNode<dataType>(d, null, null);
         else
            insert(d, node.right);
      }
   }

   // Find method - compare strings using compareTo
   public BinaryTreeNode<dataType> find(dataType d) {
      return find(d, root);
   }

   public BinaryTreeNode<dataType> find(dataType d, BinaryTreeNode<dataType> node) {
      if (node == null)
         return null;
      String keyword = node.data.toString().replaceAll("[A-Z].*", "").trim();
      System.out.println(keyword);
      int comparison = d.toString().compareTo(keyword);
      System.out.println(comparison);
      if (comparison == 0) {
         //if (node.data.toString().toLowerCase().matches(".*"+ "\\b" + d.toString().toLowerCase()+ "\\b" + ".*")) {
         return node;// Found the exact match
      } else if (comparison < 0) {
         return find(d, node.left);  // Go left if the term is smaller
      } else {
         return find(d, node.right);  // Go right if the term is larger
      }

   }

   public BinaryTreeNode<dataType> findPartial(dataType d) {
      return findPartial(d, root);
   }

   public BinaryTreeNode<dataType> findPartial(dataType d, BinaryTreeNode<dataType> node) {
      if (node == null)
         return null;
      int index = node.data.toString().indexOf(node.data.toString().replaceAll("^[^A-Z]*", "").charAt(0));
      String keyword = node.data.toString().substring(0, index).trim();
      System.out.println(keyword);
      int comparison = d.toString().compareTo(keyword);
      System.out.println(comparison);
      if (keyword.matches(".*" + "\\b" + d.toString().toLowerCase() + "\\b" + ".*")) {
         comparison = 0;
      }
      if (comparison == 0) {
         //if (node.data.toString().toLowerCase().matches(".*"+ "\\b" + d.toString().toLowerCase()+ "\\b" + ".*")) {
         return node;// Found the exact match
      } else if (comparison < 0) {
         return findPartial(d, node.left);  // Go left if the term is smaller
      } else {
         return findPartial(d, node.right);  // Go right if the term is larger
      }

   }

   // Update method - compare strings using compareTo to replace existing entry
   public BinaryTreeNode<dataType> update(dataType d) {
      return update(d, root);
   }

   public BinaryTreeNode<dataType> update(dataType d, BinaryTreeNode<dataType> node) {
      if (node == null)
         return null;

      int comparison = d.compareTo(node.data);
      if (comparison == 0) {
         node.data = d;  // Update the node if the term is found
         return node;
      } else if (comparison < 0) {
         return update(d, node.left);  // Go left
      } else {
         return update(d, node.right);  // Go right
      }
   }

   public BinaryTreeNode<dataType> findSentence(dataType d) {
      return findSentence(d, root);
   }

   public BinaryTreeNode<dataType> findSentence(dataType d, BinaryTreeNode<dataType> node) {
      if (node == null)
         return null;
      //System.out.println("Checking node: " + node.data);
      String keyword = node.data.toString().replaceAll("^[^A-Z]*", "").replaceAll("\\.*", "").replaceAll("\\d*", "").trim();
      System.out.println(keyword);

      int comparison = d.toString().compareTo(keyword);
      System.out.println(comparison);
      if (comparison == 0) {
         //if (node.data.toString().toLowerCase().matches(".*"+ "\\b" + d.toString().toLowerCase()+ "\\b" + ".*")) {
         return node;// Found the exact match
      } else if (comparison < 0) {
         return findSentence(d, node.left);  // Go left if the term is smaller
      } else {
         return findSentence(d, node.right);  // Go right if the term is larger
      }


   }
}
