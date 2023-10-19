# SCL_deepfake
Project from my bachelor's thesis: "Generating Deepfakes with Stable Diffusion, ControlNet and LoRA"
### The Pipeline
<p align="center">
  <img src="https://github.com/edoardotavassi/SCL_deepfake/blob/main/readme_elements/Info.png" width="350" title="Pipeline.">
</p>
We can see the entire pipeline used to create deepfakes from
a video source. First, the input video is decreased to 12 frames per second.
Then, for every frame, by using MediaPipe, we can extrapolate face locations
and their structure. Next, the structure created with Face Mesh is processed
to generate a mask for the latter application of the diffused image, while the locations detected by Face Detection are used to extract just the face. After
this, every cropped image is processed through Stable Diffusion with ControlNet
and LoRA.
This LoRA model was previously trained to the target face. Finally, every diffused image gets
applied to the corresponding input frame and then exported as a video.

### The Output
<p float="left" align="center">
<img src="https://github.com/edoardotavassi/SCL_deepfake/blob/main/readme_elements/input.png" width="350" title="Input Frame.">
<img src="https://github.com/edoardotavassi/SCL_deepfake/blob/main/readme_elements/final_frame.png" width="350" title="Output Frame.">
</p>
In these two images, we can observe how the software is capable of using SD, ControlNet, and LoRA to create a deepfake of my professor's face onto mine. Obviously, this process is repeated for each frame of the input video.

### GUI
<p align="center">
  <img src="https://github.com/edoardotavassi/SCL_deepfake/blob/main/readme_elements/generation-window.png" width="350" title="Pipeline.">
</p>
The GUI assists the user in interacting with the <a href="https://github.com/AUTOMATIC1111/stable-diffusion-webui">SD webui API</a> and <a href="https://github.com/bmaltais/kohya_ss">LoRA training</a>. Simultaneously, it provides all the essential processing features needed to create deepfakes.
