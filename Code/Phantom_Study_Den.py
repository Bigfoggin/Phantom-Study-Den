import customtkinter as ctk
import math, fitz
from PIL import Image, ImageTk
from tkinter import filedialog
from ctypes import windll
try:
    windll.shcore.SetProcessDpiAwareness(1)
except:
    pass
RED, DARK_RED, BLACK, WHITE, GRAY = "#D31027", "#9E0B1C", "#000000", "#FFFFFF", "#808080"
class PhantomNotebook(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.width, self.height = self.winfo_screenwidth(), self.winfo_screenheight()
        self.overrideredirect(True)
        self.geometry(f"{self.width}x{self.height}+0+0")
        self.bind("<Escape>", lambda e: self.quit())
        self.state_mode, self.pdf_images, self.menu_items, self.back_button_data = "menu", [], [], None
        self.canvas = ctk.CTkCanvas(self, width=self.width, height=self.height, bg=RED, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.draw_background_stripes()
        self.rotation, self.star_size = 0, self.height * 1.5
        self.star_bg_id = self.canvas.create_polygon(self.get_star_coords(self.width, 0, self.star_size + 30, 0), fill=BLACK, tags="star")
        self.star_id = self.canvas.create_polygon(self.get_star_coords(self.width, 0, self.star_size, 0), fill=GRAY, outline=BLACK, width=8, tags="star")
        self.display_frame = ctk.CTkCanvas(self.canvas, bg="#1A1A1A", highlightthickness=4, highlightbackground=BLACK, width=self.width * 0.7, height=self.height * 0.85)
        self.display_frame_id = None
        self.draw_menu()
        self.animate()
    def get_star_coords(self, x, y, size, rot):
        pts = []
        for i in range(10):
            r = size if i % 2 == 0 else size * 0.48
            angle = math.radians(i * 36 + rot)
            pts.extend([x + r * math.cos(angle), y + r * math.sin(angle)])
        return pts
    def draw_background_stripes(self):
        for i in range(-self.height, self.width + self.height, 105):
            self.canvas.create_line(i, 0, i + self.height, self.height, fill=DARK_RED, width=25, tags="bg_stripe")
    def open_stats(self):
        self.state_mode = "viewing"
        self.display_frame.delete("all")
        self.hide_menu()
        self.display_frame_id = self.canvas.create_window(self.width / 2, self.height / 2, window=self.display_frame, anchor="center")
        f_width, margin_x, start_y = self.width * 0.7, 60, 100
        stats_data = [("KNOWLEDGE", 85), ("CHARM", 60), ("GUTS", 90), ("PROFICIENCY", 45), ("KINDNESS", 70)]
        self.stat_bars = []
        for i, (name, target_val) in enumerate(stats_data):
            y, bar_max_w = start_y + (i * 120), f_width - 150
            self.display_frame.create_text(margin_x, y + 5, text=name, font=("Impact", 42, "italic"), fill=WHITE, anchor="w")
            self.display_frame.create_polygon([margin_x, y+45, margin_x+bar_max_w, y+35, margin_x+bar_max_w-20, y+85, margin_x+10, y+95], fill="#333333", outline=BLACK, width=2)
            bar_id = self.display_frame.create_polygon([margin_x+5, y+50, margin_x+10, y+45, margin_x+5, y+80, margin_x+10, y+90], fill=RED, tags="stat_bar")
            self.stat_bars.append({"id": bar_id, "current": 0, "target": target_val, "x": margin_x, "y": y, "max_w": bar_max_w})
        self.create_back_button()
        self.animate_stats_bars()
    def animate_stats_bars(self):
        if self.state_mode != "viewing": return
        finished = True
        for bar in self.stat_bars:
            if bar["current"] < bar["target"]:
                bar["current"] += 2
                finished = False
                w, mx, my = (bar["current"] / 100) * bar["max_w"], bar["x"], bar["y"]
                self.display_frame.coords(bar["id"], *[mx+5, my+50, mx+w, my+42, mx+w-15, my+82, mx+15, my+90])
        if not finished: self.after(10, self.animate_stats_bars)
    def open_pdf_logic(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path: self.load_pdf_content(file_path)
    def load_pdf_content(self, path):
        self.state_mode, self.pdf_images = "viewing", []
        self.display_frame.delete("all")
        self.hide_menu()
        self.display_frame_id = self.canvas.create_window(self.width / 2, self.height / 2, window=self.display_frame, anchor="center")
        doc, total_h = fitz.open(path), 40
        for page in doc:
            pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
            img = ImageTk.PhotoImage(Image.frombytes("RGB", [pix.width, pix.height], pix.samples))
            self.pdf_images.append(img)
            self.display_frame.create_image((self.width * 0.7) / 2, total_h, image=img, anchor="n")
            total_h += pix.height + 40
        self.display_frame.config(scrollregion=(0, 0, self.width * 0.7, total_h))
        self.display_frame.bind_all("<MouseWheel>", self.on_scroll)
        self.create_back_button()
    def on_scroll(self, event):
        if self.state_mode == "viewing": self.display_frame.yview_scroll(int(-1*(event.delta/120)), "units")
    def create_back_button(self):
        bsz, bx, by = int(self.height * 0.035), 25, 25
        shd = self.canvas.create_text(bx+6, by+6, text="< BACK", font=("Impact", bsz, "italic"), fill=WHITE, anchor="nw", tags="back_btn")
        txt = self.canvas.create_text(bx, by, text="< BACK", font=("Impact", bsz, "italic"), fill=BLACK, anchor="nw", tags="back_btn")
        self.back_button_data = {"text": txt, "shadow": shd, "x": bx, "y": by, "hover": 0.0, "active": False, "shd_off": 6}
        self.canvas.tag_bind("back_btn", "<Button-1>", lambda e: self.show_menu())
        self.canvas.tag_bind("back_btn", "<Enter>", lambda e: self.set_back_hover(True))
        self.canvas.tag_bind("back_btn", "<Leave>", lambda e: self.set_back_hover(False))
    def set_back_hover(self, val):
        if self.back_button_data: self.back_button_data["active"] = val
    def hide_menu(self):
        for item in self.menu_items:
            self.canvas.itemconfig(item["text"], state="hidden")
            self.canvas.itemconfig(item["shadow"], state="hidden")
    def show_menu(self):
        self.state_mode = "menu"
        if self.display_frame_id: self.canvas.delete(self.display_frame_id)
        self.canvas.delete("back_btn")
        self.back_button_data = None
        self.display_frame.unbind_all("<MouseWheel>")
        for item in self.menu_items:
            self.canvas.itemconfig(item["text"], state="normal")
            self.canvas.itemconfig(item["shadow"], state="normal")
    def draw_menu(self):
        commands = ["PDF", "SHEET", "MUSIC", "STATS", "SYSTEM"]
        for i, lbl in enumerate(commands):
            x, y, tag = self.width*0.10 + (i*self.width*0.035), self.height*0.20 + (i*self.height*0.14), f"item_{i}"
            shd = self.canvas.create_text(x+12, y+12, text=lbl, font=("Impact", int(self.height*0.08), "italic"), fill=WHITE, anchor="w", tags=tag)
            txt = self.canvas.create_text(x, y, text=lbl, font=("Impact", int(self.height*0.08), "italic"), fill=BLACK, anchor="w", tags=tag)
            self.menu_items.append({"text": txt, "shadow": shd, "x": x, "y": y, "hover": 0.0, "active": False, "shd_off": 12})
            self.canvas.tag_bind(tag, "<Enter>", lambda e, idx=i: self.set_hover(idx, True))
            self.canvas.tag_bind(tag, "<Leave>", lambda e, idx=i: self.set_hover(idx, False))
            if lbl == "PDF": self.canvas.tag_bind(tag, "<Button-1>", lambda e: self.open_pdf_logic())
            if lbl == "STATS": self.canvas.tag_bind(tag, "<Button-1>", lambda e: self.open_stats())
    def set_hover(self, idx, val):
        if self.state_mode == "menu": self.menu_items[idx]["active"] = val
    def animate(self):
        self.rotation += 0.20
        self.canvas.coords(self.star_bg_id, *self.get_star_coords(self.width, 0, self.star_size + 25, self.rotation))
        self.canvas.coords(self.star_id, *self.get_star_coords(self.width, 0, self.star_size, self.rotation))
        active_list = self.menu_items if self.state_mode == "menu" else ([self.back_button_data] if self.back_button_data else [])
        for item in active_list:
            target = 1.0 if item["active"] else 0.0
            item["hover"] += (target - item["hover"]) * 0.15
            sx, sy, off = item["hover"] * (self.width * 0.03), item["hover"] * -(self.height * 0.005), item["shd_off"]
            self.canvas.coords(item["shadow"], item["x"] + sx + off, item["y"] + sy + off)
            self.canvas.coords(item["text"], item["x"] + sx, item["y"] + sy)
            self.canvas.itemconfig(item["text"], fill=RED if item["hover"] > 0.5 else BLACK)
            self.canvas.itemconfig(item["shadow"], fill=BLACK if item["hover"] > 0.5 else WHITE)
        self.canvas.tag_lower("star")
        self.canvas.tag_lower("bg_stripe")
        self.after(16, self.animate)
if __name__ == "__main__":
    app = PhantomNotebook()
    app.mainloop()