import cv2 
import os
import glob
import re
import numpy as np
import mediapipe as mp


def __get_saving_frames_duration( cap, saving_fps):
    """Returns the list of durations where to save the frames"""
    s=[]
    #get the clip duration by dividing number of frames by the number of frames by the number of frames per second
    clip_duration = cap.get(cv2.CAP_PROP_FRAME_COUNT)/ cap.get(cv2.CAP_PROP_FPS)
    #use np.arrange() to make floating-point steps
    for i in np.arange(0, clip_duration, 1/saving_fps):
        s.append(i)
    return s

def __video_splitter(file, resize, saving_fps):
    """Splits the video in frames and saves them in a folder"""
    #create folder
    if not os.path.isdir("./Video/input_frames"):
        os.mkdir("./Video/input_frames")

    #read file
    cap = cv2.VideoCapture(file)

    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    #get resize percentage
    dim_correction = max(width, height)
    dim_correction = 512/dim_correction #percentage

    #correction
    width_resized =  (width*dim_correction) if resize else width
    height_resized = (height*dim_correction) if resize else height

    #get fps
    original_fps = cap.get(cv2.CAP_PROP_FPS)

    saving_frames_per_second = min(original_fps, saving_fps)
    saving_frames_duration = __get_saving_frames_duration(cap, saving_frames_per_second)

    #start the loop
    frame_count = 0
    saving_count = 0
    while True:
        is_read, frame = cap.read()

        if is_read:
            #resize the frame
            frame = cv2.resize(frame, (int(width_resized), int(height_resized)), interpolation=cv2.INTER_AREA)
        #break if there are no more frames
        else:
            break

        #get the duration by dividing the frame count by the fps
        frame_duration = frame_count/original_fps
        try:
            #get the earliest duration to save
            closest_duration = saving_frames_duration[0]
        except IndexError:
            #the list is empty, all frames have been saved
            break
        if frame_duration >= closest_duration:
            #if the closest duration is less than the frame duration, save the frame
            cv2.imwrite(f"./Video/input_frames/frame{saving_count}.png", frame)
            print(f"Saving frame {saving_count}")
            saving_count += 1
            #remove the saved duration from the list
            try:
                saving_frames_duration.pop(0)
            except IndexError:
                pass
        #increase the frame count    
        frame_count += 1

def __crop_frame():
    """Crops the frame"""
    # For static images:
    if not os.path.isdir("./Video/cropped_frames"):
        os.mkdir("./Video/cropped_frames")


    # mediapipe face detection
    mp_face_detection = mp.solutions.face_detection
    
    # xmin, ymin
    bounding_box_points = []
    # width, height
    bounding_box_size = []
    #initialize face detection
    with mp_face_detection.FaceDetection(
            model_selection=1, 
            min_detection_confidence=0.5) as face_detection:

        frame_count = 0
        # loop through frames
        files = glob.glob('./Video/input_frames/*.png')
        #file order is not guaranteed, so sort them
        files = sorted(files, key=lambda x:float(re.findall("(\d+)",x)[0]))
        for filename in files:
            print ("Cropping: "+filename)
            image = cv2.imread(filename)

            # Convert the BGR image to RGB before processing with mediapipe.
            results = face_detection.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # skip if no face detected
            if not results.detections:
                continue
            annotated_image = image.copy()

            padding = 30 # 30 pixels of padding

            #Array nose points for arrival images
            
            # loop through detected faces and crop them out of the frame and save them to a folder 
            for detection in results.detections:


                #get bounding box
                xmin = int(detection.location_data.relative_bounding_box.xmin*annotated_image.shape[1])
                width = int(detection.location_data.relative_bounding_box.width*annotated_image.shape[1])
                ymin = int(detection.location_data.relative_bounding_box.ymin*annotated_image.shape[0])
                height = int(detection.location_data.relative_bounding_box.height*annotated_image.shape[0])


                (h, w) = annotated_image.shape[:2]


                if ymin+height+padding > w or xmin+width+padding > h or xmin-padding < 0 or ymin-padding < 0:
                    padding = 0

                cropped_img = annotated_image[ymin-padding:ymin+height+padding, xmin-padding:xmin+width+padding]

                #save cropped image
                if cropped_img.shape[0] > 0 and cropped_img.shape[1] > 0:
                    cropped_img = cv2.resize(cropped_img, (512, 512), interpolation=cv2.INTER_AREA)
                    print(cropped_img.shape)
                    cv2.imwrite(f'./Video/cropped_frames/frame{frame_count}.png', cropped_img)
                    frame_count += 1


                #get coner bbox points
                bounding_box_points.append((xmin-padding, ymin-padding))
                bounding_box_size.append((width+padding , height+padding))

def detect_blurr(threshold):

    if not os.path.isdir("./Video/croppedTest_frames"):
        os.mkdir("./Video/croppedTest_frames")

    frame_count = 0
    # loop through frames
    files = glob.glob('./Video/cropped_frames/*.png')
    #file order is not guaranteed, so sort them
    files = sorted(files, key=lambda x:float(re.findall("(\d+)",x)[0]))
    for filename in files:
        print ("Detetcting: "+filename)
        image = cv2.imread(filename)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        fm = cv2.Laplacian(gray, cv2.CV_64F).var()
        text = "Not Blurry"

        if fm < threshold:
            text = "Blurry"
        else:
            cv2.imwrite(f'./Video/croppedTest_frames/frame{frame_count}.png', image)
            frame_count += 1

def correct_text():
    # loop through frames
    files = glob.glob('./Video/croppedTest_frames/*.txt')
    #file order is not guaranteed, so sort them
    files = sorted(files, key=lambda x:float(re.findall("(\d+)",x)[0]))
    text = "Francesco Santini "
    for filename in files:
        print ("Correcting: "+filename)
        with open(filename, 'r') as original: data = original.read()
        with open(filename, 'w') as modified: modified.write(text + data)

def maxSize():
    files = glob.glob('./Video/croppedTest_frames/*.png')
    #file order is not guaranteed, so sort them
    files = sorted(files, key=lambda x:float(re.findall("(\d+)",x)[0]))
    max = 0
    for filename in files:
        img = cv2.imread(filename)
        if (max < img.shape[0]):
            max = img.shape[0]
            print(max)
            
    print(max)


        

            
"""print("Starting video processing")
__video_splitter("Video/input.mov", False, 30)"""
#__crop_frame()
#detect_blurr(40)
#maxSize()
correct_text()
