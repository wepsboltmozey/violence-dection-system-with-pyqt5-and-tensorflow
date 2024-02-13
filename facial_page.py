import tkinter as tk
from tkinter import ttk, filedialog, simpledialog
from PIL import Image, ImageTk
import cv2
import numpy as np
import threading
import tensorflow as tf
from tensorflow.keras.preprocessing.image import img_to_array, load_img
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions

class FacialRecognitionPage:
    def __init__(self, root, back_callback):
        self.root = root
        self.back_callback = back_callback
        self.root.title("Facial Recognition Page")

        # Placeholder for user profile data (username, profile picture)
        self.username = "John Doe"
        self.profile_picture_path = "path/to/profile/picture.jpg"

        # Placeholder for the selected facial image
        self.selected_image_path = None

        # Placeholder for facial recognition result
        self.recognition_result_label = None

        # Placeholder for TensorFlow model
        self.model = tf.keras.applications.MobileNetV2(weights="imagenet", include_top=True)

        # Load and resize the user profile picture
        profile_image = Image.open(self.profile_picture_path)
        profile_image = profile_image.resize((50, 50), Image.ANTIALIAS)
        self.profile_photo = ImageTk.PhotoImage(profile_image)

        # Create a navigation bar
        self.navbar_frame = ttk.Frame(root)
        self.navbar_frame.pack(side="top", fill="x")

        # Add a back button to the navigation bar
        back_button = ttk.Button(self.navbar_frame, text="Back", command=self.back_to_main_page)
        back_button.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # Add title to the navigation bar
        title_label = ttk.Label(self.navbar_frame, text="Facial Recognition", font=("Helvetica", 16))
        title_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        # Display user profile picture and username if available
        if self.username:
            profile_label = ttk.Label(self.navbar_frame, text=self.username)
            profile_label.grid(row=0, column=2, padx=10, pady=5, sticky="e")

            profile_picture_label = ttk.Label(self.navbar_frame, image=self.profile_photo)
            profile_picture_label.grid(row=0, column=3, padx=5, pady=5, sticky="e")

        # Create the main content area
        self.content_frame = ttk.Frame(root)
        self.content_frame.pack(expand=True, fill="both")

        # Create a button to browse and select facial images
        browse_button = ttk.Button(self.content_frame, text="Browse Image", command=self.browse_image)
        browse_button.pack(pady=20)

        # Create buttons for system storage and computer storage
        system_storage_button = ttk.Button(self.content_frame, text="System Storage", command=self.browse_system_storage)
        system_storage_button.pack(pady=10)

        computer_storage_button = ttk.Button(self.content_frame, text="Computer Storage", command=self.browse_computer_storage)
        computer_storage_button.pack(pady=10)

        # Create a label to display the selected image
        self.selected_image_label = ttk.Label(self.content_frame, text="No Image Selected")
        self.selected_image_label.pack(pady=20)

        # Create a bottom bar with buttons for facial recognition actions
        bottom_bar_frame = ttk.Frame(self.content_frame)
        bottom_bar_frame.pack(side="bottom", pady=20)

        start_recognition_button = ttk.Button(bottom_bar_frame, text="Start Facial Recognition", command=self.start_facial_recognition)
        start_recognition_button.pack(side="left", padx=10)

        wanted_button = ttk.Button(bottom_bar_frame, text="Wanted", command=self.submit_to_wanted_list)
        wanted_button.pack(side="left", padx=10)

        cancel_button = ttk.Button(bottom_bar_frame, text="Cancel", command=self.cancel_facial_recognition)
        cancel_button.pack(side="right", padx=10)

    def back_to_main_page(self):
        # Callback to switch back to the main page
        self.root.destroy()

    def browse_image(self):
        # Allow the user to browse and select an image
        file_path = filedialog.askopenfilename(title="Select an Image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.selected_image_path = file_path
            self.selected_image_label.config(text=f"Selected Image: {file_path}")

    def browse_system_storage(self):
        # Placeholder for browsing and selecting images from system storage
        # In a real application, you would list the saved images and allow the user to select one
        # For simplicity, let's assume a pre-defined list of system storage images
        system_storage_images = ["path/to/image1.jpg", "path/to/image2.jpg", "path/to/image3.jpg"]

        selected_image = simpledialog.askitemlist("Select Image", "Select an image from System Storage", system_storage_images)
        if selected_image:
            self.selected_image_path = selected_image
            self.selected_image_label.config(text=f"Selected Image: {selected_image}")

    def browse_computer_storage(self):
        # Allow the user to browse and select an image from computer storage
        file_path = filedialog.askopenfilename(title="Select an Image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.selected_image_path = file_path
            self.selected_image_label.config(text=f"Selected Image: {file_path}")

    def start_facial_recognition(self):
        # Placeholder for facial recognition logic
        if self.selected_image_path:
            # Load and preprocess the selected image
            selected_image = load_img(self.selected_image_path, target_size=(224, 224))
            selected_image_array = img_to_array(selected_image)
            selected_image_array = preprocess_input(selected_image_array)
            selected_image_array = np.expand_dims(selected_image_array, axis=0)

            # Make predictions using the model
            predictions = self.model.predict(selected_image_array)
            label = decode_predictions(predictions)
            recognized_label = f"Label: {label[0][0][1]}"

            # Display the recognition result
            if not self.recognition_result_label:
                self.recognition_result_label = ttk.Label(self.content_frame, text=recognized_label)
                self.recognition_result_label.pack(pady=10)
            else:
                self.recognition_result_label.config(text=recognized_label)

    def submit_to_wanted_list(self):
        # Placeholder for submitting the image to the wanted list
        if self.selected_image_path:
            # Add logic to submit the image to the wanted list
            # For now, let's print a message
            print("Image submitted to wanted list.")

    def cancel_facial_recognition(self):
        # Clear the selected image and recognition result
        self.selected_image_path = None
        self.selected_image_label.config(text="No Image Selected")

        if self.recognition_result_label:
            self.recognition_result_label.destroy()
            self.recognition_result_label = None

if __name__ == "__main__":
    root = tk.Tk()
    facial_recognition_page = FacialRecognitionPage(root, None)  # Replace 'None' with the actual callback for going back to the main page
    root.mainloop()
