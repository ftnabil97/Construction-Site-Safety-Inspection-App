#!/usr/bin/env python
# coding: utf-8

# In[12]:


import tkinter as tk
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import numpy as np
from ultralytics import YOLO
import datetime

filepaths=[]
file_list=[]
frame3=None
current_file_index=0
classes = ['Gloves', 'Hardhat', 'Mask', 'NO-Gloves', 'NO-Hardhat',
           'NO-Mask', 'NO-Safety Boot', 'NO-Safety Vest', 'Person', 'Safety Boot', 'Safety Vest']
label1 = None  # Global variable for label widget
success=False
cap=None
_class_index=None


def upload_files():
    global filepaths
    global file_list
    global current_file_index
    global img
    global video_frames

    filetypes = [('Image Files', '*.jpg *.jpeg *.png'), ('Video Files', '*.mp4 *.avi')]
    filepaths = filedialog.askopenfilename(multiple=True, filetypes=filetypes)
    
    file_list=[] 
    current_file_index=0
    
    
    for filepath in filepaths:
        if filepath.lower().endswith(('.jpg', '.jpeg', '.png')):
            img=cv2.imread(filepath)
            
            img=detect(img)
            annotated_image = img[0].plot()
            
            numpy_image = annotated_image.astype(np.uint8)  # Convert to uint8 data type
            numpy_image=numpy_image[:, :, ::-1] #convert from RGB to BGR
            PIL_image = Image.fromarray(numpy_image) #convert numpy array to PIL image

            PIL_image=PIL_image.resize((640,640))
            uploaded_file=ImageTk.PhotoImage(PIL_image)
            file_list.append(uploaded_file)
        else:
            pass

    if file_list:
        file_display(current_file_index)
        
def file_display(file_index):
    global label1
    global button_forward
    global button_back
    global success
    global cap
    
    if label1 is not None:
        if cap is not None:
            cap.release()
        success=False
        label1.grid_forget() # Remove the existing label
      
        
    label1=Label(image=file_list[file_index],bg="SystemButtonFace")
    label1.grid(in_=frame3, row=0,column=1,columnspan=3)
    
    button_back = tk.Button(window, text="<<", command=back, state=tk.DISABLED,bg="#cfd3e6")
    button_forward = tk.Button(window, text=">>", command=forward,bg="#cfd3e6")
    
    button_back.grid(row=9, column=1)
    button_forward.grid(row=9, column=3)
    

    
    # Update the state of forward and back buttons
    if file_index == 0:
        button_back.config(state=tk.DISABLED)
    else:
        button_back.config(state=tk.NORMAL)
        
    if file_index == len(file_list) - 1:
        button_forward.config(state=tk.DISABLED)
    else:
        button_forward.config(state=tk.NORMAL)
    
def forward():
    global current_file_index
    current_file_index +=1
    file_display(current_file_index)
    
def back():
    global current_file_index
    current_file_index -=1
    file_display(current_file_index)

def hide_button(widget):
    widget.grid_forget()
def show_button(widget):
    widget.grid()   
    
def capture_image():
    image=Image.fromarray(numpy_frame)
    time=str(datetime.datetime.now().today()).replace(":"," ")+".jpg"
    image.save(time)

def open_webcam():
    global label1
    global frame
    global cap
    global success
    global numpy_frame
    global button_forward
    global button_back
    global frame3
    global capture_button
    
    button_back = tk.Button(window, text="<<", command=back, state=tk.DISABLED,bg="#cfd3e6")
    button_forward = tk.Button(window, text=">>", command=forward,bg="#cfd3e6")
    
    button_back.grid(row=9, column=1)
    button_forward.grid(row=9, column=3)    
    
    if button_forward:
        button_forward.config(state=tk.DISABLED)
    else:
        pass
    if button_back:
        button_back.config(state=tk.DISABLED)
    else:
        pass
    
    if label1 is not None:
        #frame3.grid_forget() # Remove the existing label
        label1.grid_forget()
        
    #frame3.grid(row=0, column=1, columnspan=3, rowspan=8)
    label1=Label(frame3,bg="SystemButtonFace")
    label1.grid(in_=frame3, row=0,column=1,columnspan=3)
        
    # Create the capture button and hide it initially
    capture_button = Button(frame3, text="Capture Image", command=capture_image, state="disabled",bg="#cfd3e6")
    capture_button.grid(in_=frame3, row=1, column=1, columnspan=3)
    
    # Open the video file
    cap = cv2.VideoCapture(0)

    # Loop through the video frames
    while cap.isOpened():
        # Read a frame from the video
        success, frame = cap.read()

        if success:
            
            frame=cv2.flip(frame,1)
            
            # Run YOLOv8 inference on the frame
            result_frame=web_processing(frame)
            
            # Visualize the results on the frame
            annotated_frame = result_frame[0].plot()
            
            numpy_frame=annotated_frame[:, :, ::-1] #convert from RGB to BGR            
            pil_frame=ImageTk.PhotoImage(Image.fromarray(numpy_frame))
            label1['image']=pil_frame
            
            frame3.update()
            
            # Enable the capture button when the webcam is on
            capture_button.config(state="normal")
            
            # Break the loop if 'q' is pressed
            #if cv2.waitKey(1) & 0xFF == ord("q"):
             #   break   
        else:
            # Break the loop if the end of the video is reached
            break
    
    # Release the video capture object and close the display window
    cap.release()
    cv2.destroyAllWindows()
    capture_button.grid_forget()
    
def catch_classindex(class_index=None):
    global _class_index
    _class_index=class_index
    return _class_index

def web_processing(frame=None):
    _cam_index=_class_index
    result_frame = detect(frame,_cam_index)
    return result_frame
    
def detect(image, class_index=None):
    model = YOLO('best.pt')
    if class_index is not None and class_index < len(classes):
        selected_class = classes[class_index]
        result = model.predict(image, classes=classes.index(selected_class), verbose=False)
    else:
        result = model(image, verbose=False)
    return result

def process_image(class_index):
    
    selected_class = classes[class_index]
    if success==True:
        webcam_index=class_index
        return catch_classindex(webcam_index)
    else:  
        for i, image_path in enumerate(filepaths):
            if image_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                img = cv2.imread(image_path)
                result = detect(img, class_index)
                annotated_image = result[0].plot()
                numpy_image = annotated_image.astype(np.uint8)
                numpy_image = numpy_image[:, :, ::-1]
                pil_image = Image.fromarray(numpy_image)
                pil_image = pil_image.resize((640, 640))
                uploaded_file = ImageTk.PhotoImage(pil_image)
                file_list[i] = uploaded_file
        file_display(current_file_index)
        
def all_class_process(class_index):
    #selected_class = classes[class_index]
    if success==True:
        webcam_index=class_index
        return catch_classindex(webcam_index)
    else:  
        for i, image_path in enumerate(filepaths):
            if image_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                img = cv2.imread(image_path)
                result = detect(img, class_index)
                annotated_image = result[0].plot()
                numpy_image = annotated_image.astype(np.uint8)
                numpy_image = numpy_image[:, :, ::-1]
                pil_image = Image.fromarray(numpy_image)
                pil_image = pil_image.resize((640, 640))
                uploaded_file = ImageTk.PhotoImage(pil_image)
                file_list[i] = uploaded_file
        file_display(current_file_index)

# Create the tkinter window
window = tk.Tk()
window.title('Construction Site Safety Instruction')
window.configure(bg="#2E2E47")
window.iconbitmap('safety-icon.ico')

frame2 = LabelFrame(window,text='control Frame',fg="#cfd3e6",bg="#2E2E47",padx=10,pady=10)
frame2.grid(sticky= "N")

frame1=LabelFrame(window,text='Control Detection',fg="#cfd3e6",bg="#2E2E47", padx=10,pady=10)
frame1.grid(row=1, column=0,sticky= "N")

frame3 = LabelFrame(window,text='Main Frame',fg="#cfd3e6",bg="#2E2E47", width=640, height=640)
frame3.grid(row=0, column=1, columnspan=3, rowspan=8)

# Create the buttons
upload_button = tk.Button(frame2, text="Upload Images", command=upload_files, height=1, width=15,bg="#cfd3e6")
upload_button.grid()

webcam_button = tk.Button(frame2, text="Open Webcam", command=open_webcam, height=1, width=15,bg="#cfd3e6")
webcam_button.grid()

button_exit = tk.Button(window, text="Exit Program", command=window.destroy,bg="#cfd3e6")
button_exit.grid(row=9, column=2)

# Create the buttons for each class
for i in range(len(classes)):
    class_name = classes[i]
    button = tk.Button(frame1, text=class_name, command=lambda class_index=i: process_image(class_index), height=1, width=15,bg="#cfd3e6")
    button.grid(row=i+1, rowspan=1)
button = tk.Button(frame1, text="All Classes", command=lambda class_index=None: all_class_process(class_index), height=1, width=15,bg="#cfd3e6")
button.grid(row=0, column=0)

# Run the tkinter event loop
window.mainloop()
    
cap.release()

