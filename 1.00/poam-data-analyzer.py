import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from tkinter import *
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class FrequencyAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("POAM Radio Telescope Data Analyzer")
        self.root.geometry("800x600")
        
        # Configure styles
        self.root.configure(bg='#f0f0f0')
        button_style = {'font': ('Arial', 10), 'bg': '#4CAF50', 'fg': 'white'}
        label_style = {'font': ('Arial', 10), 'bg': '#f0f0f0'}
        
        # Create GUI elements
        Label(root, text="POAM Radio Telescope Data Analyzer", font=('Arial', 16, 'bold'), bg='#f0f0f0').pack(pady=10)
        
        # File selection frame
        file_frame = Frame(root, bg='#f0f0f0')
        file_frame.pack(pady=10)
        
        Label(file_frame, text="Select Data File:", **label_style).grid(row=0, column=0, padx=5)
        
        self.file_entry = Entry(file_frame, width=50, font=('Arial', 10))
        self.file_entry.grid(row=0, column=1, padx=5)
        
        Button(file_frame, text="Browse", command=self.browse_file, **button_style).grid(row=0, column=2, padx=5)
        
        # Process button
        Button(root, text="Process Data", command=self.process_data, 
               font=('Arial', 12, 'bold'), bg='#2196F3', fg='white').pack(pady=20)
        
        # Save button
        self.save_button = Button(root, text="Save Plot", command=self.save_plot,
                         font=('Arial', 10), bg='#FF9800', fg='white', state=DISABLED)
        self.save_button.pack(pady=5)

        # Plot frame
        self.plot_frame = Frame(root, bg='white')
        self.plot_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Status bar
        self.status_var = StringVar()
        self.status_var.set("Ready")
        Label(root, textvariable=self.status_var, bd=1, relief=SUNKEN, anchor=W, 
              font=('Arial', 8), bg='#f0f0f0').pack(fill=X, side=BOTTOM)
    
    def browse_file(self):
        """Open file dialog to select input file"""
        filename = filedialog.askopenfilename(
            title="Select Data File",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
        )
        if filename:
            self.file_entry.delete(0, END)
            self.file_entry.insert(0, filename)
    
    def process_data(self):
        """Process the selected file and display results"""
        input_file = self.file_entry.get()
        
        if not input_file:
            messagebox.showerror("Error", "Please select a file first")
            return
        
        try:
            self.status_var.set("Processing...")
            self.root.update()  # Update the GUI
            
            # Process the file
            processed_file, figure = self._process_frequency_data(input_file)
            
            # Clear previous plot
            for widget in self.plot_frame.winfo_children():
                widget.destroy()
            
            # Embed the plot in the GUI
            canvas = FigureCanvasTkAgg(figure, master=self.plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=BOTH, expand=True)
            
            self.status_var.set(f"Success! Processed data saved to: {processed_file}")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
            self.status_var.set("Error processing file")
    
    def save_plot(self):
        """Save the current plot to a file"""
        if not hasattr(self, 'current_figure'):
            messagebox.showwarning("Warning", "No plot to save. Process data first.")
            return
        
        filetypes = [
            ('PNG files', '*.png'),
            ('JPEG files', '*.jpg'),
            ('PDF files', '*.pdf'),
            ('SVG files', '*.svg'),
            ('All files', '*.*')
        ]
        
        default_filename = os.path.splitext(self.file_entry.get())[0] + "_plot.png"
        
        filename = filedialog.asksaveasfilename(
            title="Save Plot As",
            initialfile=default_filename,
            filetypes=filetypes,
            defaultextension='.png'
        )
        
        if filename:
            try:
                self.current_figure.savefig(filename, dpi=300, bbox_inches='tight')
                self.status_var.set(f"Plot saved to: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save plot:\n{str(e)}")

    def _process_frequency_data(self, filename):
        """Core processing function (modified from original)"""
        # Clean the input filename
        clean_filename = filename.lstrip("./")
        base_name = os.path.splitext(clean_filename)[0]
        processed_filename = f"{base_name}_processed.txt"
        
        # Read and filter lines
        with open(filename, "r") as file:
            lines = file.readlines()
        
        filtered_lines = [line for index, line in enumerate(lines) if index == 0 or index % 2 == 1]
        
        # Save processed file
        with open(processed_filename, "w") as file:
            file.writelines(filtered_lines)
        
        # Read and process data
        data = pd.read_csv(processed_filename, delim_whitespace=True)
        df_avg = data.mean(axis=0)
        float_array = np.array(df_avg.index.tolist(), dtype=float)
        
        # Create plot
        fig = plt.figure(figsize=(8, 4), dpi=100)
        plt.plot(float_array, df_avg.values)
        plt.xlabel('Frequency (MHz)')
        plt.ylabel('Average Amplitude (dBm)')
        plt.title(f'Average Amplitude for Each Frequency\n{base_name}')
        plt.grid(True)
        plt.tight_layout()
        
        self.current_figure = fig  # Store the figure for saving later
        self.save_button.config(state=NORMAL)  # Enable the save button
        
        return processed_filename, fig

# Create and run the application
if __name__ == "__main__":
    root = Tk()
    app = FrequencyAnalyzerApp(root)
    root.mainloop()