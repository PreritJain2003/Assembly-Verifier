import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class PenAssemblyVerifier:
    def __init__(self, root, threshold=0.7):
        self.root = root
        self.root.title("Pen Assembly Verification")
        self.root.configure(background='#2b2b2b')

        self.steps = [
            ('STEP 1 - Ink', 'ink1.jpg', 5),
            ('STEP 2 - Body', 'body1.jpg', 5),
            ('STEP 3 - Back Cap', 'backcap1.jpg', 7),
            ('STEP 4 - Final Pen', 'pen1.jpg', 4)
        ]
        self.current_step = 0
        self.verification_status = {}
        self.attempts = {step[0]: 0 for step in self.steps}
        self.threshold = threshold
        self.countdown_value = self.steps[self.current_step][2]

        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1080)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1920)
        self.camera_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.camera_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.root.geometry(f"{self.camera_width + 350}x{self.camera_height + 150}")

        self.setup_styles()
        self.create_main_frame()
        self.create_camera_frame()
        self.create_template_frame()

        self.update_camera_feed()
        self.root.after(1000, self.start_countdown)

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#2b2b2b')
        self.style.configure('TLabel', font=('Helvetica', 16), background='#2b2b2b', foreground='#ffffff')
        self.style.configure('TButton', font=('Helvetica', 16), background='#2b2b2b', foreground='#ffffff')
        self.style.configure('TProgressbar', thickness=30)
        self.style.configure('Retest.TButton', font=('Helvetica', 16, 'bold'), background='orange', foreground='#2b2b2b')

    def create_main_frame(self):
        self.main_frame = ttk.Frame(self.root, padding=10, style='TFrame')
        self.main_frame.pack(fill='both', expand=True)

    def create_camera_frame(self):
        self.camera_frame = ttk.Frame(self.main_frame, padding=5, style='TFrame')
        self.camera_frame.pack(side='left', fill='both', expand=True)

        self.instruction_label = ttk.Label(self.camera_frame, text="Starting in 5 seconds...", style='TLabel')
        self.instruction_label.pack(pady=10)

        self.camera_label = ttk.Label(self.camera_frame, background='#1e1e1e')
        self.camera_label.pack(pady=10)

    def create_template_frame(self):
        self.template_frame = ttk.Frame(self.main_frame, padding=5, style='TFrame')
        self.template_frame.pack(side='right', fill='both', expand=True)

        self.progress_label = ttk.Label(self.template_frame, text="Step 1 of 4: Ink", style='TLabel')
        self.progress_label.pack(pady=5)

        self.progress_bar = ttk.Progressbar(self.template_frame, length=400, mode='determinate', style='TProgressbar')
        self.progress_bar.pack(pady=10)
        self.progress_bar['maximum'] = len(self.steps)
        self.progress_bar['value'] = self.current_step

        self.create_result_boxes()
        self.create_buttons()

    def create_result_boxes(self):
        self.result_box_frame = ttk.Frame(self.template_frame, padding=5, style='TFrame', relief='ridge', borderwidth=2)
        self.result_box_frame.pack(pady=10, fill='x')

        self.result_box_label = ttk.Label(self.result_box_frame, text="Verification Results", style='TLabel')
        self.result_box_label.pack(pady=5)

        self.result_frame = ttk.Frame(self.result_box_frame, padding=5, style='TFrame')
        self.result_frame.pack(pady=10, fill='x')

        self.result_labels = {}

        self.final_result_frame = ttk.Frame(self.template_frame, padding=5, style='TFrame', relief='ridge', borderwidth=2)
        self.final_result_frame.pack(pady=10, fill='x')

        self.final_result_label = ttk.Label(self.final_result_frame, text="", font=('Helvetica', 18, 'bold'), background='#2b2b2b', foreground='#ffffff')
        self.final_result_label.pack(pady=10)

    def create_buttons(self):
        self.button_frame = ttk.Frame(self.template_frame, padding=5, style='TFrame')
        self.button_frame.pack(pady=20)

        self.retest_button = ttk.Button(self.button_frame, text="Retest", style='Retest.TButton', command=self.retest)
        self.retest_button.pack(side='left', padx=10)

        self.quit_button = ttk.Button(self.button_frame, text="Quit", style='Retest.TButton', command=self.end_program)
        self.quit_button.pack(side='left', padx=10)

    def start_countdown(self):
        if self.countdown_value > 0:
            self.instruction_label.config(text=f"Starting in {self.countdown_value} seconds...")
            self.countdown_value -= 1
            self.root.after(1000, self.start_countdown)
        else:
            self.instruction_label.config(text="Capturing images...")
            self.capture_image()

    def update_camera_feed(self):
        ret, frame = self.cap.read()
        if ret:
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.camera_label.imgtk = imgtk
            self.camera_label.configure(image=imgtk)
        self.root.after(10, self.update_camera_feed)

    def capture_image(self):
        ret, frame = self.cap.read()
        if ret:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            step_name, template_path, _ = self.steps[self.current_step]
            is_verified, confidence = self.template_match(template_path, gray_frame)
            self.verification_status[step_name] = {
                'verified': is_verified,
                'confidence': confidence
            }
            self.update_verification_results(step_name, is_verified, confidence)
            if is_verified:
                self.next_step()
            else:
                self.retry_step()

    def update_verification_results(self, step_name, is_verified, confidence):
        self.attempts[step_name] += 1
        result_text = 'Verified' if is_verified else 'Not Verified'
        result_color = '#00ff00' if is_verified else '#ff0000'

        if step_name in self.result_labels:
            self.result_labels[step_name].config(text=f"{step_name} ({self.attempts[step_name]}): {result_text} (Conf: {confidence:.2f})", foreground=result_color)
        else:
            result_frame = ttk.Frame(self.result_frame, padding=5, style='TFrame')
            result_frame.pack(fill='x')

            step_label = ttk.Label(result_frame, text=step_name, font=('Helvetica', 16), background='#2b2b2b', foreground='#ffffff')
            step_label.pack(side='left', padx=5)

            result_label = ttk.Label(result_frame, text=f"{result_text} (Conf: {confidence:.2f})", font=('Helvetica', 16), background='#2b2b2b', foreground=result_color)
            result_label.pack(side='left', padx=5)

            self.result_labels[step_name] = result_label

    def next_step(self):
        self.current_step += 1
        if self.current_step < len(self.steps):
            step_name, _, countdown_time = self.steps[self.current_step]
            self.progress_label.config(text=f"Step {self.current_step + 1} of {len(self.steps)}: {step_name}")
            self.progress_bar['value'] = self.current_step
            self.countdown_value = countdown_time
            self.root.after(1000, self.start_countdown_for_step)
        else:
            self.cap.release()
            self.display_final_results()

    def retry_step(self):
        self.instruction_label.config(text="Verification failed. Please adjust the pen and try again.")
        self.countdown_value = 5
        self.root.after(1000, self.start_countdown_for_step)

    def start_countdown_for_step(self):
        if self.countdown_value > 0:
            self.instruction_label.config(text=f"Capturing next step in {self.countdown_value} seconds...")
            self.countdown_value -= 1
            self.root.after(1000, self.start_countdown_for_step)
        else:
            self.capture_image()

    def template_match(self, template_path, image):
        template = cv2.imread(template_path, 0)
        template = cv2.GaussianBlur(template, (5, 5), 0)
        image = cv2.GaussianBlur(image, (5, 5), 0)

        found = None
        for scale in np.linspace(0.5, 1.5, 30)[::-1]:
            resized = cv2.resize(template, (int(template.shape[1] * scale), int(template.shape[0] * scale)))
            if resized.shape[0] > image.shape[0] or resized.shape[1] > image.shape[1]:
                continue

            result = cv2.matchTemplate(image, resized, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            if found is None or max_val > found[0]:
                found = (max_val, max_loc, scale)

        if found is None:
            return False, 0.0

        max_val, max_loc, scale = found
        return max_val >= self.threshold, max_val

    def display_final_results(self):
        if all(status['verified'] for status in self.verification_status.values()):
            final_result = "PEN SUCCESSFULLY MANUFACTURED!!"
            self.final_result_label.config(text=final_result, foreground='lightgreen')
        else:
            final_result = "PEN VERIFICATION FAILED!"
            self.final_result_label.config(text=final_result, foreground='red')

    def retest(self):
        self.current_step = 0
        self.verification_status = {}
        self.attempts = {step[0]: 0 for step in self.steps}
        self.cap.release()
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1080)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1920)
        self.camera_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.camera_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.countdown_value = self.steps[self.current_step][2]
        self.progress_bar['value'] = self.current_step
        for widget in self.result_frame.winfo_children():
            widget.destroy()
        self.result_labels = {}
        self.final_result_label.config(text="")
        self.instruction_label.config(text="Starting in 5 seconds...")
        self.root.after(1000, self.start_countdown)

    def end_program(self):
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PenAssemblyVerifier(root)
    root.mainloop()