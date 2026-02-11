import tkinter as tk
from tkinter import ttk

class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        bg_color = kwargs.pop("bg", "#1e293b")
        super().__init__(container, *args, **kwargs)
        self.configure(bg=bg_color)
        
        self.canvas = tk.Canvas(self, bg=bg_color, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=bg_color)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.window_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Configure canvas to resize the scrollable frame to fill width
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.window_id, width=e.width))

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Global binding for mousewheel (Windows, Mac, Linux)
        self.bind_all("<MouseWheel>", self._on_mousewheel)
        self.bind_all("<Button-4>", self._on_mousewheel)
        self.bind_all("<Button-5>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        if not self.canvas.winfo_exists():
            return
            
        # Check if mouse is over this widget or its children
        x, y = self.canvas.winfo_pointerxy()
        target = self.canvas.winfo_containing(x, y)
        
        is_ours = False
        curr = target
        while curr:
            if curr == self:
                is_ours = True
                break
            curr = curr.master
            
        if is_ours:
            # Scroll speed: 10 units per tick for a "fluid" feel
            if event.num == 4 or (event.delta and event.delta > 0):
                self.canvas.yview_scroll(-10, "units")
            elif event.num == 5 or (event.delta and event.delta < 0):
                self.canvas.yview_scroll(10, "units")

    def update_scroll(self):
        """Force update of scroll region."""
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        # Optional: ensure children propagate scroll to canvas
        # But usually bind_all is the culprit for leaks. 
        # By binding to canvas and making it large, we get better performance.
