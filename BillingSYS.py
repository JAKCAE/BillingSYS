import sqlite3
import tkinter as tk
from tkinter import messagebox
import datetime
from difflib import get_close_matches  # Import get_close_matches function
import os
import sys
#import In_out  

application_path=os.path.dirname(sys.executable)#get the exe path and in the next step to make sure our csv save in there 

# Create a connection to the database
conn = sqlite3.connect('store.db')
c = conn.cursor()

# Create tables if they don't exist
c.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                password TEXT NOT NULL
             )''')

c.execute('''CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL NOT NULL
             )''')

# Insert sample user data
#c.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('1', '2'))
# Commit changes and close connection

conn.commit()
conn.close()


class CashierSystem:
    def __init__(self, master):
        self.master = master
        self.master.title("Cashier System")
        self.username=''
        # Colors
        self.primary_color = "#3498db"
        self.secondary_color = "#2ecc71"
        self.text_color = "black"

        # Login variables
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.show_password_var = tk.BooleanVar(value=False)

        # Product variables
        self.product_name_var = tk.StringVar()
        self.product_price_var = tk.DoubleVar()

        # Cart variables
        self.cart_items = []

        # Create login frame
        self.login_frame = tk.Frame(self.master, bg=self.primary_color, relief=tk.RAISED, borderwidth=2)
        self.login_frame.pack(pady=10, padx=10)

        self.username_label = tk.Label(self.login_frame, text="Username:", bg=self.primary_color, fg=self.text_color, font=("Arial", 14))
        self.username_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.username_entry = tk.Entry(self.login_frame, textvariable=self.username_var, relief=tk.SUNKEN, borderwidth=2, font=("Arial", 14))
        self.username_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        self.password_label = tk.Label(self.login_frame, text="Password:", bg=self.primary_color, fg=self.text_color, font=("Arial", 14))
        self.password_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.password_entry = tk.Entry(self.login_frame, textvariable=self.password_var, show="*", relief=tk.SUNKEN, borderwidth=2, font=("Arial", 14))
        self.password_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        # Show Password checkbutton
        self.show_password_checkbox = tk.Checkbutton(self.login_frame, text="Show Password", variable=self.show_password_var, onvalue=True, offvalue=False, command=self.toggle_password_visibility, font=("Arial", 14))
        self.show_password_checkbox.grid(row=1, column=2, padx=(0, 10), pady=10, sticky="e")

        self.login_button = tk.Button(self.login_frame, text="Login", command=self.validate_login, bg=self.secondary_color, fg=self.text_color, relief=tk.RAISED, borderwidth=2, font=("Arial", 14))
        self.login_button.grid(row=2, column=0, columnspan=3, padx=10, pady=20)

        # Bind Enter key to login validation
        self.password_entry.bind('<Return>', lambda event: self.validate_login())
        
    #view password
    def toggle_password_visibility(self):
        """Toggle visibility of password entry"""
        if self.show_password_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")
            
    #login
    def validate_login(self):
        username = self.username_var.get()
        password = self.password_var.get()

        conn = sqlite3.connect('store.db')
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = c.fetchone()

        conn.close()

        if user:
            messagebox.showinfo("Login Successful", "Welcome back, " + username + "!")
            self.username = username
            self.login_frame.destroy()
            self.create_main_frame()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def create_main_frame(self):
        self.main_frame = tk.Frame(self.master, bg=self.primary_color, relief=tk.RAISED, borderwidth=2)
        self.main_frame.pack(padx=20, pady=10,side=tk.LEFT)

        self.products_frame = tk.Frame(self.master, bg=self.primary_color, relief=tk.RAISED, borderwidth=2)
        self.products_frame.pack(padx=20,pady=10,side=tk.RIGHT)
        
        self.product_name_label = tk.Label(self.main_frame, text="Product Name:", bg=self.primary_color, fg=self.text_color)
        self.product_name_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.product_name_entry = tk.Entry(self.main_frame, textvariable=self.product_name_var, relief=tk.SUNKEN, borderwidth=2)
        self.product_name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        #bind the product name entry suggestion 
        self.product_name_entry.bind("<KeyRelease>", self.suggest_products)

        self.product_price_label = tk.Label(self.main_frame, text="Product Price:", bg=self.primary_color, fg=self.text_color)
        self.product_price_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.product_price_entry = tk.Entry(self.main_frame, textvariable=self.product_price_var, relief=tk.SUNKEN, borderwidth=2)
        self.product_price_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        self.product_name_entry.bind("<Return>",func=self.add_product)

        self.add_product_button = tk.Button(self.main_frame, text="Add Product", command=self.add_product, bg=self.secondary_color, fg=self.text_color, relief=tk.RAISED, borderwidth=2)
        self.add_product_button.grid(row=2, column=0, columnspan=2, padx=10, pady=5)


        self.checkout_button = tk.Button(self.main_frame, text="Checkout", command=self.checkout, bg=self.secondary_color, fg=self.text_color, relief=tk.RAISED, borderwidth=2)
        self.checkout_button.grid(row=5, column=0, columnspan=2, padx=10, pady=5)
        
        # Button to delete product from cart
        # frame to delete product from cart
        #label for cart 
        self.cart_label = tk.Label(self.products_frame, text="Cart:", bg=self.primary_color, fg=self.text_color)
        self.cart_label.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        
    def validate_price(self,price):
        if price<=0:
          messagebox.showerror("Please enter a price")
          #raise ValueError("Please enter a price")
        elif price==0:
          messagebox.showerror("Please enter a price  NOT 0")

    
    def get_product_suggestions(self, partial_name):
        conn = sqlite3.connect('store.db')
        c = conn.cursor()

        c.execute("SELECT name FROM products WHERE name LIKE ?", (f"%{partial_name}%",))
        suggestions = [row[0] for row in c.fetchall()]
        conn.close()

        return suggestions

    def suggest_products(self, event):
        
        conn = sqlite3.connect('store.db')
        c = conn.cursor()
        
        partial_name = self.product_name_var.get()
        suggestions = self.get_product_suggestions(partial_name)
        matches = get_close_matches(partial_name, suggestions, n=5, cutoff=0.2)

        if matches:
            suggestion_popup = tk.Toplevel(self.master)
            suggestion_popup.title("Product Suggestions")

            suggestion_listbox = tk.Listbox(suggestion_popup, bg=self.primary_color, fg=self.text_color, selectbackground=self.secondary_color)
            suggestion_listbox.pack(expand=True, fill=tk.BOTH)

            for match in matches:
                suggestion_listbox.insert(tk.END, match)

            def on_suggestion_select(event):
                index = suggestion_listbox.curselection()
                if index:
                    selected_suggestion = suggestion_listbox.get(index)
                    
                    # Update product name entry with the selected suggestion
                    self.product_name_var.set(selected_suggestion)
                    c.execute("SELECT price FROM products WHERE name=?",(selected_suggestion,))
                    price=c.fetchone()
                    self.product_price_var.set(price[0])
                    
                    conn.close()
                    # Destroy the suggestion popup
                    suggestion_popup.destroy()

            suggestion_listbox.bind("<<ListboxSelect>>", on_suggestion_select)
        
    
    def add_product(self):
        product_name = self.product_name_var.get()
        product_price = self.product_price_var.get()
        self.validate_price(product_price)

        if product_name and product_price:
            self.cart_items.append((product_name, product_price))
            self.update_display()
            messagebox.showinfo("Product Added", "Product has been added to the cart.")
        else:
            messagebox.showerror("Missing Information", "Please enter both product name and price.")
            
    def update_display(self):
        # Clear only product labels and delete buttons
        widgets_to_remove = []
        for widget in self.products_frame.winfo_children():
            if isinstance(widget, tk.Label) and widget.winfo_parent() == self.products_frame:
                text_content = widget.cget("text")
                if text_content!= "cart":
                    widgets_to_remove.append(widget)
            elif isinstance(widget, tk.Button) and widget.winfo_parent() == self.products_frame:
                    widgets_to_remove.append(widget)

        for widget in widgets_to_remove:
            widget.destroy()

        print("after destruction",self.cart_items)
        # Display each product in the cart_items list
        for index, item in enumerate(self.cart_items):
            # Product name label
            product_label = tk.Label(self.products_frame, text=f"Product {index + 1}: {item[0]} - ${item[1]:.2f}", bg=self.primary_color, fg=self.text_color)
            product_label.grid(row=index+1, column=0, padx=10, pady=5, sticky="w")

            # Delete button for the product
            delete_button = tk.Button(self.products_frame, text="Delete", bg=self.secondary_color, fg=self.text_color, relief=tk.RAISED, borderwidth=2,
                                    command=lambda idx=index: self.delete_product(idx))
            print("Product deleted after the button was clicked",self.cart_items)
            delete_button.grid(row=index+1, column=1, padx=5, pady=5, sticky="w")


    def delete_product(self, index):
        if 0 <= index <len(self.cart_items):
            del self.cart_items[index]
            print("after delete a product",self.cart_items)
            self.update_display()
        else:
            messagebox.showerror("Invalid Index", "The index to delete is out of range.")
          
    def checkout(self):
          if self.cart_items:                  
              self.show_receipt_preferences()
              messagebox.showinfo("Checkout Successful","please choose your recipt")
          else:
              messagebox.showerror("Empty Cart", "Cart is empty. Please add some items before checkout.")
              
    '''def append_bills(self,key):
     try:
        for item in self.cart_items:
            product=In_out.get_product_info(item[0])
            In_out.add_income(item[0],1,item[1],product[2],key)
     except Exception as e:
         print(e)'''
            
    def show_receipt_preferences(self):
          receipt_frame = tk.Frame(self.master, bg=self.primary_color, relief=tk.RAISED, borderwidth=2)
          receipt_frame.pack(pady=50, padx=100)

          tk.Label(receipt_frame, text="Choose receipt preference:", bg=self.primary_color, fg=self.text_color, font=("Arial", 16)).pack(pady=10)

          tk.Button(receipt_frame, text="No Receipt", command=self.thank_you, bg=self.secondary_color, fg=self.text_color, relief=tk.RAISED, borderwidth=2, font=("Arial", 14)).pack(pady=10)
          tk.Button(receipt_frame, text="Email Receipt", command=self.email_receipt, bg=self.secondary_color, fg=self.text_color, relief=tk.RAISED, borderwidth=2, font=("Arial", 14)).pack(pady=10)
          tk.Button(receipt_frame, text="Print Receipt", command=self.print_receipt, bg=self.secondary_color, fg=self.text_color, relief=tk.RAISED, borderwidth=2, font=("Arial", 14)).pack(pady=10)
          
          if receipt_frame:
            self.master.after(7500, receipt_frame.destroy)

    def email_receipt(self):
        messagebox.showinfo("Receipt sent successfully")
        #print("cart",self.cart_items)
        self.thank_you()
        
    def thank_you(self):
        messagebox.showinfo("Thank You for choosing us","Our principal is creating milktea in otder to achive the goal of making everyone fell happy.")
        self.empty_cart()
        date_today=datetime.datetime.now().strftime("%H:%M:%d_%m_%Y")
        self.append_bills(f"K_{date_today}_y")
        
    def print_receipt(self):
        date_today=datetime.datetime.now().strftime("%H:%M:%d_%m_%Y")
        file_name = f'receipt_in_{date_today}_by_{self.username}.txt'
        with open(f'{file_name}', 'w') as receipt_file:
            receipt_file.write("Receipt\n\n")
            subtotal = sum(item[1] for item in self.cart_items)
            tax_rate = 0.13
            taxes = subtotal * tax_rate
            total = subtotal + taxes
            receipt_file.write("LMilkTea".center(10,"*"))
            receipt_file.write("Receipt\n\n")
            receipt_file.write(f"{date_today}\n")
            for item in self.cart_items:
                receipt_file.write(f"{item[0]}: ${item[1]:.2f}\n")
            receipt_file.write("\nSubtotal: ${:.2f}\n".format(subtotal))
            receipt_file.write("Tax ({}%): ${:.2f}\n".format(tax_rate * 100, taxes))
            receipt_file.write
            receipt_file.write("Total: ${:.2f}\n".format(total))
        messagebox.showinfo("Receipt Generated", "Receipt has been generated successfully.")
        self.thank_you()
        
    def empty_cart(self):
        self.cart_items = []
        self.update_display()
        
def main():
    root = tk.Tk()
    app = CashierSystem(root)
    root.mainloop()


if __name__ == "__main__":
    main()
