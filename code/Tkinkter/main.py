import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import os
import re


class ExcelSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TEST SCRIPT ASSIST")

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

        # Upload Excel file button
        self.upload_button = tk.Button(self.left_frame, text="Upload Excel File", command=self.upload_excel)
        self.upload_button.grid(row=0, column=0, columnspan=3, pady=10, sticky="w")

        # Add the new button for uploading a folder of text files
        self.upload_folder_button = tk.Button(self.left_frame, text="Upload Text Folder",command=self.upload_text_folder)
        self.upload_folder_button.grid(row=4, column=0, columnspan=3, pady=10, sticky="w")

        # Search Label
        self.search_label = tk.Label(self.left_frame, text="Enter REQ ID OR USECASE ID:")
        self.search_label.grid(row=1, column=0, sticky="w")

        # Search Entry
        self.search_entry = tk.Entry(self.left_frame, width=30)
        self.search_entry.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        # Search Button
        self.search_button = tk.Button(self.left_frame, text="Search", command=self.search_excel)
        self.search_button.grid(row=2, column=2, padx=5, pady=5, sticky="w")

        # Generate Button
        self.generate_button = tk.Button(self.left_frame, text="Generate", command=self.generate_scripts)
        self.generate_button.grid(row=3, column=0, columnspan=3, pady=20)  # Center the button with increased padding

        # Bind Enter key to search entry
        self.search_entry.bind("<Return>", self.search_excel)

        # Treeview widget for first display box (right side)
        self.tree_frame1 = tk.Frame(self.frame)
        self.tree_frame1.pack(side=tk.RIGHT, padx=10, pady=(50, 10), fill=tk.BOTH, expand=True)

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
        self.results_text3.config(state=tk.DISABLED)  # Make text widget read-only

        # Frame for the two display boxes
        self.results_frame = tk.Frame(self.root)
        self.results_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Label and Text Widget for Excel Data Display
        self.results_label2 = tk.Label(self.results_frame, text="GENERATED SCRIPTS")
        self.results_label2.pack(side=tk.TOP, padx=10, pady=5, anchor=tk.NW)

        self.results_text2 = tk.Text(self.results_frame, height=50, width=50)  # Increased height
        self.results_text2.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.results_text2.config(state=tk.DISABLED)  # Make text widget read-only


        # Initialize variables
        self.filepath = None
        self.use_case_data = []  # List to store Usecase sheet data
        self.text_files_data = {}

    def upload_excel(self):
        self.filepath = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
        if self.filepath:
            messagebox.showinfo("File Uploaded", f"Uploaded: {self.filepath}")
            self.load_use_case_data()

    def upload_text_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.text_files_data = {}
            for filename in os.listdir(folder_path):
                if filename.endswith(".txt"):
                    file_path = os.path.join(folder_path, filename)
                    with open(file_path, "r") as file:
                        file_content = file.read()
                        self.text_files_data.update(self.extract_functions_from_file(file_content))
            messagebox.showinfo("Folder Uploaded", f"Uploaded text files from: {folder_path}")

    def extract_functions_from_file(self,text):
        
        pattern = r'\$(\w+)\s*\(\)\s*\{\s*([\s\S]*?)\s*\}'
        matches = re.findall(pattern, text)
        
        functions_dict = {}
        for match in matches:
            function_name = match[0]
            content = match[1].strip().split('\n')
            temp = [line.strip() for line in content if line.strip()]
            functions_dict[f"${function_name} ()"] = self.remove_comments(temp)
        
        return functions_dict
    
    def remove_comments(self,strings):
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
                self.results_text2.config(state=tk.DISABLED)  # Set state back to disabled
            else:
                self.results_text2.config(state=tk.NORMAL)  # Set state to normal to edit content
                self.results_text2.delete(1.0, tk.END)  # Clear previous results
                self.results_text2.insert(tk.END, "No matching rows found.")
                self.results_text2.config(state=tk.DISABLED)  # Set state back to disabled

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

        self.results_text2.config(state=tk.DISABLED)  # Set state back to disabled

        # Clear generated scripts box
        self.results_text3.config(state=tk.NORMAL)  # Set state to normal to edit content
        self.results_text3.delete(1.0, tk.END)  # Clear previous results
        self.results_text3.insert(tk.END, "Generated Scripts\n\n")  # Initial display message
        self.results_text3.config(state=tk.DISABLED)  # Set state back to disabled

    def on_double_click(self, event):
        # Get selected item
        item = self.tree1.selection()[0]
        selected_data = self.tree1.item(item, "values")

        # Find the corresponding "Scenarios", "Preconditions", and "TestCases" values for the selected "Use Case ID"
        use_case_id = selected_data[1]
        use_case_data = next((item for item in self.use_case_data if item["Use Case ID"] == use_case_id), None)

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
        self.results_text2.config(state=tk.DISABLED)  # Set state back to disabled

        # Display actual values in the third display box (results_text3)
        self.results_text3.config(state=tk.NORMAL)  # Set state to normal to edit content
        self.results_text3.delete(1.0, tk.END)  # Clear previous results
        self.results_text3.insert(tk.END, f"//Use Case ID: {use_case_id}\n")
        self.results_text3.insert(tk.END, f"//Scenarios: {scenario}\n")
        self.results_text3.insert(tk.END, f"//Preconditions: {preconditions}\n")
        self.results_text3.insert(tk.END, f"//Test Cases: {test_cases}\n")
        self.results_text3.config(state=tk.DISABLED)  # Set state back to disabled

    def process_conditions(self,conditions):
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

    def extract_blocks(self,input_txt):
        blocks = {}
        lines = input_txt.strip().split('\n')
        current_function = None
        current_block = []

        for line in lines:
            line = line.strip()
            if line.startswith('$') and line.endswith('() {'):
                if current_function:
                    blocks[current_function] = '\n'.join(current_block).strip()
                current_function = line.split(' ')[0]
                current_block = []
            elif line == '}':
                if current_function:
                    blocks[current_function] = '\n'.join(current_block).strip()
                    current_function = None
            elif current_function:
                current_block.append(line)
        return blocks

    def generate_scripts(self):
        if not self.filepath:
            messagebox.showerror("Error", "Please upload an Excel file first.")
            return

        if not self.use_case_data:
            messagebox.showerror("Error", "No 'Usecase' data loaded. Please upload an Excel file.")
            return

        try:
            for use_case_data in self.use_case_data:
                use_case_id = use_case_data["Use Case ID"]
                scenario = use_case_data["Scenarios"]
                preconditions = use_case_data["Preconditions"]
                test_cases = use_case_data["TestCases"]
                final_output = ""
                
                formatted_scenario = f"// {use_case_id}\n// {scenario}\n"
                formatted_preconditions = self.process_conditions(preconditions)
                formatted_test_cases = self.process_conditions(test_cases)
        
                
                normalized_input = ';'.join(formatted_preconditions.split("\n"))

                for function_name, content_lines in self.text_files_data.items():
                    content_str = ';'.join(content_lines)
                    if content_str in normalized_input:
                        normalized_input = re.sub(re.escape(content_str), function_name, normalized_input)

                normalized_test_case_input = ';'.join(formatted_test_cases.split("\n"))
                for function_name, content_lines in self.text_files_data.items():
                    content_str = ';'.join(content_lines)
                    if content_str in normalized_test_case_input:
                        normalized_test_case_input = re.sub(re.escape(content_str), function_name, normalized_test_case_input)
                
                normalized_input = '\n'.join(normalized_input.split(";"))
                normalized_test_case_input = '\n'.join(normalized_test_case_input.split(";"))


                
                final_output = "".join([formatted_scenario, normalized_input ,normalized_test_case_input,])
                

            save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
            if save_path:
                with open(save_path, "w") as file:
                    file.write(final_output)
                messagebox.showinfo("Success", f"Scripts generated and saved to: {save_path}")

            self.results_text2.config(state=tk.NORMAL)
            self.results_text2.delete(1.0, tk.END)
            self.results_text2.insert(tk.END, final_output)
            self.results_text2.config(state=tk.DISABLED)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while generating scripts: {str(e)}")

# Create the main window
if __name__ == "__main__":
    root = tk.Tk()
    app = ExcelSearchApp(root)
    root.mainloop()
