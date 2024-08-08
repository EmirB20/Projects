import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.util.*;
import java.util.Queue;

public class WaiterSystem {
    private JFrame frame;
    private JPanel loginPanel, floorPanel, tableDetailPanel;
    private CardLayout cardLayout;
    private Map<Integer, JButton> tableButtons;
    private Map<Integer, String> tableStatus;
    private Map<String, char[]> waitStaffCredentials;
    private Map<Integer, Queue<String>> orderQueues; // Map from table ID to its specific order queue
    private static final String[] MENU_CATEGORIES = {"Soups/Salads", "Entrees", "Desserts", "Drinks", "Appetizers"};
    private Map<String, String[]> menuItems;

    public WaiterSystem() {
        waitStaffCredentials = new HashMap<>();
        waitStaffCredentials.put("waiter1", new char[]{'p', 'a', 's', 's'});
        tableButtons = new HashMap<>();
        tableStatus = new HashMap<>();
        orderQueues = new HashMap<>(); // Initialize map of queues
        for (int i = 1; i <= 30; i++) {
            tableStatus.put(i, "open");
            orderQueues.put(i, new LinkedList<>()); // Create a separate queue for each table
        }
        initializeMenuItems();
        createGUI();
    }

    private void initializeMenuItems() {
        menuItems = new HashMap<>();
        menuItems.put("Soups/Salads", new String[]{"Caesar Salad", "Tomato Soup", "Greek Salad", "Onion Soup"});
        menuItems.put("Entrees", new String[]{"Steak", "Salmon", "Chicken Alfredo", "Vegetarian Pizza"});
        menuItems.put("Desserts", new String[]{"Cheesecake", "Apple Pie", "Chocolate Ice Cream", "Fruit Salad"});
    menuItems.put("Drinks", new String[]{"Water", "Coke", "Beer", "Wine"});
    menuItems.put("Appetizers", new String[]{"Fries", "Spring Rolls", "Garlic Bread", "Bruschetta"});
    }

    private void createGUI() {
        frame = new JFrame("Restaurant Floor Plan");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        cardLayout = new CardLayout();
        frame.setLayout(cardLayout);
    
        setupLoginPanel();
        setupFloorPanel();
        setupTableDetailPanel();
    
        frame.pack();
        frame.setVisible(true);
    }
    
    private void setupLoginPanel() {
        loginPanel = new JPanel(new GridLayout(3, 2));
        JLabel usernameLabel = new JLabel("Username:");
        JTextField usernameField = new JTextField();
        JLabel passwordLabel = new JLabel("Password:");
        JPasswordField passwordField = new JPasswordField();
        JButton loginButton = new JButton("Login");
        loginButton.addActionListener(e -> {
            char[] enteredPassword = passwordField.getPassword();
            if (waitStaffCredentials.containsKey(usernameField.getText()) &&
                    Arrays.equals(waitStaffCredentials.get(usernameField.getText()), enteredPassword)) {
                cardLayout.show(frame.getContentPane(), "Floor Plan");
            } else {
                JOptionPane.showMessageDialog(frame, "Invalid credentials!", "Error", JOptionPane.ERROR_MESSAGE);
            }
            usernameField.setText("");
            passwordField.setText("");
        });
    
        loginPanel.add(usernameLabel);
        loginPanel.add(usernameField);
        loginPanel.add(passwordLabel);
        loginPanel.add(passwordField);
        loginPanel.add(loginButton);
    
        frame.add(loginPanel, "Login");
    }
    
    private void setupFloorPanel() {
        floorPanel = new JPanel(new GridLayout(6, 5));
        for (int i = 1; i <= 30; i++) {
            JButton tableButton = new JButton("Table " + i);
            tableButton.setBackground(getColorForStatus(tableStatus.get(i)));
            tableButton.setOpaque(true);
            tableButton.setBorderPainted(false);
            int tableId = i;
            tableButton.addActionListener(e -> showTableManagementInterface(tableId));
            floorPanel.add(tableButton);
            tableButtons.put(i, tableButton);
        }
        JButton logoutButton = new JButton("Logout");
        logoutButton.addActionListener(e -> cardLayout.show(frame.getContentPane(), "Login"));
        floorPanel.add(logoutButton);
    
        frame.add(floorPanel, "Floor Plan");
    }
    
    private void setupTableDetailPanel() {
        tableDetailPanel = new JPanel(new BorderLayout());
        frame.add(tableDetailPanel, "Table Details");
    }
    
    private void showTableManagementInterface(int tableId) {
        JPanel tableManagementPanel = new JPanel(new GridLayout(0, 1));
        JLabel infoLabel = new JLabel("Manage Table " + tableId + " - Status: " + tableStatus.get(tableId));
        tableManagementPanel.add(infoLabel);
    
        JButton changeStatusButton = new JButton("Change Status");
        changeStatusButton.addActionListener(e -> changeTableStatus(tableId));
        tableManagementPanel.add(changeStatusButton);
    
        JButton viewOrdersButton = new JButton("View/Add Orders");
        viewOrdersButton.addActionListener(e -> showOrderQueue(tableId));
        tableManagementPanel.add(viewOrdersButton);
    
        JButton backButton = new JButton("Back to Floor Plan");
        backButton.addActionListener(e -> cardLayout.show(frame.getContentPane(), "Floor Plan"));
        tableManagementPanel.add(backButton);
    
        tableDetailPanel.removeAll();
        tableDetailPanel.add(tableManagementPanel);
        tableDetailPanel.revalidate();
        tableDetailPanel.repaint();
    
        cardLayout.show(frame.getContentPane(), "Table Details");
    }
    
    private void showOrderQueue(int tableId) {
        JPanel orderPanel = new JPanel(new BorderLayout());
        JTextArea orderTextArea = new JTextArea(10, 30);
        orderTextArea.setEditable(false);
        JScrollPane scrollPane = new JScrollPane(orderTextArea);
        orderPanel.add(scrollPane, BorderLayout.CENTER);
        updateOrderTextArea(orderTextArea, tableId);
    
        JComboBox<String> menuItemComboBox = new JComboBox<>();
        for (String category : MENU_CATEGORIES) {
            menuItemComboBox.addItem("-- " + category);
            for (String item : menuItems.get(category)) {
                menuItemComboBox.addItem(item);
            }
        }
        orderPanel.add(menuItemComboBox, BorderLayout.NORTH);
    
        JButton addItemButton = new JButton("Add Item to Order");
        addItemButton.addActionListener(e -> {
            String selectedItem = (String) menuItemComboBox.getSelectedItem();
            if (selectedItem != null && !selectedItem.startsWith("--")) {
                orderQueues.get(tableId).add(selectedItem);
                updateOrderTextArea(orderTextArea, tableId);
            }
        });
        orderPanel.add(addItemButton, BorderLayout.SOUTH);
    
        JOptionPane.showMessageDialog(frame, orderPanel, "Manage Orders for Table " + tableId, JOptionPane.PLAIN_MESSAGE);
    }
    
    private void updateOrderTextArea(JTextArea orderTextArea, int tableId) {
        StringBuilder ordersText = new StringBuilder("Orders for Table " + tableId + ":\n");
        Queue<String> queue = orderQueues.get(tableId);
        for (String order : queue) {
            ordersText.append(order).append("\n");
        }
        orderTextArea.setText(ordersText.toString());
        System.out.println(ordersText.toString());
    }
    
    private void changeTableStatus(int tableId) {
        String[] statuses = {"open", "occupied", "dirty"};
        String currentStatus = tableStatus.get(tableId);
        String newStatus = (String) JOptionPane.showInputDialog(frame, "Select status for Table " + tableId,
                "Change Status", JOptionPane.QUESTION_MESSAGE, null, statuses, currentStatus);
        if (newStatus != null && !newStatus.isEmpty()) {
            tableStatus.put(tableId, newStatus);
            JButton tableButton = tableButtons.get(tableId);
            tableButton.setBackground(getColorForStatus(newStatus));
            showTableManagementInterface(tableId); // Refresh to show updated status
        }
    }
    
    private Color getColorForStatus(String status) {
        switch (status) {
            case "open": return Color.GREEN;
            case "occupied": return Color.YELLOW;
            case "dirty": return Color.RED;
            default: return Color.GRAY;
        }
    }
    
    public static void main(String[] args) {
        SwingUtilities.invokeLater(WaiterSystem::new);
    }
}







