import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

class FrequencyAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("POAM Radio Telescope Data Analyzer")
        self.root.geometry("1200x1000")
        
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
        
        # Frequency selection frame
        freq_frame = Frame(root, bg='#f0f0f0')
        freq_frame.pack(pady=10)
        
        Label(freq_frame, text="Select Frequency (MHz):", **label_style).grid(row=0, column=0, padx=5)
        self.freq_combobox = ttk.Combobox(freq_frame, width=15, state='readonly')
        self.freq_combobox.grid(row=0, column=1, padx=5)
        Button(freq_frame, text="Update Plots", command=self.update_plots, 
              font=('Arial', 10), bg='#2196F3', fg='white').grid(row=0, column=2, padx=5)
        
        # Process and Save buttons
        button_frame = Frame(root, bg='#f0f0f0')
        button_frame.pack(pady=10)
        Button(button_frame, text="Process Data", command=self.process_data, 
               font=('Arial', 12, 'bold'), bg='#2196F3', fg='white').pack(side=LEFT, padx=5)
        self.save_avg_button = Button(button_frame, text="Save Freq Plot", command=lambda: self.save_plot('avg'),
                                    font=('Arial', 10), bg='#FF9800', fg='white', state=DISABLED)
        self.save_avg_button.pack(side=LEFT, padx=5)
        self.save_ts_button = Button(button_frame, text="Save Time Plot", command=lambda: self.save_plot('ts'),
                                   font=('Arial', 10), bg='#FF9800', fg='white', state=DISABLED)
        self.save_ts_button.pack(side=LEFT, padx=5)
        
        # Main plot container (split view)
        self.plot_container = Frame(root, bg='white')
        self.plot_container.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Frequency plot frame (left)
        self.freq_plot_frame = Frame(self.plot_container, bg='white', bd=2, relief=GROOVE)
        self.freq_plot_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)
        
        # Time series plot frame (right)
        self.ts_plot_frame = Frame(self.plot_container, bg='white', bd=2, relief=GROOVE)
        self.ts_plot_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=5, pady=5)
        
        # Status bar
        self.status_var = StringVar()
        self.status_var.set("Ready")
        Label(root, textvariable=self.status_var, bd=1, relief=SUNKEN, anchor=W, 
              font=('Arial', 8), bg='#f0f0f0').pack(fill=X, side=BOTTOM)
        
        # Initialize variables
        self.data = None
        self.avg_figure = None
        self.ts_figure = None
        self.current_plot = None
    
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
        """Process the selected file and display both plots"""
        input_file = self.file_entry.get()
        
        if not input_file:
            messagebox.showerror("Error", "Please select a file first")
            return
        
        try:
            self.status_var.set("Processing...")
            self.root.update()
            
            # Process the file
            processed_file = self._process_file(input_file)
            
            # Plot average frequencies
            self.avg_figure = self._plot_average_frequencies()
            self._display_plot(self.avg_figure, self.freq_plot_frame)
            
            # Update frequency dropdown and plot time series for first frequency
            self._update_frequency_combobox()
            if self.freq_combobox['values']:
                self.plot_time_series()
            
            self.status_var.set(f"Success! Processed data saved to: {processed_file}")
            self.save_avg_button.config(state=NORMAL)
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
            self.status_var.set("Error processing file")
    
    def update_plots(self):
        """Update both plots with current settings"""
        if self.data is None:
            messagebox.showwarning("Warning", "Please process data first")
            return
            
        # Update frequency plot
        self.avg_figure = self._plot_average_frequencies()
        self._display_plot(self.avg_figure, self.freq_plot_frame)
        
        # Update time series plot if frequency is selected
        if self.freq_combobox.get():
            self.plot_time_series()
    
    def plot_time_series(self):
        """Plot time series for selected frequency"""
        selected_freq = self.freq_combobox.get()
        if not selected_freq:
            messagebox.showwarning("Warning", "Please select a frequency")
            return
            
        try:
            self.status_var.set(f"Plotting time series for {selected_freq} MHz...")
            self.root.update()
            
            self.ts_figure = self._plot_time_series(selected_freq)
            self._display_plot(self.ts_figure, self.ts_plot_frame)
            
            self.status_var.set(f"Time series plot for {selected_freq} MHz")
            self.save_ts_button.config(state=NORMAL)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to plot time series:\n{str(e)}")
            self.status_var.set("Error plotting time series")
    
    def _process_file(self, filename):
        """Process input file and return processed filename"""
        clean_filename = filename.lstrip("./")
        base_name = os.path.splitext(clean_filename)[0]
        processed_filename = f"{base_name}_processed.txt"
        
        with open(filename, "r") as file:
            lines = file.readlines()
        
        filtered_lines = [line for index, line in enumerate(lines) if index == 0 or index % 2 == 1]
        
        with open(processed_filename, "w") as file:
            file.writelines(filtered_lines)
        
        self.data = pd.read_csv(processed_filename, delim_whitespace=True)
        return processed_filename
    
    def _plot_average_frequencies(self):
        """Create average frequency plot"""
        df_avg = self.data.mean(axis=0)
        float_array = np.array(df_avg.index.tolist(), dtype=float)
        
        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(float_array, df_avg.values)
        ax.set_xlabel('Frequency (MHz)')
        ax.set_ylabel('Average Amplitude (dBm)')
        ax.set_title('Average Amplitude Spectrum')
        ax.grid(True)
        
        # Highlight selected frequency if available
        selected_freq = self.freq_combobox.get()
        if selected_freq:
            try:
                freq_val = float(selected_freq)
                ax.axvline(x=freq_val, color='r', linestyle='--', alpha=0.5)
            except ValueError:
                pass
        
        return fig
    
    def _plot_time_series(self, frequency):
        """Create time series plot for specific frequency"""
        time_interval = 0.0529  # Your specified time interval
        intensity = self.data[frequency]
        time_series = np.arange(0, time_interval * len(intensity), time_interval)
        
        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        line, = ax.plot(time_series, intensity)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Intensity (dBm)')
        ax.set_title(f'Time Series at {frequency} MHz')
        ax.grid(True)
        
        # Add annotation for cursor position
        annot = ax.annotate("", xy=(0,0), xytext=(10,10), textcoords="offset points",
                           bbox=dict(boxstyle="round", fc="w"),
                           arrowprops=dict(arrowstyle="->"))
        annot.set_visible(False)
        
        def on_motion(event):
            if event.inaxes == ax:
                x, y = event.xdata, event.ydata
                annot.xy = (x, y)
                annot.set_text(f"Time: {x:.3f}s\nIntensity: {y:.2f} dBm")
                annot.set_visible(True)
                fig.canvas.draw_idle()
                
        fig.canvas.mpl_connect('motion_notify_event', on_motion)
        
        return fig
    
    def _update_frequency_combobox(self):
        """Update frequency dropdown with available frequencies"""
        frequencies = [str(f) for f in self.data.columns.tolist()]
        self.freq_combobox['values'] = frequencies
        if frequencies:
            self.freq_combobox.current(0)
    
    def _display_plot(self, figure, frame):
        """Display the given figure in the specified frame"""
        for widget in frame.winfo_children():
            widget.destroy()
        
        canvas = FigureCanvasTkAgg(figure, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        
        # Add navigation toolbar
        toolbar = NavigationToolbar2Tk(canvas, frame)
        toolbar.update()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)
    
    def save_plot(self, plot_type):
        """Save the current plot to a file"""
        figure = self.avg_figure if plot_type == 'avg' else self.ts_figure
        
        if figure is None:
            messagebox.showwarning("Warning", f"No {plot_type} plot to save")
            return
        
        filetypes = [
            ('PNG files', '*.png'),
            ('JPEG files', '*.jpg'),
            ('PDF files', '*.pdf'),
            ('SVG files', '*.svg'),
            ('All files', '*.*')
        ]
        
        default_name = os.path.splitext(self.file_entry.get())[0]
        default_name += "_freq_plot.png" if plot_type == 'avg' else "_time_plot.png"
        
        filename = filedialog.asksaveasfilename(
            title="Save Plot As",
            initialfile=default_name,
            filetypes=filetypes,
            defaultextension='.png'
        )
        
        if filename:
            try:
                figure.savefig(filename, dpi=300, bbox_inches='tight')
                self.status_var.set(f"Plot saved to: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save plot:\n{str(e)}")

if __name__ == "__main__":
    root = Tk()
    app = FrequencyAnalyzerApp(root)
    root.mainloop()