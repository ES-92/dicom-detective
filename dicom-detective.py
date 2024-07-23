import tkinter as tk
from tkinter import filedialog, messagebox
import pydicom
import os
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def compare_dicom_files(file1_path, file2_path):
    try:
        # Load the DICOM files
        dicom1 = pydicom.dcmread(file1_path)
        dicom2 = pydicom.dcmread(file2_path)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read DICOM files: {e}")
        return None

    # Collect all tags from both files
    tags1 = set(dicom1.dir())
    tags2 = set(dicom2.dir())
    all_tags = tags1.union(tags2)

    differences = []

    # Compare the tags, excluding 'PixelData'
    for tag in all_tags:
        if tag == 'PixelData':
            continue
        try:
            value1 = getattr(dicom1, tag, "Not Found")
            value2 = getattr(dicom2, tag, "Not Found")
        except Exception as e:
            value1 = f"Error: {e}"
            value2 = f"Error: {e}"
        
        if value1 != value2:
            differences.append((tag, value1, value2))
    
    return differences

def open_file1():
    file_path = filedialog.askopenfilename(title="Select first DICOM file", filetypes=[("DICOM files", "*.dcm")])
    if file_path:
        entry_file1.delete(0, tk.END)
        entry_file1.insert(0, file_path)
        plot_images()

def open_file2():
    file_path = filedialog.askopenfilename(title="Select second DICOM file", filetypes=[("DICOM files", "*.dcm")])
    if file_path:
        entry_file2.delete(0, tk.END)
        entry_file2.insert(0, file_path)
        plot_images()

def plot_images():
    file1_path = entry_file1.get()
    file2_path = entry_file2.get()
    
    if not os.path.exists(file1_path) or not os.path.exists(file2_path):
        return

    try:
        dicom1 = pydicom.dcmread(file1_path)
        dicom2 = pydicom.dcmread(file2_path)

        image1 = dicom1.pixel_array
        image2 = dicom2.pixel_array

        fig, axes = plt.subplots(1, 2, figsize=(10, 5))
        axes[0].imshow(image1, cmap='gray')
        axes[0].set_title('First DICOM Image')
        axes[1].imshow(image2, cmap='gray')
        axes[1].set_title('Second DICOM Image')

        for ax in axes:
            ax.axis('off')

        if hasattr(root, 'canvas'):
            root.canvas.get_tk_widget().grid_forget()

        root.canvas = FigureCanvasTkAgg(fig, master=root)
        root.canvas.draw()
        root.canvas.get_tk_widget().grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')
    except Exception as e:
        messagebox.showerror("Error", f"Failed to plot DICOM images: {e}")

def show_differences():
    file1_path = entry_file1.get()
    file2_path = entry_file2.get()
    
    if not os.path.exists(file1_path) or not os.path.exists(file2_path):
        messagebox.showerror("Error", "Please select valid DICOM files.")
        return

    def compare_and_display():
        differences = compare_dicom_files(file1_path, file2_path)
        
        if differences is None:
            return

        text_output.delete(1.0, tk.END)

        if differences:
            for diff in differences:
                text_output.insert(tk.END, f"Attribute: {diff[0]}\n")
                text_output.insert(tk.END, f"  File1: {diff[1]}\n")
                text_output.insert(tk.END, f"  File2: {diff[2]}\n\n")
        else:
            text_output.insert(tk.END, "No differences found.")

    # Run the comparison in a separate thread to avoid blocking the GUI
    compare_thread = threading.Thread(target=compare_and_display)
    compare_thread.start()

# Create the main window
root = tk.Tk()
root.title("DICOM Detective")

# Configure grid layout
root.grid_rowconfigure(4, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)

# Create and place the widgets
tk.Label(root, text="First DICOM file:").grid(row=0, column=0, padx=10, pady=5)
entry_file1 = tk.Entry(root, width=50)
entry_file1.grid(row=0, column=1, padx=10, pady=5)
btn_file1 = tk.Button(root, text="Browse...", command=open_file1)
btn_file1.grid(row=0, column=2, padx=10, pady=5)

tk.Label(root, text="Second DICOM file:").grid(row=1, column=0, padx=10, pady=5)
entry_file2 = tk.Entry(root, width=50)
entry_file2.grid(row=1, column=1, padx=10, pady=5)
btn_file2 = tk.Button(root, text="Browse...", command=open_file2)
btn_file2.grid(row=1, column=2, padx=10, pady=5)

btn_compare = tk.Button(root, text="Compare", command=show_differences)
btn_compare.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

text_output = tk.Text(root, width=100, height=20)
text_output.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

# Start the main loop
root.mainloop()
