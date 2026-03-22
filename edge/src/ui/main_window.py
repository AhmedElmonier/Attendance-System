import tkinter as tk

class MainWindow(tk.Tk):
    def __init__(self, locale="en"):
        super().__init__()
        self.locale = locale
        self.title("Attendance Kiosk | كشك الحضور")
        self.geometry("800x600")
        
        # Configure layout direction based on locale
        self.layout_dir = 'right' if self.locale == 'ar' else 'left'
        self.bg_color = "#f8fafc"
        self.configure(bg=self.bg_color)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Header
        header_text = "يرجى النظر إلى الكاميرا" if self.locale == 'ar' else "Please look at the camera"
        header = tk.Label(self, text=header_text, font=("Arial", 24, "bold"), bg=self.bg_color)
        header.pack(pady=40)
        
        # Video Frame Placeholder
        self.video_frame = tk.Frame(self, width=640, height=480, bg="black")
        self.video_frame.pack(pady=20)
        
        # Status Label
        status_text = "في انتظار المسح..." if self.locale == 'ar' else "Waiting for scan..."
        self.status_label = tk.Label(self, text=status_text, font=("Arial", 16), bg=self.bg_color, fg="#64748b")
        self.status_label.pack(side=self.layout_dir, padx=40, pady=20)

    def update_status(self, text: str, color: str = "#64748b"):
        self.status_label.config(text=text, fg=color)

if __name__ == "__main__":
    app_ar = MainWindow(locale="ar")
    app_ar.mainloop()
