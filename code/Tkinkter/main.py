import tkinter as tk
from tkinter import PhotoImage, filedialog, messagebox, ttk
import pandas as pd
from PIL import Image, ImageTk
import base64
import io
import os
import re


class ExcelSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TEST SCRIPT ASSIST")
        img = PhotoImage(file=r'C:\Users\PREETHAE\Downloads\Capgemini.png')
        root.iconphoto(False, img)
        self.selected_item = None

        # Get screen width and height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Set the window size and position
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")

        # Frame to hold widgets
        self.frame = tk.Frame(self.root, padx=10, pady=10)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Left Frame for upload button and search bar
        self.left_frame = tk.Frame(self.frame, pady=50)  # Increase the padding to move contents down
        self.left_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)

        # Load and add image to the top-left corner
        #self.image = PhotoImage(file=r'C:\Users\PREETHAE\Downloads\Capgemini-Logo.png')
        #self.image_label = tk.Label(self.left_frame, image=self.image)
        #self.image_label.grid(row=0, column=0, columnspan=7, rowspan=1, padx=1, pady=30, sticky="n")

        # Upload Excel file button
        self.upload_button = tk.Button(self.left_frame, text="Upload Test Case \nExcel File", command=self.upload_excel)
        self.upload_button.grid(row=0, column=0, columnspan=3, pady=10, sticky="w")

        # Add the new button for uploading a folder of text files
        self.upload_folder_button = tk.Button(self.left_frame, text="Upload Reusable \nScript file",
                                              command=self.upload_text_folder)
        self.upload_folder_button.grid(row=0, column=0, columnspan=3, pady=10, sticky="e")

        # Search Label
        self.search_label = tk.Label(self.left_frame, text="Enter REQ ID OR USECASE ID:")
        self.search_label.grid(row=2, column=0, sticky="w")

        # Search Entry
        self.search_entry = tk.Entry(self.left_frame, width=30)
        self.search_entry.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        # Search Button
        self.search_button = tk.Button(self.left_frame, text="Search", command=self.search_excel)
        self.search_button.grid(row=3, column=2, padx=2, pady=2, sticky="w")

        # Generate Button
        self.generate_button = tk.Button(self.left_frame, text="Generate", command=self.generate_scripts)
        self.generate_button.grid(row=1, column=0, columnspan=3, pady=20)  # Center the button with increased padding

        # Bind Enter key to search entry
        self.search_entry.bind("<Return>", self.search_excel)

        # Treeview widget for first display box (right side)
        self.tree_frame1 = tk.Frame(self.frame)
        self.tree_frame1.pack(side=tk.RIGHT, padx=10, pady=(15, 10), fill=tk.BOTH, expand=True)

        self.tree1 = ttk.Treeview(self.tree_frame1, columns=("Requirement ID", "Use Case ID"), show="headings")
        self.tree1.heading("Requirement ID", text="Requirement ID")
        self.tree1.heading("Use Case ID", text="Use Case ID")
        self.tree1.column("Requirement ID", anchor=tk.W, stretch=tk.YES)
        self.tree1.column("Use Case ID", anchor=tk.W, stretch=tk.YES)
        self.tree1.pack(fill=tk.BOTH, expand=True)

        # Bind double-click event
        self.tree1.bind("<Double-1>", self.on_double_click)

        # Frame for the Generated Scripts section
        self.generated_scripts_frame = tk.Frame(self.root)
        self.generated_scripts_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Label and Text Widget for Generated Scripts
        self.results_label3 = tk.Label(self.generated_scripts_frame, text="EXCEL DATA")
        self.results_label3.pack(side=tk.TOP, padx=10, pady=5, anchor=tk.NW)

        self.results_text3 = tk.Text(self.generated_scripts_frame, height=50, width=20)  # Increased height
        self.results_text3.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.results_text3.config(state=tk.DISABLED)  # Make text widget read_only

        # Frame for the two display boxes
        self.results_frame = tk.Frame(self.root)
        self.results_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Label and Text Widget for Excel Data Display
        self.results_label2 = tk.Label(self.results_frame, text="GENERATED SCRIPTS")
        self.results_label2.pack(side=tk.TOP, padx=10, pady=5, anchor=tk.NW)

        self.results_text2 = tk.Text(self.results_frame, height=50, width=50, undo=True)  # Increased height
        self.results_text2.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.results_text2.config(state=tk.NORMAL)  # Make text widget editable

        # Frame for the Save button
        self.button_frame = tk.Frame(self.results_frame)
        self.button_frame.pack(side=tk.RIGHT, padx=15, pady=110, fill=tk.Y)

        # Bind Undo/Redo commands
        self.results_text2.bind("<Control-z>", self.undo_edit)
        self.results_text2.bind("<Control-y>", self.redo_edit)

        # Save Button
        self.save_button = tk.Button(self.button_frame, text="Save", command=self.save_generated_script)
        self.save_button.pack()

        # Initialize variables
        self.filepath = None
        self.use_case_data = []  # List to store Use case sheet data
        self.text_files_data = {}

    def upload_excel(self):
        # Open a file dialog to select an Excel file
        self.filepath = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])

        # Check if a file was selected
        if self.filepath:
            # Show a message box with the path of the uploaded file
            messagebox.showinfo("File Uploaded", f"Uploaded: {self.filepath}")

            # Call a method to load use case data from the selected file
            self.load_use_case_data()

    def upload_text_folder(self):
        # Open a directory dialog to select a folder
        folder_path = filedialog.askdirectory()

        # Check if a folder was selected
        if folder_path:
            # Initialize an empty dictionary to store text file data
            self.text_files_data = {}

            # Iterate over each file in the selected folder
            for filename in os.listdir(folder_path):
                # Process only text files with a .txt extension
                if filename.endswith(".txt"):
                    # Construct the full file path
                    file_path = os.path.join(folder_path, filename)

                    # Open and read the content of the text file
                    with open(file_path, "r") as file:
                        file_content = file.read()

                        # Extract function data from the file content and update the dictionary
                        self.text_files_data.update(self.extract_functions_from_file(file_content))

            # Show a message box indicating the folder with text files has been uploaded
            messagebox.showinfo("Folder Uploaded", f"Uploaded text files from: {folder_path}")

    def extract_functions_from_file(self, text):
        # Define a regular expression pattern to match function_blocks
        # Function blocks start with a $ followed by the function name,
        # followed by () and {, then the function content, and ends with }
        pattern = r'\$(\w+)\s*\(\)\s*\{\s*([\s\S]*?)\s*\}'

        # Use re.findall to find all matches of the pattern in the provided text
        matches = re.findall(pattern, text)

        # Initialize an empty dictionary to store extracted functions
        functions_dict = {}

        # Iterate over each match found by the regular expression
        for match in matches:
            # Extract the function name and content from the match
            function_name = match[0]
            content = match[1].strip().split('\n')

            # Remove leading and trailing whitespace from each line and filter out empty lines
            temp = [line.strip() for line in content if line.strip()]

            # Add the function to the dictionary with its name as the key and its content as the value
            functions_dict[f"${function_name} ()"] = self.remove_comments(temp)

        # Return the dictionary containing all extracted functions and their content
        return functions_dict

    def remove_comments(self, strings):
        # Filter out lines that start with '//' (comments) from the list of strings
        return [s for s in strings if not s.startswith('//')]

    def load_use_case_data(self):
        try:
            # Load the specific sheet "Usecase" from the Excel file into a DataFrame
            xl = pd.ExcelFile(self.filepath)
            if 'Usecase' not in xl.sheet_names:
                messagebox.showerror("Error", "No 'Usecase' sheet found in the Excel file.")
                return

            # Load only the required columns starting from B14
            df = xl.parse('Usecase', header=None, skiprows=15, usecols="B:G")

            # Rename columns based on their positions
            df.columns = ["Requirement ID", "Use Case ID", "Placeholder", "Scenarios", "Preconditions", "TestCases"]

            # Replace NaN values with "-"
            df.fillna("-", inplace=True)

            # Store data in a list of dictionaries
            self.use_case_data = [
                {"Requirement ID": row["Requirement ID"], "Use Case ID": row["Use Case ID"],
                 "Scenarios": row["Scenarios"], "Preconditions": row["Preconditions"], "TestCases": row["TestCases"]}
                for index, row in df.iterrows()
            ]

            # Display all results in the Treeview
            self.display_results(self.use_case_data)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while loading 'Usecase' sheet: {str(e)}")

    def search_excel(self, event=None):
        if not self.filepath:
            messagebox.showerror("Error", "Please upload an Excel file first.")
            return

        search_term = self.search_entry.get()

        try:
            if not self.use_case_data:
                messagebox.showerror("Error", "No 'Usecase' data loaded. Please upload an Excel file.")
                return

            # Filter data based on search term in 'Requirement ID' or 'Use Case ID'
            filtered_cases = [
                item for item in self.use_case_data
                if search_term.lower() in str(item["Requirement ID"]).lower() or search_term.lower() in str(
                    item["Use Case ID"]).lower()
            ]

            # Display results in treeview
            self.display_results(filtered_cases)

            # Automatically show the details in the second display box if only one result is found
            if len(filtered_cases) == 1:
                self.show_details(filtered_cases[0])
            elif len(filtered_cases) > 1:
                self.results_text2.config(state=tk.NORMAL)  # Set state to normal to edit content
                self.results_text2.delete(1.0, tk.END)  # Clear previous results
                self.results_text2.insert(tk.END, "Multiple results found. Double-click a row to view details.")
                self.results_text2.config(state=tk.NORMAL)  # Set state back to editable
            else:
                self.results_text2.config(state=tk.NORMAL)  # Set state to normal to edit content
                self.results_text2.delete(1.0, tk.END)  # Clear previous results
                self.results_text2.insert(tk.END, "No matching rows found.")
                self.results_text2.config(state=tk.NORMAL)  # Set state back to editable

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def display_results(self, results):
        # Clear the previous treeview content
        for item in self.tree1.get_children():
            self.tree1.delete(item)

        if not results:
            self.tree1.insert("", "end", values=("No matching rows found.", ""))
        else:
            for item in results:
                self.tree1.insert("", "end", values=(item["Requirement ID"], item["Use Case ID"]))

        self.results_text2.config(state=tk.NORMAL)  # Set state to normal to edit content
        self.results_text2.delete(1.0, tk.END)  # Clear previous results

        if not results:
            self.results_text2.insert(tk.END, "No matching rows found.")
        else:
            # Insert placeholder data for second display box
            self.results_text2.insert(tk.END, "Placeholder text for additional information.\n")

        self.results_text2.config(state=tk.NORMAL)  # Set state back to disabled

        # Clear generated scripts box
        self.results_text3.config(state=tk.NORMAL)  # Set state to normal to edit content
        self.results_text3.delete(1.0, tk.END)  # Clear previous results
        self.results_text3.insert(tk.END, "Generated Scripts\n\n")  # Initial display message
        self.results_text3.config(state=tk.DISABLED)  # Set state back to read_only

    def on_double_click(self, event):
        # Get selected item
        item = self.tree1.selection()[0]
        selected_data = self.tree1.item(item, "values")
        # Find the corresponding "Scenarios", "Preconditions", and "TestCases" values for the selected "Use Case ID"
        use_case_id = selected_data[1]
        use_case_data = next((item for item in self.use_case_data if item["Use Case ID"] == use_case_id), None)
        self.selected_item = use_case_data

        if use_case_data:
            self.show_details(use_case_data)

    def show_details(self, use_case_data):
        # Extract the details
        use_case_id = use_case_data["Use Case ID"]
        scenario = use_case_data["Scenarios"]
        preconditions = use_case_data["Preconditions"]
        test_cases = use_case_data["TestCases"]

        # Format the test case as requested
        formatted_scenario = f"// {use_case_id}\n// {scenario}\n"

        # Function to process the conditions
        def process_conditions(conditions):
            output_start = False
            lines = conditions.split("\n")
            modified_lines = []

            for line in lines:
                if not output_start:
                    modified_lines.append(line)
                    if line.strip() == "Output:":
                        output_start = True
                else:
                    if "=" in line and "delay" not in line:
                        key, value = line.split("=")
                        key = key.strip()
                        value = value.strip()
                        modified_line = f"CHECK {key} = {value}, ERROR: {key} SHOULD BE {value}"
                        modified_lines.append(modified_line)
                    else:
                        modified_lines.append(line)

            return "\n".join(modified_lines)

        # Process preconditions and test cases
        formatted_preconditions = process_conditions(preconditions)
        formatted_test_cases = process_conditions(test_cases)

        # Combine formatted scenario, preconditions, and test cases
        combined_output = f"{formatted_scenario}\n// {formatted_preconditions}\n// {formatted_test_cases}"

        # Display the combined output in the second display box (results_text2)
        self.results_text2.config(state=tk.NORMAL)  # Set state to normal to edit content
        self.results_text2.delete(1.0, tk.END)  # Clear previous results
        self.results_text2.insert(tk.END, combined_output)
        self.results_text2.config(state=tk.NORMAL)  # Set state back to editable

        # Display actual values in the third display box (results_text3)
        self.results_text3.config(state=tk.NORMAL)  # Set state to normal to edit content
        self.results_text3.delete(1.0, tk.END)  # Clear previous results
        self.results_text3.insert(tk.END, f"//Use Case ID: {use_case_id}\n")
        self.results_text3.insert(tk.END, f"//Scenarios: {scenario}\n")
        self.results_text3.insert(tk.END, f"//Preconditions: {preconditions}\n")
        self.results_text3.insert(tk.END, f"//Test Cases: {test_cases}\n")
        self.results_text3.config(state=tk.DISABLED)  # Set state back to read_only

        # Disable editing for Requirement ID and Use Case ID in results_text2
        self.results_text2.tag_configure("readonly", foreground="black")
        self.results_text2.insert(tk.END, f"\n\nRequirement ID: {use_case_data['Requirement ID']}\n", "readonly")
        self.results_text2.insert(tk.END, f"Use Case ID: {use_case_id}\n", "readonly")

    def process_conditions(self, conditions):
        # Flag to indicate if the output section has started
        output_start = False

        # Split the conditions into individual lines
        lines = conditions.split("\n")

        # Initialize a list to hold the modified lines
        modified_lines = []

        # Iterate over each line in the conditions
        for line in lines:
            # If the output section has not started
            if not output_start:
                # Add the line to the modified lines list
                modified_lines.append(line)
                # Check if the line indicates the start of the output section
                if line.strip() == "Output:":
                    output_start = True
            else:
                # If the line contains an '=' but does not contain 'delay'
                if "=" in line and "delay" not in line:
                    # Split the line into key and value parts
                    key, value = line.split("=")
                    # Strip any extra whitespace from key and value
                    key = key.strip()
                    value = value.strip()
                    # Format the line as a CHECK statement with error message
                    modified_line = f"CHECK {key} = {value}, ERROR: {key} SHOULD BE {value}"
                    # Add the modified line to the list
                    modified_lines.append(modified_line)
                else:
                    # If the line does not meet the above criteria, add it as is
                    modified_lines.append(line)

        # Join the modified lines into a single string and return it
        return "\n".join(modified_lines)

    def extract_blocks(self, input_txt):
        # Initialize an empty dictionary to store function blocks
        blocks = {}

        # Split the input text into lines and remove any leading/trailing whitespace
        lines = input_txt.strip().split('\n')

        # Initialize variables to keep track of the current function and its block of code
        current_function = None
        current_block = []

        # Iterate over each line in the input text
        for line in lines:
            # Remove any leading/trailing whitespace from the line
            line = line.strip()

            # Check if the line marks the start of a new function block
            if line.startswith('$') and line.endswith('() {'):
                # Save the previous function block if there is one
                if current_function:
                    blocks[current_function] = '\n'.join(current_block).strip()
                # Extract the function name from the line and initialize a new block
                current_function = line.split(' ')[0]
                current_block = []
            # Check if the line marks the end of a function block
            elif line == '}':
                # Save the current function block and reset the function tracker
                if current_function:
                    blocks[current_function] = '\n'.join(current_block).strip()
                    current_function = None
            # If within a function block, add the line to the current block
            elif current_function:
                current_block.append(line)

        # Return the dictionary containing all extracted function blocks
        return blocks

    def generate_scripts(self):
        # Check if an Excel file has been uploaded
        if not self.filepath:
            messagebox.showerror("Error", "Please upload an Excel file first.")
            return

        # Check if use case data has been loaded from the Excel file
        if not self.use_case_data:
            messagebox.showerror("Error", "No 'Usecase' data loaded. Please upload an Excel file.")
            return

        try:
            # Retrieve the selected item's details
            use_case_id = self.selected_item["Use Case ID"]
            scenario = self.selected_item["Scenarios"]
            preconditions = self.selected_item["Preconditions"]
            test_cases = self.selected_item["TestCases"]
            final_output = ""

            # Format the scenario and preconditions & test cases for output
            formatted_scenario = f"// {use_case_id}\n// {scenario}\n"
            formatted_preconditions = self.process_conditions(preconditions)
            formatted_test_cases = self.process_conditions(test_cases)

            # Normalize input by joining lines with semicolons
            normalized_input = ';'.join(formatted_preconditions.split("\n"))
            normalized_test_case_input = ';'.join(formatted_test_cases.split("\n"))

            print("inside 1st loop")
            # Iterate over the function data from text files
            for function_name, content_lines in self.text_files_data.items():
                # Convert content lines to a semicolon-separated string
                content_str = ';'.join(content_lines)
                print(function_name, "Function Name", content_lines, "Content Str")

                # Skip processing if the content string is empty
                if content_str == "":
                    print("Skipping", function_name)
                    continue

                # Replace occurrences of content_str in normalized_input with the function_name
                if content_str in normalized_input:
                    print(content_str)
                    normalized_input = re.sub(re.escape(content_str), function_name, normalized_input)

                # Replace occurrences of content_str in normalized_test_case_input with the function_name
                if content_str in normalized_test_case_input:
                    print(content_str)
                    normalized_test_case_input = re.sub(re.escape(content_str), function_name,
                                                        normalized_test_case_input)

            print("After for loop")

            # Reformat the normalized inputs by joining with new lines
            normalized_input = '\n'.join(normalized_input.split(";"))
            normalized_test_case_input = '\n'.join(normalized_test_case_input.split(";"))

            # Concatenate formatted sections to create the final output
            final_output = "".join([formatted_scenario, normalized_input, normalized_test_case_input])

            # Prompt the user to save the generated scripts to a file
            save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
            if save_path:
                # Write the final output to the specified file
                with open(save_path, "w") as file:
                    file.write(final_output)
                messagebox.showinfo("Success", f"Scripts generated and saved to: {save_path}")

            # Update the results text widget with the generated scripts
            self.results_text2.config(state=tk.NORMAL)
            self.results_text2.delete(1.0, tk.END)
            self.results_text2.insert(tk.END, final_output)
            self.results_text2.config(state=tk.DISABLED)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while generating scripts: {str(e)}")

    def save_generated_script(self):
        if not self.use_case_data:
            messagebox.showerror("Error", "No use case data to save.")
            return

        # Get the updated content from the text widget
        updated_content = self.results_text2.get(1.0, tk.END).strip()

        # Extract the use case ID from the updated content
        use_case_id_start = updated_content.find("Use Case ID: ")
        if use_case_id_start == -1:
            messagebox.showerror("Error", "Could not find Use Case ID in the text.")
            return

        use_case_id_start += len("Use Case ID: ")
        use_case_id_end = updated_content.find("\n", use_case_id_start)
        if use_case_id_end == -1:
            use_case_id_end = len(updated_content)
        use_case_id = updated_content[use_case_id_start:use_case_id_end].strip()

        # Find the corresponding item in self.use_case_data
        for item in self.use_case_data:
            if item["Use Case ID"] == use_case_id:
                # Update the item with the new values
                item["Scenarios"] = updated_content  # Extract and parse specific fields as needed
                item["Preconditions"] = updated_content
                item["TestCases"] = updated_content
                break
        else:
            messagebox.showerror("Error", "Use Case ID not found in the data.")
            return

        # Print updated self.use_case_data only once
        if not hasattr(self, 'updated'):
            print("Updated self.use_case_data:", self.use_case_data)
            self.updated = True

    def undo_edit(self, event=None):
        self.results_text2.edit_undo()

    def redo_edit(self, event=None):
        self.results_text2.edit_redo()

# Create the main window
if __name__ == "__main__":
    root = tk.Tk()
    app = ExcelSearchApp(root)
    root.mainloop()
