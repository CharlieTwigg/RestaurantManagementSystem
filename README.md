# RestaurantManagementSystem

General Introduction 

	Modern restaurants need efficient tools for daily tasks. Traditional methods like manual order handling and bookkeeping are outdated and prone to costly human errors. A Restaurant Management System (RMS) addresses this by:

1. Storing restaurant and menu details for easier reservation and order management.
2. Creating and tracking orders for specific tables.
3. Generating and saving bills automatically.
	
RMS Capabilities

Restaurant Configuration:

Allows setup and modification of the restaurant's name, table/seat count, and full menu.
Users can update this information anytime via the "Configure Facility/Menu" section.
Order Management & Kitchen Workflow:

Transmits confirmed customer orders directly to the kitchen for preparation.
Manages the order process through distinct stages: Customer Confirmation -> Kitchen Notification -> Cooking Process -> Chef/Kitchen Fulfillment -> Order Ready for Customer.
Keeps the order active in the system until the customer requests the final bill.
Customer Billing & Data:

Generates customized receipts for customers upon request, branded with the restaurant's name.
Provides a graphical user interface (GUI) with dropdown menus for staff (e.g., cashiers) to easily select menu items and create orders from the database.
Stores finalized order data in the database for record-keeping and potential data analysis.

Technical Side

	Application will have Graphical User Interface using Python’s built-in module Tkinter. SQLite3 will be the database of choice; hence no active internet connection is required. Initial start will start with main window.Application doesn’t require third-party packages in order to run.


How to use application

Clone the repo to your local machine:
```
 git clone https://github.com/CharlieTwigg/RestaurantManagementSystem.git
 cd RestaurantManagementSystem
```

Run pip install to get required packages:
```
 pip install -r requirements.txt
```

Run the command below to initialize the app:
```
 python BASE/Components/rms.py
```

   
   

