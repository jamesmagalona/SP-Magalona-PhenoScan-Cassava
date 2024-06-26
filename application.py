"""
Developer: Rowell James C. Magalona
Email: rowelljamesmagalona@gmail.com
Description: 
    This desktop application is designed for cassava research at IPB, 
    specifically developed in collaboration with lead researcher Jose Arnel Reyes.
    The application automates the processing of multiple images to improve efficiency
    over traditional methods, which are time-consuming. 


Functionality:
    - Process multiple images simultaneously, including tasks like image conversion, 
    blurring, filtering, masking, combining, and finding contours.
    - Extracts phenotypic data such as projected leaf area, green area pixel count, 
    blue area pixel count, projected convex hull, and number of pixels on the convex hull.
    - Save resulting processed images to specific folders.
    - Export data as CSV files containing projected leaf area, green area pixel count, 
    blue area pixel count, projected convex hull, and number of pixels on the convex hull.
"""


import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk
from tkinter import font as tkfont
import cv2
import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Pool
import threading
import csv
import re
from tkinter import messagebox
import psutil
import sys
import os



#for sorting the image filenames
def natural_sort_key(s):
    #split the string into a list of strings and integers
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]


class ImageSelectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PhenoSnap Cassava")
        
        #for deployment
        #determine the path to the resources folder
        if getattr(sys, 'frozen', False):
            #if the application is frozen (e.g., compiled with PyInstaller)
            base_path = sys._MEIPASS  #use PyInstaller's temporary directory
        else:
            #if running in a normal Python environment
            base_path = os.path.abspath(os.path.dirname(__file__))
        
        #load the icon image
        icon_path = os.path.join(base_path, "resources", "icon.ico")
        icon_image = Image.open(icon_path)
        icon_photo = ImageTk.PhotoImage(icon_image)
        self.root.iconphoto(False, icon_photo)
        
        #center window on the screen
        window_width = 1000
        window_height = 600
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_coordinate = (screen_width - window_width) // 2
        y_coordinate = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")
        
        #make the app responsive
        self.root.columnconfigure(index=0, weight=1)
        self.root.columnconfigure(index=1, weight=1)
        self.root.columnconfigure(index=2, weight=1)
        self.root.rowconfigure(index=0, weight=1)
        self.root.rowconfigure(index=1, weight=1)
        self.root.rowconfigure(index=2, weight=1)

        #create a style
        self.style = ttk.Style(root)
        
        #determine the path to the forest-dark folder
        base_dir = os.path.dirname(os.path.abspath(__file__))
        forest_dark_tcl_path = os.path.join(base_dir, "forest-dark.tcl")

        #import the dark theme tcl file
        self.root.tk.call("source", forest_dark_tcl_path)
        
        #set the dark theme with the theme_use method
        self.style.theme_use("forest-dark")

        #create variables to store image paths and current index
        self.image_paths = []
        self.current_index = 0
        
        #create a Frame for input widgets
        self.widgets_frame = tk.Frame(root, bg="#4C4A48", width=300, height=600)
        self.widgets_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.widgets_frame.pack_propagate(False)

        #create a style object
        self.style = ttk.Style()
        # self.style.configure("Custom.TButton", foreground="blue", background="#333333")

        # Configure the style object to set the font for the Button widget
        self.style.configure("Custom.TButton", font=("Century Gothic", 10), foreground="#FFFFFF",background="#FFFFFF")

        #button to open folder and select images
        self.open_folder_button = ttk.Button(self.widgets_frame, text="Open Folder", command=self.open_folder, style="Custom.TButton")
        self.open_folder_button.pack(padx=5, pady=10, fill=tk.X)

        #button to manually select images
        self.save_images_button = ttk.Button(self.widgets_frame, text="Save Images", command=self.save_images, style="Custom.TButton",state = "disabled")
        self.save_images_button.pack(padx=5, fill=tk.X)

        #separator
        separator = ttk.Separator(self.widgets_frame, orient="horizontal")
        separator.pack(fill="x", pady=10)

        #button to save csv file
        self.save_csv_button = ttk.Button(self.widgets_frame, text="Save CSV", command=self.save_to_csv, style="Custom.TButton",state = "disabled")
        self.save_csv_button.pack(padx=5, pady=5, fill=tk.X)

        #separator
        separator = ttk.Separator(self.widgets_frame, orient="horizontal")
        separator.pack(fill="x", pady=10)

        #listbox to display selected image names
        self.image_listbox = tk.Listbox(self.widgets_frame, selectmode=tk.SINGLE, bg="#4C4A48")
        self.image_listbox.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)

        #scrollbar for the listbox
        scrollbar = ttk.Scrollbar(self.widgets_frame, orient=tk.VERTICAL, command=self.image_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.image_listbox.config(yscrollcommand=scrollbar.set)

        #create a Frame for the canvas and navigation buttons
        self.canvas_frame = tk.Frame(root, width=700, height=600)
        self.canvas_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        self.canvas_frame.pack_propagate(False)

        #create a custom font
        custom_font = tkfont.Font(family="Baskerville Old Face", size=20)

        #create a Label widget with custom font
        text_label = tk.Label(self.canvas_frame, text="PhenoScan Cassava", font=custom_font)

        #pack the Label widget
        text_label.pack(side=tk.TOP)

        #separator
        separator = ttk.Separator(self.canvas_frame, orient="horizontal")
        separator.pack(fill="x", pady=10)

        #placeholder rectangle for displaying the image
        self.canvas = tk.Canvas(self.canvas_frame, width=500, height=400, bg="#4b9841")
        self.canvas.pack(padx=10, pady=10)

        # # Load and display initial image
        # self.initial_image = tk.PhotoImage(file="PhenoScanCassavaLogo1.png")  # Provide the correct path
        # self.image_id = self.canvas.create_image(250, 200, image=self.initial_image)

        #create a custom font
        custom_font = tkfont.Font(family="Century Gothic", size=12)

        #create a Label widget with custom font
        self.text_label = tk.Label(self.canvas_frame, text="Projected Cassava Leaf Area: _ squarecm", font=custom_font)
        
        #pack the Label widget
        self.text_label.pack(side=tk.RIGHT,padx=20, pady=20)


        #button to navigate to the previous image
        self.prev_button = ttk.Button(self.canvas_frame, text="Prev", command=self.prev_image, style="Accent.TButton")
        self.prev_button.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X)

        #button to navigate to the next image
        self.next_button = ttk.Button(self.canvas_frame, text="Next", command=self.next_image, style="Accent.TButton")
        self.next_button.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X)

        #image cache
        self.image_cache = {}
        self.leaf_area_dict = {}
        self.count_processed_images = 0

        #placeholder for the progress bar
        self.progress_bar = ttk.Progressbar(self.root, mode="indeterminate", length=200)
    
    #filtering to keep mask larger than said threshold
    def filter_connected_components(self,mask, min_component_size):
        #perform connected component analysis
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)

        #create a mask to keep only components larger than the threshold
        filtered_mask = np.zeros_like(mask)
        for label in range(1, num_labels):  #skip background label 0
            if stats[label, cv2.CC_STAT_AREA] >= min_component_size:
                filtered_mask[labels == label] = 255
        
        return filtered_mask
    
    #count pixels
    def count_pixels_in_hull(self,image, hull):
        #create an empty mask
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        
        #fill the hull with white color on the mask
        cv2.drawContours(mask, [hull], -1, (255), thickness=cv2.FILLED)
        
        #count the number of non-zero pixels in the mask
        pixel_count = cv2.countNonZero(mask)
        
        return pixel_count

    #image processing
    def process_image(self,image_path):
        #read image using cv 
        #then apply gaussian blur
        #then convert it to hsv format for easy identification
        image = cv2.imread(image_path)
        blurred_image = cv2.GaussianBlur(image, (5, 5), 0)
        hsv_image = cv2.cvtColor(blurred_image, cv2.COLOR_BGR2HSV)

        #------------------------morph first before masking-----------------
        kernel = np.ones((9, 9), np.uint8)
        green_mask = cv2.morphologyEx(hsv_image, cv2.MORPH_OPEN, kernel)
        green_mask = cv2.inRange(green_mask, (34, 25, 25), (86, 255,255))

        #apply filtering
        #costumized threshold (you can adjust it)
        min_component_size = 20000
        green_mask = self.filter_connected_components(green_mask, min_component_size)

        #find contours in the green mask
        contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        #compute the convex hull for each contour
        hulls = [cv2.convexHull(contour) for contour in contours]

        #--------------------------for convex hull----------------------------
        #function to compute the distance between two convex hulls
        def hulls_close(hull1, hull2, max_distance):
            for point1 in hull1:
                for point2 in hull2:
                    distance = np.linalg.norm(point1[0] - point2[0])
                    if distance < max_distance:
                        return True
            return False

        #merge convex hulls if they are close to each other
        def merge_hulls(hulls, max_distance):
            merged = []
            while hulls:
                current_hull = hulls.pop(0)
                to_merge = [current_hull]
                i = 0
                while i < len(hulls):
                    if hulls_close(current_hull, hulls[i], max_distance):
                        to_merge.append(hulls.pop(i))
                    else:
                        i += 1
                merged_hull = np.vstack(to_merge)
                merged.append(cv2.convexHull(merged_hull))
            return merged if merged else hulls  #return original hulls if no merges occurred

        #merging hulls
        #customized threshold value (you can adjust it)
        max_distance = 500  #set your desired maximum distance here
        merged_hulls = merge_hulls(hulls, max_distance)


        #find the largest hull
        largest_hull = max(merged_hulls, key=cv2.contourArea)

        #create a mask representing the largest hull
        largest_hull_mask = np.zeros_like(green_mask)
        cv2.drawContours(largest_hull_mask, [largest_hull], -1, (255), thickness=cv2.FILLED)


        #perform bitwise AND operation between green mask and largest hull mask
        green_mask = cv2.bitwise_and(green_mask, largest_hull_mask)


        # Slice the green
        imask = green_mask>0
        green = np.zeros_like(image, np.uint8)
        green[imask] = image[imask]

        #mask of blue (100,40,40) ~ (150,255,255)
        blue_mask = cv2.inRange(hsv_image, (100, 40, 40), (150, 255, 255))

        #slice the blue
        imask_blue = blue_mask > 0
        blue = np.zeros_like(image, np.uint8)
        blue[imask_blue] = image[imask_blue]

        #combine masks for blue and green areas
        combined_mask = cv2.bitwise_or(green_mask, blue_mask)

        #convert the image from BGR to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        #apply Gaussian Blur
        blurred_image = cv2.GaussianBlur(rgb_image, (5, 5), 0)
        try:
            #slice the combined mask
            imask_combined = combined_mask > 0
            combined_image = np.zeros_like(blurred_image, np.uint8)
            combined_image[imask_combined] = blurred_image[imask_combined]

            #calculate pixel area of the blue part
            blue_area_pixel = np.sum(blue_mask > 0)

            #calculate pixel area of the green part
            leaf_area_pixel = np.sum(green_mask > 0)

            convex_hull_pixel = self.count_pixels_in_hull(image, largest_hull)

            print("Pixel area of the blue part:", blue_area_pixel, "pixels")
            print("Pixel area of the green part:", leaf_area_pixel, "pixels")

            leaf_area_cm2 = self.calculate_leaf_area_cm2(leaf_area_pixel, blue_area_pixel)
            convex_hull_cm2 = self.calculate_leaf_area_cm2(convex_hull_pixel, blue_area_pixel)
            #self.leaf_area_dict[image_path] = leaf_area_cm2

            #store the values in the dictionary
            self.leaf_area_dict[image_path] = {
                'leaf_area_cm2': leaf_area_cm2,
                'number_of_green_pixels': leaf_area_pixel,
                'number_of_blue_pixels': blue_area_pixel,
                'convex_hull_cm2': convex_hull_cm2,
                'convex_hull_pixels': convex_hull_pixel
            }

            self.count_processed_images = self.count_processed_images + 1
            print("number of processed images: ",self.count_processed_images)
            
            #draw contours on the original image to have the pesonalized image result requested by ipb
            cv2.drawContours(combined_image, [largest_hull], -1, (0, 255, 0), 5)

            #return final_image
            #return blue_mask
            return combined_image
        
        except Exception as e:
            print("An error occurred:", e)
            print(image_path)
            return blurred_image

    #calculations
    def calculate_leaf_area_cm2(self, leaf_area_pixel, blue_area_pixel):
        blue_area_cm2 = 10

        if leaf_area_pixel == 0 or blue_area_pixel == 0:
            return 0
        else:
            #calculate conversion factor
            conversion_factor = blue_area_pixel / blue_area_cm2

            #calculate leaf area in square centimeters
            leaf_area_cm2 = leaf_area_pixel / conversion_factor

            print(f"Leaf area: {leaf_area_cm2} square centimeters")

            return leaf_area_cm2
    
    #calculations
    def calculate_convex_hull(self, convex_hull_pixel, blue_area_pixel):
        blue_area_cm2 = 10

        if convex_hull_pixel == 0 or blue_area_pixel == 0:
            return 0
        else:
            #calculate conversion factor
            conversion_factor = blue_area_pixel / blue_area_cm2

            #calculate leaf area in square centimeters
            convex_hull_cm2 = convex_hull_pixel / conversion_factor

            print(f"Leaf area: {convex_hull_cm2} square centimeters")

            return convex_hull_cm2
    
    #check if memory already at 85% then it will not run anymore
    def is_memory_critical(self, threshold=85):
            memory_info = psutil.virtual_memory()
            return memory_info.percent > threshold

    #open selected folder
    def open_folder(self):
        self.image_cache = {}
        self.leaf_area_dict = {}
        self.count_processed_images = 0
        self.current_index = 0
        self.image_path = []
        #open file dialog to select a folder
        folder_path = filedialog.askdirectory(title="Select Folder")

        contents = os.listdir(folder_path)
        
        #check if the list is empty
        if not contents:
            #display error message
            messagebox.showerror("Error", f"Folder is empty\n")
            return True
        else:
            #start a new thread to process images
            threading.Thread(target=self.process_images_thread, args=(folder_path,), daemon=True).start()

    #i used threading for the progress bar
    #unecessary but idgaf
    def process_images_thread(self, folder_path):
        if folder_path:
            #create a progress window
            self.progress_window = tk.Toplevel(self.root)
            self.progress_window.title("Processing...")
            #calculate window position to center it on the screen
            window_width = 300
            window_height = 100
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            x_coordinate = (screen_width - window_width) // 2
            y_coordinate = (screen_height - window_height) // 2
            self.progress_window.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

            self.progress_window.transient(self.root)  # Set the progress window as transient to the main window
            self.progress_window.grab_set()  # Grab focus to the progress window
            # self.progress_window.overrideredirect(True)  # Remove window manager decorations

            #add text to the window
            text_label = tk.Label(self.progress_window, text="Processing images...", fg="white", font=("Century Gothic", 10))
            text_label.pack(pady=10)

            #create a progress bar as an instance attribute
            self.progress_bar = ttk.Progressbar(self.progress_window, mode="determinate", length=250)
            self.progress_bar.pack(pady=20)

            #get list of image files in the folder
            image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
            image_files.sort(key=natural_sort_key)  #sort the filenames naturally
            self.image_paths = [os.path.join(folder_path, filename) for filename in image_files]
            num_images = len(image_files)

            if self.is_memory_critical():
                print("Warning: Memory usage is above 85%. Cannot process more images.")
                #close the progress window
                self.progress_window.destroy()
                #display error message
                messagebox.showerror("Error", f"Memory Almost Full. Cannot process more images\n")
                return True

            #process each image and store in the cache
            for i, image_path in enumerate(self.image_paths, start=1):
                if image_path not in self.image_cache:
                    image_with_contours = self.process_image(image_path)
                    self.image_cache[image_path] = image_with_contours
                
                #update progress bar
                progress_value = (i / num_images) * 100
                self.progress_bar["value"] = progress_value
                self.progress_bar.update()

            #update the label text
            self.update_label_text()

            #update the listbox
            self.update_image_listbox()
            
            #highlight the first image name in the listbox
            if self.image_paths:
                self.image_listbox.selection_set(0)
                self.current_index = 0
                self.show_image()

            #close the progress window
            self.progress_window.destroy()

    #save images
    def save_images(self):
        #open a dialog for the user to select the directory to save images
        save_directory = filedialog.askdirectory()

        #start a new thread to process images
        threading.Thread(target=self.save_images_thread, args=(save_directory,)).start()
        
    #used threadung in saving message fo the progress bar
    def save_images_thread(self, save_directory):
        if save_directory:
            #create a progress window
            self.progress_window = tk.Toplevel(self.root)
            self.progress_window.title("Saving...")
            #calculate window position to center it on the screen
            window_width = 300
            window_height = 100
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            x_coordinate = (screen_width - window_width) // 2
            y_coordinate = (screen_height - window_height) // 2
            self.progress_window.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

            self.progress_window.transient(self.root)  #set the progress window as transient to the main window
            self.progress_window.grab_set()  #grab focus to the progress window

            #add text to the window
            text_label = tk.Label(self.progress_window, text="Saving images...", fg="white", font=("Poppins Light", 10))
            text_label.pack(pady=10)

            #create a progress bar as an instance attribute
            self.progress_bar = ttk.Progressbar(self.progress_window, mode="determinate", length=250)
            self.progress_bar.pack(pady=20)


            for i, (image_path, image) in enumerate(self.image_cache.items(), start=1):
                #extract the filename without extension
                base_filename = os.path.splitext(os.path.basename(image_path))[0]
                
                #create a new filename with the counter
                new_filename = f"{base_filename}.jpg"
                save_path = os.path.join(save_directory, new_filename)
                
                #check if the file already exists and find a unique filename
                counter = 1
                while os.path.exists(save_path):
                    new_filename = f"{base_filename}({counter}).jpg"
                    save_path = os.path.join(save_directory, new_filename)
                    counter += 1

                #save the image using OpenCV
                cv2.imwrite(save_path, cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                print(f"Saved {save_path}")
                
                #update progress bar
                progress_value = (i / len(self.image_cache)) * 100
                self.progress_bar["value"] = progress_value
                self.progress_bar.update()

            #close the progress window
            self.progress_window.destroy()

    #for displaying the image
    def show_image(self):
        if self.image_paths:
            image_path = self.image_paths[self.current_index]

            #cache the image
            if image_path in self.image_cache:
                image_with_contours = self.image_cache[image_path]
            else:
                image_with_contours = self.process_image(image_path)
                self.image_cache[image_path] = image_with_contours

            image = Image.fromarray(image_with_contours)

            image.thumbnail((400, 400))  #resize image to fit canvas
            photo = ImageTk.PhotoImage(image)
            self.canvas.create_image(250, 250, image=photo, anchor=tk.CENTER)
            self.canvas.image = photo  #keep reference to avoid garbage collection
            
            #highlight the first image name in the listbox when an image is opened
            if self.current_index == 0:
                self.image_listbox.selection_set(0)
    
    #update image listbox
    def update_image_listbox(self):
        self.save_images_button.config(state="enabled")
        self.save_csv_button.config(state="enabled")
        self.image_listbox.delete(0, tk.END)

        for image_path in self.image_paths:
            self.image_listbox.insert(tk.END, os.path.basename(image_path))
    
    #display
    def display_selected_image(self, event):
        selected_index = self.image_listbox.curselection()
        if selected_index:
            self.current_index = selected_index[0]
            self.show_image()
    
    #image navigation
    def next_image(self):
        if self.image_paths:
            #update the current index
            self.current_index = (self.current_index + 1) % len(self.image_paths)
            #show the image
            self.show_image()
            #update the selection in the listbox
            self.image_listbox.selection_clear(0, tk.END)  # Clear previous selection
            self.image_listbox.selection_set(self.current_index)  # Highlight the current index
            self.image_listbox.see(self.current_index)  # Scroll to the current index
            #update the label text
            self.update_label_text()

    #image navigation
    def prev_image(self):
        if self.image_paths:
            #update the current index
            self.current_index = (self.current_index - 1) % len(self.image_paths)
            #show the image
            self.show_image()
            #update the selection in the listbox
            self.image_listbox.selection_clear(0, tk.END)  # Clear previous selection
            self.image_listbox.selection_set(self.current_index)  # Highlight the current index
            self.image_listbox.see(self.current_index)  # Scroll to the current index
            #update the label text
            self.update_label_text()

    #update cassava leaf area
    def update_label_text(self):
        #get the current image path
        current_image_path = self.image_paths[self.current_index]
        
        #get the leaf area for the current image path from the dictionary
        data = self.leaf_area_dict.get(current_image_path, None)

        if data:
            leaf_area = data.get('leaf_area_cm2', "Unknown")
        else:
            leaf_area = "Unknown"
        
        #update the text of the label with formatted leaf area
        self.text_label.config(text=f"Projected Cassava Leaf Area: {leaf_area:.2f} squarecm")

    def save_to_csv(self):
        #prompt the user to select a file path for saving the CSV file
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            #open the CSV file for writing
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                #write the header row
                writer.writerow(['Image Filename', 'Leaf Area cm2', 'Number of Green Pixels', 'Number of Blue Pixels', 'Convex Hull Area', 'Convex Hull Pixels'])
                #write each key-value pair from the dictionary to a separate row
                for image_path, data in self.leaf_area_dict.items():
                    filename = os.path.basename(image_path)
                    writer.writerow([filename, data['leaf_area_cm2'], data['number_of_green_pixels'], data['number_of_blue_pixels'], data['convex_hull_cm2'], data['convex_hull_pixels']])
            print("CSV file saved to:", file_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageSelectorApp(root)
    root.mainloop()