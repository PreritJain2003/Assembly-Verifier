README: Assembly Verification System
Introduction
The Assembly Verification System is a computer vision-based tool designed to verify the
assembly of components. It uses a camera to capture images and compares them against
predefined templates to ensure each step of the assembly process is correctly executed. The
system is implemented using Python, OpenCV, and Tkinter.
Prerequisites
1. Hardware:
o Raspberry Pi 4 Model B (or a compatible computer)
o Raspberry Pi High Quality Camera (or a compatible USB camera)
o LED ring light (optional, for better image quality)
o Stable power supply
2. Software:
o Python 3.x
o OpenCV
o NumPy
o Tkinter
o PIL (Pillow)
Installation
1. Install Python: Ensure you have Python 3.x installed on your system. You can
download it from the official Python website.
2. Install Required Libraries: Open a terminal or command prompt and run the
following commands to install the required libraries:
Bash
Copy code
pip install opencv-python-headless numpy pillow
Running the Program
1. Download the Code: Download the PenAssemblyVerifier.py file from the
repository or copy the provided code into a new Python file named
PenAssemblyVerifier.py.
2. Prepare the Template Images: Place your template images (e.g., ink1.jpg,
body1.jpg, backcap1.jpg, pen1.jpg) in the same directory as the
PenAssemblyVerifier.py file.
3. Run the Program: Open a terminal or command prompt, navigate to the directory
containing PenAssemblyVerifier.py, and run the following command:
bash
Copy code
python PenAssemblyVerifier.py
Customization
To customize the program for verifying a different assembly process, you need to modify
specific parts of the code to update the steps, template images, and countdown times. Follow
these steps:
1. Step Names, Template Images, and Countdown Times:
o Open PenAssemblyVerifier.py in a text editor.
o Locate the self.steps list in the __init__ method (around line 12).
o Update the step names, template image filenames, and countdown times as
needed.
# Line 12
self.steps = [
 ('STEP 1 - Ink', 'ink1.jpg', 5),
 ('STEP 2 - Body', 'body1.jpg', 5),
 ('STEP 3 - Back Cap', 'backcap1.jpg', 7),
 ('STEP 4 - Final Pen', 'pen1.jpg', 4)
]
2. Verification Threshold:
o Locate the self.threshold variable in the __init__ method (around line 7).
o Update the threshold value if needed. The default is set to 0.8.
# Line 7
self.threshold = threshold
3. Template Matching Method:
o The template matching logic is implemented in the template_match method
(around line 195).
o If you need to customize the matching process, you can modify this method
accordingly.
# Line 195
def template_match(self, template_path, image):
 template = cv2.imread(template_path, 0)
 template = cv2.GaussianBlur(template, (5, 5), 0)
 image = cv2.GaussianBlur(image, (5, 5), 0)
 found = None
 for scale in np.linspace(0.5, 1.5, 30)[::-1]:
 resized = cv2.resize(template, (int(template.shape[1] *
scale), int(template.shape[0] * scale)))
 if resized.shape[0] > image.shape[0] or resized.shape[1] >
image.shape[1]:
 continue
 result = cv2.matchTemplate(image, resized,
cv2.TM_CCOEFF_NORMED)
 min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
 if found is None or max_val > found[0]:
 found = (max_val, max_loc, scale)
 if found is None:
 return False, 0.0
 max_val, max_loc, scale = found
 return max_val >= self.threshold, max_val
Conclusion
The Assembly Verification System provides a flexible framework for verifying assembly
processes using computer vision. By following the instructions above, you can customize and
run the program to suit different assembly verification needs.
