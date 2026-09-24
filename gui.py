import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import cv2
import customtkinter as ctk

import image as ops

ctk.set_appearance_mode("Dark")

class ROIDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("ROI Selection")
        self.geometry("300x280")
        self.configure(fg_color="#14141F")
        
        self.transient(parent)
        self.grab_set()
        
        self.result = None

        labels = ["Start Row (y1):", "End Row (y2):", "Start Column (x1):", "End Column (x2):"]
        self.entries = []

        for i, text in enumerate(labels):
            lbl = ctk.CTkLabel(self, text=text, text_color="#A0A0B8", font=("Segoe UI", 12))
            lbl.grid(row=i, column=0, padx=15, pady=8, sticky="w")
            
            entry = ctk.CTkEntry(self, width=120, fg_color="#0A0A0E", border_color="#6C5CE7")
            entry.grid(row=i, column=1, padx=15, pady=8)
            self.entries.append(entry)

        self.btn_submit = ctk.CTkButton(
            self, text="Apply ROI", fg_color="#00B894", text_color="#0A0A0E", font=("Segoe UI", 12, "bold"),
            command=self.validate_and_submit
        )
        self.btn_submit.grid(row=4, column=0, columnspan=2, pady=15)
        self.entries[0].focus_set()

    def validate_and_submit(self):
        try:
            values = [int(entry.get().strip()) for entry in self.entries]
            if any(v < 0 for v in values):
                messagebox.showerror("Error", "All values must be positive integers!", parent=self)
                return
            self.result = tuple(values)
            self.destroy()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid integers in all fields!", parent=self)


class UniqueImageApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AuraVision - Advanced Image Suite")
        self.root.geometry("1450x880")
        self.root.configure(fg_color="#0A0A0E")

        self.original = None
        self.processed = None
        self.image_path = None

        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        self.top_frame = ctk.CTkFrame(root, height=70, fg_color="#14141F", corner_radius=12)
        self.top_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=15, pady=(15, 5))

        ctk.CTkButton(
            self.top_frame, text="OPEN IMAGE", command=self.open_image,
            fg_color="#6C5CE7"
        ).pack(side=tk.LEFT, padx=15, pady=15)

        ctk.CTkButton(
            self.top_frame, text="RUN PROCESS", command=self.apply_operations,
            fg_color="#00B894", text_color="#0A0A0E"
        ).pack(side=tk.LEFT, padx=5, pady=15)

        ctk.CTkButton(
            self.top_frame, text="EXPORT", command=self.save_image,
            fg_color="#E17055"
        ).pack(side=tk.LEFT, padx=5, pady=15)

        self.info_label = ctk.CTkLabel(
            self.top_frame, text="System Ready",
            font=("Segoe UI Mono", 12), text_color="#A0A0B8"
        )
        self.info_label.pack(side=tk.RIGHT, padx=20, pady=15)

        self.sidebar_frame = ctk.CTkScrollableFrame(
            root, width=260, label_text="OPERATIONS LAB",
            fg_color="#14141F", label_text_color="#6C5CE7"
        )
        self.sidebar_frame.grid(row=1, column=0, sticky="nsew", padx=(15, 5), pady=10)

        self.operations = [
            "Grayscale", "Red Channel", "Green Channel", "Blue Channel",
            "ROI", "Histogram", "Gamma Correction", "Min-Max Stretching",
            "Laplacian", "Salt and Pepper", "Outlier Method",
            "Sobel", "Prewitt", "Dilation", "Erosion", "Opening", "Closing"
        ]

        self.vars = {}
        for op in self.operations:
            var = tk.BooleanVar()
            self.vars[op] = var
            ctk.CTkCheckBox(
                self.sidebar_frame, text=op, variable=var,
                fg_color="#6C5CE7"
            ).pack(anchor="w", padx=15, pady=8)

        self.images_frame = ctk.CTkFrame(root, fg_color="#14141F", corner_radius=12)
        self.images_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 15), pady=10)

        self.images_frame.grid_columnconfigure(0, weight=1)
        self.images_frame.grid_columnconfigure(1, weight=1)
        self.images_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self.images_frame, text="UPLOAD IMAGE",
            font=("Segoe UI", 13, "bold")
        ).grid(row=0, column=0, pady=(15, 5))

        ctk.CTkLabel(
            self.images_frame, text="OUTPUT MONITOR",
            font=("Segoe UI", 13, "bold"), text_color="#00B894"
        ).grid(row=0, column=1, pady=(15, 5))

        self.original_panel = ctk.CTkLabel(
            self.images_frame, text="[ AWAITING IMAGE INPUT ]"
        )
        self.original_panel.grid(row=1, column=0, padx=15, pady=(5, 15), sticky="nsew")

        self.processed_panel = ctk.CTkLabel(
            self.images_frame, text="[ PROCESSED STREAM ]"
        )
        self.processed_panel.grid(row=1, column=1, padx=15, pady=(5, 15), sticky="nsew")

    
    def open_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if not path:
            return

        self.image_path = path
        self.original = cv2.imread(path)
        self.processed = self.original.copy()

        h, w = ops.get_info(self.original)
        
        self.info_label.configure(
            text=f"RES: {w}x{h} px  |  STATUS: ACTIVE",
            text_color="#00B894"
        )

        self.show_image(self.original, self.original_panel)
        self.show_image(self.processed, self.processed_panel)
    
    
    def show_image(self, img, panel):
        if img is None:
            return

        if len(img.shape) == 2:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        else:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        pil_img = Image.fromarray(img_rgb)
        pil_img.thumbnail((600, 600))

        tk_img = ImageTk.PhotoImage(pil_img)
        panel.configure(image=tk_img, text="")
        panel.image = tk_img
        

    def get_roi_values(self):
        dialog = ROIDialog(self.root)
        self.root.wait_window(dialog) 
        return dialog.result
    
    

    def apply_operations(self):
        if self.original is None:
            messagebox.showwarning("System Alert", "No source feed detected. Load an image.")
            return

        img = self.original.copy()

        for op_name, var in self.vars.items():
            if not var.get():
                continue

            if op_name == "Grayscale":
                img = ops.to_gray(img)
            elif op_name == "Red Channel":
                img = ops.extract_channel(img, "red")
            elif op_name == "Green Channel":
                img = ops.extract_channel(img, "green")
            elif op_name == "Blue Channel":
                img = ops.extract_channel(img, "blue")
            elif op_name == "ROI":
                values = self.get_roi_values()
                if values is not None:
                    img = ops.roi_range(img, *values)
            elif op_name == "Histogram":
                img = ops.histogram_image(img)
            elif op_name == "Gamma Correction":
                img = ops.gamma_correction(img)
            elif op_name == "Min-Max Stretching":
                img = ops.min_max_stretch(img)
            elif op_name == "Laplacian":
                img = ops.laplacian_filter(img)
            elif op_name == "Salt and Pepper":
                img = ops.remove_salt_pepper(img)
            elif op_name == "Outlier Method":
                img = ops.outlier_method(img)
            elif op_name == "Sobel":
                img = ops.sobel_filter(img)
            elif op_name == "Prewitt":
                img = ops.prewitt_filter(img)
            elif op_name == "Dilation":
                img = ops.dilation(img)
            elif op_name == "Erosion":
                img = ops.erosion(img)
            elif op_name == "Opening":
                img = ops.opening(img)
            elif op_name == "Closing":
                img = ops.closing(img)

        self.processed = img
        self.show_image(self.processed, self.processed_panel)

    def save_image(self):
        if self.processed is None:
            messagebox.showwarning("System Alert", "Output matrix is empty. Process an image first.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Direct", "*.png"), ("JPEG Compressed", "*.jpg")]
        )
        if path:
            cv2.imwrite(path, self.processed)
            messagebox.showinfo("Export Success", f"Saved to: {path}")


if __name__ == "__main__":
    root = ctk.CTk()
    app = UniqueImageApp(root)
    root.mainloop()
