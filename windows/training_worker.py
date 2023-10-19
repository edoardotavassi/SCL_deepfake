from PyQt6.QtCore import (
    QObject,
    QRunnable,
    pyqtSignal,
    pyqtSlot,
)
import os
import sys
import cv2
import re
import numpy as np
import glob
import shutil
import mediapipe as mp
import json

class WorkerKilledException(Exception):
    """Raised when the worker thread is killed."""
    pass

class WorkerSignals(QObject):
    """Defines the signals available from a running worker thread."""

    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    progress = pyqtSignal(str, int)

class Worker(QRunnable):
    """Worker thread."""
    
    def __init__(self, video, training_name, model_name, blur_threshold):
        super().__init__()
        self.file = video
        self.basedir = os.path.dirname(video)
        self.training_name = training_name
        self.model_name = model_name
        self.blur_threshold = blur_threshold
        self.signals = WorkerSignals()
        self.is_killed = False
        
    def __get_saving_frames_duration(self):
        """Returns the list of durations where to save the frames"""
        s=[]
        #get the clip duration by dividing number of frames by the number of frames by the number of frames per second
        clip_duration = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)/ self.cap.get(cv2.CAP_PROP_FPS)
        #use np.arrange() to make floating-point steps
        for i in np.arange(0, clip_duration, 1/self.saving_fps):
            s.append(i)
        return s
    
    def __video_splitter(self):
        """Splits the video in frames and saves them in a folder"""
        #create folders
        dir_path = os.path.join(self.basedir,f"{self.model_name}_lora", "temp")
        if not os.path.isdir(os.path.join(self.basedir,f"{self.model_name}_lora")):
            os.makedirs(os.path.join(self.basedir,f"{self.model_name}_lora"))
            os.mkdir(os.path.join(self.basedir,f"{self.model_name}_lora","log"))
            os.mkdir(os.path.join(self.basedir,f"{self.model_name}_lora","model"))
            os.mkdir(dir_path)

        #read file
        self.cap = cv2.VideoCapture(self.file)

        self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

        self.total_frames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
        
        #get fps
        self.original_fps = self.cap.get(cv2.CAP_PROP_FPS)

        self.saving_fps = min(self.original_fps, 30)
        saving_frames_duration = self.__get_saving_frames_duration()

        #start the loop
        frame_count = 0
        saving_count = 0
        while True:
            self.check_exception()
            is_read, frame = self.cap.read()

            if is_read:
                #resize the frame
                frame = cv2.resize(frame, (int(self.width), int(self.height)), interpolation=cv2.INTER_AREA)
            #break if there are no more frames
            else:
                break

            #get the duration by dividing the frame count by the fps
            frame_duration = frame_count/self.original_fps
            try:
                #get the earliest duration to save
                closest_duration = saving_frames_duration[0]
            except IndexError:
                #the list is empty, all frames have been saved
                break
            if frame_duration >= closest_duration:
                #if the closest duration is less than the frame duration, save the frame
                cv2.imwrite(os.path.join(dir_path, f"frame{saving_count}.png"), frame)

                self.signals.progress.emit(
                    f"Splitting frame{saving_count}.png",
                    int((frame_count/self.total_frames)*100)
                    )
                saving_count += 1
                #remove the saved duration from the list
                try:
                    saving_frames_duration.pop(0)
                except IndexError:
                    pass
            #increase the frame count    
            frame_count += 1
        self.signals.progress.emit("",100)
        self.total_frames = saving_count

    def __crop_frame(self):
        """Crops the frame, detects blur and saves them in a folder"""
        self.signals.progress.emit("Cropping",0)
        #create folder
        dir_path = os.path.join(self.basedir,f"{self.model_name}_lora", "image",f"100_{self.model_name}")
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)


        # mediapipe face detection
        mp_face_detection = mp.solutions.face_detection
        
        # xmin, ymin
        self.bounding_box_points = []
        # width, height
        self.bounding_box_size = []
        #initialize face detection
        self.signals.progress.emit("Initializing face detection",0)
        with mp_face_detection.FaceDetection(
                model_selection=1, 
                min_detection_confidence=0.5) as face_detection:
            self.signals.progress.emit("Face detection initialized",0)

            frame_count = 0
            # loop through frames
            files = glob.glob(os.path.join(self.basedir,f"{self.model_name}_lora", "temp","*.png"))
            #file order is not guaranteed, so sort them
            files = sorted(files, key=lambda x:float(re.findall("(\d+)",x)[0]))
            for filename in files:
                self.check_exception()
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
                    cropped_img = annotated_image[ymin-padding:ymin+height+padding, xmin-padding:xmin+width+padding]

                #save cropped image
                cropped_img = cv2.resize(cropped_img, (512, 512), interpolation=cv2.INTER_AREA)

                #blur detection
                gray = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
                fm = cv2.Laplacian(gray, cv2.CV_64F).var()
                if fm < self.blur_threshold:
                    continue
                else:
                    cv2.imwrite(os.path.join(dir_path, f"frame{frame_count}.png"), cropped_img)

                    self.signals.progress.emit(
                        f"Cropping frame{frame_count}.png",
                        int((frame_count/self.total_frames)*100)
                        )
                
                    frame_count += 1

        shutil.rmtree(os.path.join(self.basedir,f"{self.model_name}_lora", "temp"))

        self.signals.progress.emit("",100)


    def __generate_json(self):
        """Generates the json file"""
        dict = {
            "pretrained_model_name_or_path": "runwayml/stable-diffusion-v1-5",
            "v2": False,
            "v_parameterization": False,
            "logging_dir": os.path.join(self.basedir,f"{self.model_name}_lora","log").replace("\\","/"),
            "train_data_dir": os.path.join(self.basedir,f"{self.model_name}_lora", "image",f"100_{self.model_name}").replace("\\","/"),
            "reg_data_dir": "",
            "output_dir": os.path.join(self.basedir,f"{self.model_name}_lora","model").replace("\\","/"),
            "max_resolution": "512,512",
            "learning_rate": "0.0001",
            "lr_scheduler": "constant",
            "lr_warmup": "0",
            "train_batch_size": 2,
            "epoch": "1",
            "save_every_n_epochs": "1",
            "mixed_precision": "fp16",
            "save_precision": "fp16",
            "seed": "1234",
            "num_cpu_threads_per_process": 2,
            "cache_latents": True,
            "caption_extension": ".txt",
            "enable_bucket": False,
            "gradient_checkpointing": False,
            "full_fp16": False,
            "no_token_padding": False,
            "stop_text_encoder_training": 0,
            "use_8bit_adam": True,
            "xformers": True,
            "save_model_as": "safetensors",
            "shuffle_caption": False,
            "save_state": False,
            "resume": "",
            "prior_loss_weight": 1.0,
            "text_encoder_lr": "5e-5",
            "unet_lr": "0.0001",
            "network_dim": 128,
            "lora_network_weights": "",
            "color_aug": False,
            "flip_aug": False,
            "clip_skip": 2,
            "gradient_accumulation_steps": 1.0,
            "mem_eff_attn": False,
            "output_name": self.model_name,
            "model_list": "runwayml/stable-diffusion-v1-5",
            "max_token_length": "75",
            "max_train_epochs": "",
            "max_data_loader_n_workers": "1",
            "network_alpha": 128,
            "training_comment": "",
            "keep_tokens": "0",
            "lr_scheduler_num_cycles": "",
            "lr_scheduler_power": ""
        }

        # Serializing json
        json_object = json.dumps(dict, indent=4)

        with open(os.path.join(self.basedir,f"{self.model_name}_lora", "lora_settings.json"), "w") as outfile:
            outfile.write(json_object)
        


    @pyqtSlot()
    def run(self):
        """Initialise the runner function."""
        try:
            self.__video_splitter()
            self.__crop_frame()
            self.__generate_json()
        except WorkerKilledException:
            self.signals.progress.emit("Killed",0)
            self.signals.finished.emit()
        except:
            traceback = sys.exc_info()[2]
            self.signals.error.emit((sys.exc_info()[:2] + (traceback,)))
        else:
            self.signals.finished.emit()

    def check_exception(self):
        """Check for an exception."""
        if self.is_killed:
            raise WorkerKilledException
    
    def kill(self):
        """Kill the thread."""
        self.is_killed = True
