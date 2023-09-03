from PyQt6.QtCore import (
    QObject,
    QRunnable,
    pyqtSignal,
    pyqtSlot,
)


import os
from PIL import Image, PngImagePlugin
import requests
import io
import glob
import time
import cv2
import re
import threading
import base64
import pickle as pkl

from .util import generate_payload

class WorkerKilledException(Exception):
    """Raised when the worker thread is killed."""
    pass

class WorkerSignals(QObject):
    """Defines the signals available from a running worker thread."""

    finished_image = pyqtSignal()
    finished_batch = pyqtSignal()
    error = pyqtSignal(tuple)
    application_signal = pyqtSignal()
    progress_image = pyqtSignal(str, int)
    progress_batch = pyqtSignal(str, int) 

class Worker(QRunnable):
    """Worker thread to process image"""

    def __init__(self, frame_number=0, prompt="", negative_prompt="",steps=12, seed=-1, denoise=0.3, cfg=7, single_frame_flag=True):
        super().__init__()
        self.url = "http://127.0.0.1:7860" #server url
        self.signals = WorkerSignals()
        self.basedir = os.path.dirname(os.path.abspath(__file__))
        self.is_killed = False

        self.frame_number = frame_number
        self.prompt = prompt
        self.negative_prompt = negative_prompt
        self.steps = steps
        self.seed = seed
        self.denoise = denoise
        self.cfg = cfg
        self.single_frame_flag = single_frame_flag
        
        self.done = False

        #load the bounding box size of each frame
        with open(os.path.join(self.basedir,"..", "VideoFiles", "size.pkl"), "rb") as f:
            self.bounding_box_size= pkl.load(f)
        
        with open(os.path.join(self.basedir,"..", "VideoFiles", "points.pkl"), "rb") as f:
            self.bounding_box_points= pkl.load(f)

        self.signals.progress_image.emit("",0)

    def progress_check(self):
        while True:
            if self.done:
                break

            try:
                progress = requests.get(url=f'{self.url}/sdapi/v1/progress')
                self.signals.progress_image.emit(f"frame{self.frame_number}.png", int(progress.json()['progress']*100))
                time.sleep(0.5)
            except:
                pass
    
    def single_frame(self):
        """Call Server to test single frame"""

        payload = generate_payload(
            file=os.path.join(self.basedir, "..", "VideoFiles", "cropped_frames", f"frame{self.frame_number}.png"), 
            prompt=self.prompt, 
            negative_prompt=self.negative_prompt,
            steps=self.steps,
            seed=self.seed,
            denoising_strength=self.denoise, 
            cfg_scale=self.cfg
            )
    
        
        #start the progress bar animation
        t = threading.Thread(target=self.progress_check)
        t.start()
        
        response = requests.post(url=f'{self.url}/controlnet/img2img', json=payload)
        
        #stop the progress bar animation
        self.done = True
        self.signals.progress_image.emit("", 100)

        r = response.json()

        i = r['images'][0]
        image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))

        png_payload = {
            "image": "data:image/png;base64," + i
        }
        response2 = requests.post(url=f'{self.url}/sdapi/v1/png-info', json=png_payload)

        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("parameters", response2.json().get("info"))

        #gets the bounding box size of a cropped image
        w, h  = self.bounding_box_size[self.frame_number]
        #resize the image to the bounding box size due to the SD API cropping the image
        image = image.resize((w+30, h+30), Image.ANTIALIAS)

        image.save(os.path.join(self.basedir, "..", "VideoFiles", "temp.png"), pnginfo=pnginfo)
        self.signals.progress_image.emit("", 100)


    def batch_process(self):
        """Process all the frames"""
        self.signals.progress_batch.emit("", 0)
        
        if not os.path.isdir(os.path.join(self.basedir, "..", "VideoFiles", "output_frames")):
            os.makedirs(os.path.join(self.basedir, "..", "VideoFiles", "output_frames"))

        self.frame_number = 0

        files = glob.glob(os.path.join(self.basedir, "..", "VideoFiles", "cropped_frames", "*.png"))
        files = sorted(files, key=lambda x:float(re.findall("(\d+)",x)[0]))

        for filename in files:
            self.check_exception()
            self.done = False
            self.signals.progress_image.emit(f"frame{self.frame_number}.png", 0)

            payload = generate_payload(
                file=filename, 
                prompt=self.prompt, 
                negative_prompt=self.negative_prompt,
                steps=self.steps,
                seed=self.seed,
                denoising_strength=self.denoise, 
                cfg_scale=self.cfg
                )
            
            #start the progress bar animation
            t = threading.Thread(target=self.progress_check)
            t.start()
    
            response = requests.post(url=f'{self.url}/controlnet/img2img', json=payload)

            r = response.json()
            
            i = r['images'][0]
            image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))

            png_payload = {
                "image": "data:image/png;base64," + i
            }
            response2 = requests.post(url=f'{self.url}/sdapi/v1/png-info', json=png_payload)

            pnginfo = PngImagePlugin.PngInfo()
            pnginfo.add_text("parameters", response2.json().get("info"))

            #gets the bounding box size of a cropped image
            w, h  = self.bounding_box_size[self.frame_number]
            #resize the image to the bounding box size due to the SD API cropping the image
            image = image.resize((w+30, h+30), Image.ANTIALIAS)
           

            image.save(os.path.join(self.basedir, "..", "videoFiles", "temp.png"), pnginfo=pnginfo)
            self.signals.progress_image.emit(f"frame{self.frame_number}.png", 100)
            self.signals.finished_image.emit()

            image.save(os.path.join(self.basedir, "..", "VideoFiles", "output_frames", f"frame{self.frame_number}.png"), pnginfo=pnginfo)
            self.signals.progress_batch.emit("", int((self.frame_number/len(files))*100))
            self.frame_number += 1

            self.done = True
        
        self.signals.progress_batch.emit("", 100)

    def apply_latent_image(self):
        """Apply latent image to the initial frame"""
        self.signals.application_signal.emit()
        self.signals.progress_batch.emit("", 0)
        
        # For static images:
        if not os.path.isdir(os.path.join(self.basedir, "..", "VideoFiles", "final_frames")):
            os.makedirs(os.path.join(self.basedir, "..", "VideoFiles", "final_frames"))

        self.frame_number = 0
        # loop through frames
        files = glob.glob(os.path.join(self.basedir, "..", "VideoFiles", "output_frames", "*.png"))
        #file order is not guaranteed, so sort them
        files = sorted(files, key=lambda x:float(re.findall("(\d+)",x)[0]))
        for filename in files:
            self.check_exception()

            self.signals.progress_image.emit(f"frame{self.frame_number}.png", 0)
            
            image = Image.open(filename)
            output_image = Image.open(os.path.join(self.basedir, "..", "VideoFiles", "input_frames", f"frame{self.frame_number}.png"))
            mask_image = Image.open(os.path.join(self.basedir, "..", "VideoFiles", "mask_frames", f"frame{self.frame_number}.png")).convert('L')

            self.signals.progress_image.emit(f"frame{self.frame_number}.png", 50)
 
            #paste image
            output_image.paste(image, self.bounding_box_points[self.frame_number], mask_image)
      
            #save cropped image
            output_image.save(os.path.join(self.basedir, "..", "VideoFiles", "final_frames",f'frame{self.frame_number}.png'))
            output_image.save(os.path.join(self.basedir, "..", "VideoFiles",'temp.png'))

            self.signals.progress_image.emit(f"frame{self.frame_number}.png", 100)
            self.signals.finished_image.emit()
            self.signals.progress_batch.emit(f"frame{self.frame_number}.png", int((self.frame_number/len(files))*100))

            self.frame_number += 1
        
        self.signals.progress_batch.emit("", 100)

    def generate_video(self):
        """Generate the video from the frames"""
        self.signals.progress_batch.emit("", 0)
        img_array = []
        files = glob.glob(os.path.join(self.basedir, "..", "VideoFiles", "final_frames", '*.png'))
        files = sorted(files, key=lambda x:float(re.findall("(\d+)",x)[0]))
        self.frame_number = 0
        for filename in files:
            self.check_exception()
            self.signals.progress_batch.emit(f"frame{self.frame_number}.png",int((self.frame_number/len(files))*100) )
            
            img = cv2.imread(filename)
            height, width, layers = img.shape
            img_array.append(img)

        
        writer = cv2.VideoWriter(
            os.path.join(self.basedir, "..", "VideoFiles", 'output.avi'),
            cv2.VideoWriter_fourcc(*'DIVX'), 
            12, 
            (width,height)
            )
        
        self.signals.progress_batch.emit("", 0)

        for i in range(len(img_array)):
            self.check_exception()

            writer.write(img_array[i])

            self.signals.progress_batch.emit(f"frame{i}.png",int((i/len(files))*100) )
        writer.release()
        
            
    

    @pyqtSlot()
    def run(self):
        try:
            if self.single_frame_flag:
                self.single_frame()
                self.signals.finished_image.emit()
            else:
                self.batch_process()
                self.apply_latent_image()
                self.generate_video()
                self.signals.finished_batch.emit()
        except WorkerKilledException:
            self.signals.progress_image.emit("Killed",0)
            self.signals.progress_batch.emit("Killed",0)
        except Exception as e:
            self.signals.error.emit((type(e), e, None))

    def check_exception(self):
        """Check for an exception."""
        if self.is_killed:
            raise WorkerKilledException
    
    def kill(self):
        """Kill the thread."""
        self.is_killed = True
        self.done = True

