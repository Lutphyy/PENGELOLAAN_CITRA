"""
==========================================================
Program Histogram Specification (Peningkatan Mutu Citra)
Pengolahan Citra Digital - Python (Tkinter GUI)
==========================================================
Mendukung citra BERWARNA (RGB) - proses per channel R, G, B
==========================================================
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import os


class HistogramApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Histogram Specification - Pengolahan Citra Digital")
        self.root.geometry("1400x880")
        self.root.configure(bg="#1e1e2e")
        self.root.minsize(1200, 750)

        # Data
        self.img_original = None       # numpy array RGB
        self.img_reference = None      # numpy array RGB
        self.img_equalized = None
        self.img_specified = None

        self._build_styles()
        self._build_ui()

    def _build_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"),
                         foreground="#cdd6f4", background="#1e1e2e")
        style.configure("Sub.TLabel", font=("Segoe UI", 10),
                         foreground="#a6adc8", background="#1e1e2e")
        style.configure("Main.TFrame", background="#1e1e2e")
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"),
                         foreground="#1e1e2e", background="#89b4fa",
                         padding=(14, 8))
        style.map("Accent.TButton", background=[('active', '#74c7ec')])
        style.configure("Status.TLabel", font=("Segoe UI", 9),
                         foreground="#a6adc8", background="#181825",
                         padding=(8, 4))

    def _build_ui(self):
        # Header
        header = ttk.Frame(self.root, style="Main.TFrame")
        header.pack(fill=tk.X, padx=20, pady=(15, 5))
        ttk.Label(header, text="📊 Histogram Specification (RGB)",
                  style="Title.TLabel").pack(side=tk.LEFT)
        ttk.Label(header, text="Peningkatan Mutu Citra Digital - Berwarna",
                  style="Sub.TLabel").pack(side=tk.LEFT, padx=(15, 0))

        # Toolbar
        toolbar = ttk.Frame(self.root, style="Main.TFrame")
        toolbar.pack(fill=tk.X, padx=20, pady=8)

        ttk.Button(toolbar, text="📂 Load Citra Asli",
                   style="Accent.TButton",
                   command=self.load_original).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(toolbar, text="📂 Load Citra Referensi",
                   style="Accent.TButton",
                   command=self.load_reference).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(toolbar, text="⚡ Histogram Equalization",
                   style="Accent.TButton",
                   command=self.do_equalization).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(toolbar, text="🎯 Histogram Specification",
                   style="Accent.TButton",
                   command=self.do_specification).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(toolbar, text="💾 Simpan Hasil",
                   style="Accent.TButton",
                   command=self.save_result).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(toolbar, text="🔄 Reset",
                   style="Accent.TButton",
                   command=self.reset_all).pack(side=tk.RIGHT)

        # Main content
        self.main_frame = ttk.Frame(self.root, style="Main.TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        self.fig = Figure(figsize=(14, 7), facecolor='#1e1e2e')
        self.fig.subplots_adjust(hspace=0.5, wspace=0.35)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Status bar
        self.status_var = tk.StringVar(value="Siap. Silakan load citra asli untuk memulai.")
        ttk.Label(self.root, textvariable=self.status_var,
                  style="Status.TLabel", anchor=tk.W).pack(fill=tk.X, side=tk.BOTTOM)

        self._show_welcome()

    def _show_welcome(self):
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.set_facecolor('#1e1e2e')
        ax.text(0.5, 0.55, "Histogram Specification (RGB)", fontsize=28,
                ha='center', va='center', color='#89b4fa', fontweight='bold',
                transform=ax.transAxes)
        ax.text(0.5, 0.40, "Mendukung Citra Berwarna (RGB)", fontsize=14,
                ha='center', va='center', color='#a6adc8', transform=ax.transAxes)
        ax.text(0.5, 0.28, "Klik 'Load Citra Asli' untuk memulai", fontsize=11,
                ha='center', va='center', color='#585b70', transform=ax.transAxes)
        ax.axis('off')
        self.canvas.draw()

    # ================ Helpers ================

    def _compute_cdf(self, channel):
        """Hitung CDF ternormalisasi dari satu channel."""
        hist, _ = np.histogram(channel.flatten(), bins=256, range=(0, 256))
        cdf = hist.cumsum()
        cdf_min = cdf[cdf > 0].min()
        cdf_normalized = (cdf - cdf_min) * 255 / (cdf.max() - cdf_min)
        return np.clip(cdf_normalized, 0, 255).astype(np.uint8), hist

    def _equalize_channel(self, channel):
        cdf, _ = self._compute_cdf(channel)
        return cdf[channel]

    def _specify_channel(self, src_channel, ref_channel):
        cdf_src, _ = self._compute_cdf(src_channel)
        cdf_ref, _ = self._compute_cdf(ref_channel)
        mapping = np.zeros(256, dtype=np.uint8)
        for i in range(256):
            diff = np.abs(cdf_ref.astype(int) - int(cdf_src[i]))
            mapping[i] = np.argmin(diff)
        return mapping[src_channel]

    def _ensure_rgb(self, img_array):
        """Pastikan array adalah RGB (3 channel)."""
        if len(img_array.shape) == 2:
            return np.stack([img_array]*3, axis=-1)
        if img_array.shape[2] == 4:  # RGBA
            return img_array[:, :, :3]
        return img_array

    def _plot_rgb_histogram(self, ax, img, title_text):
        """Plot histogram RGB overlay di satu axes."""
        colors = ['#ff6b6b', '#51cf66', '#339af0']  # R, G, B
        labels = ['Red', 'Green', 'Blue']
        for i, (c, lbl) in enumerate(zip(colors, labels)):
            ax.hist(img[:, :, i].flatten(), bins=256, range=(0, 256),
                    color=c, alpha=0.5, label=lbl, edgecolor='none')
        ax.set_title(title_text, color='#cdd6f4', fontsize=10, fontweight='bold')
        ax.legend(fontsize=7, loc='upper right',
                  facecolor='#313244', edgecolor='#45475a', labelcolor='#cdd6f4')
        ax.set_facecolor('#313244')
        ax.tick_params(colors='#a6adc8', labelsize=7)
        ax.set_xlabel("Intensitas", color='#a6adc8', fontsize=8)
        ax.set_ylabel("Frekuensi", color='#a6adc8', fontsize=8)
        for s in ax.spines.values():
            s.set_color('#45475a')

    # ================ File Loading ================

    def load_original(self):
        path = filedialog.askopenfilename(
            title="Pilih Citra Asli",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff")])
        if not path:
            return
        try:
            img = np.array(Image.open(path))
            self.img_original = self._ensure_rgb(img)
            self.img_equalized = None
            self.img_specified = None
            self.status_var.set(f"Citra asli dimuat: {os.path.basename(path)} "
                                f"({self.img_original.shape[1]}x{self.img_original.shape[0]}, RGB)")
            self._display_original()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuka citra:\n{e}")

    def load_reference(self):
        path = filedialog.askopenfilename(
            title="Pilih Citra Referensi",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff")])
        if not path:
            return
        try:
            img = np.array(Image.open(path))
            self.img_reference = self._ensure_rgb(img)
            self.status_var.set(f"Citra referensi dimuat: {os.path.basename(path)}")
            self._display_with_reference()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuka citra referensi:\n{e}")

    # ================ Processing ================

    def do_equalization(self):
        if self.img_original is None:
            messagebox.showwarning("Peringatan", "Silakan load citra asli terlebih dahulu!")
            return
        result = np.zeros_like(self.img_original)
        for ch in range(3):
            result[:, :, ch] = self._equalize_channel(self.img_original[:, :, ch])
        self.img_equalized = result
        self.status_var.set("Histogram Equalization selesai (RGB).")
        self._display_equalization_result()

    def do_specification(self):
        if self.img_original is None:
            messagebox.showwarning("Peringatan", "Silakan load citra asli terlebih dahulu!")
            return
        if self.img_reference is None:
            messagebox.showwarning("Peringatan", "Silakan load citra referensi terlebih dahulu!")
            return
        result = np.zeros_like(self.img_original)
        for ch in range(3):
            result[:, :, ch] = self._specify_channel(
                self.img_original[:, :, ch], self.img_reference[:, :, ch])
        self.img_specified = result
        self.status_var.set("Histogram Specification selesai (RGB).")
        self._display_specification_result()

    def save_result(self):
        img = self.img_specified if self.img_specified is not None else self.img_equalized
        if img is None:
            messagebox.showwarning("Peringatan", "Belum ada hasil untuk disimpan!")
            return
        path = filedialog.asksaveasfilename(
            title="Simpan Hasil", defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp")])
        if path:
            Image.fromarray(img).save(path)
            self.status_var.set(f"Hasil disimpan: {path}")

    # ================ Display ================

    def _display_original(self):
        self.fig.clear()
        ax1 = self.fig.add_subplot(1, 2, 1)
        ax1.imshow(self.img_original)
        ax1.set_title("Citra Asli (RGB)", color='#cdd6f4', fontsize=12, fontweight='bold')
        ax1.axis('off')

        ax2 = self.fig.add_subplot(1, 2, 2)
        self._plot_rgb_histogram(ax2, self.img_original, "Histogram Citra Asli (RGB)")
        self.canvas.draw()

    def _display_with_reference(self):
        if self.img_original is None:
            return
        self.fig.clear()

        ax1 = self.fig.add_subplot(2, 2, 1)
        ax1.imshow(self.img_original); ax1.set_title("Citra Asli", color='#cdd6f4', fontsize=10, fontweight='bold'); ax1.axis('off')

        ax2 = self.fig.add_subplot(2, 2, 2)
        self._plot_rgb_histogram(ax2, self.img_original, "Histogram Asli")

        ax3 = self.fig.add_subplot(2, 2, 3)
        ax3.imshow(self.img_reference); ax3.set_title("Citra Referensi", color='#cdd6f4', fontsize=10, fontweight='bold'); ax3.axis('off')

        ax4 = self.fig.add_subplot(2, 2, 4)
        self._plot_rgb_histogram(ax4, self.img_reference, "Histogram Referensi")
        self.canvas.draw()

    def _display_equalization_result(self):
        self.fig.clear()

        ax1 = self.fig.add_subplot(2, 2, 1)
        ax1.imshow(self.img_original); ax1.set_title("Citra Asli", color='#cdd6f4', fontsize=10, fontweight='bold'); ax1.axis('off')

        ax2 = self.fig.add_subplot(2, 2, 2)
        self._plot_rgb_histogram(ax2, self.img_original, "Histogram Asli")

        ax3 = self.fig.add_subplot(2, 2, 3)
        ax3.imshow(self.img_equalized); ax3.set_title("Hasil Equalization", color='#cdd6f4', fontsize=10, fontweight='bold'); ax3.axis('off')

        ax4 = self.fig.add_subplot(2, 2, 4)
        self._plot_rgb_histogram(ax4, self.img_equalized, "Histogram Equalized")
        self.canvas.draw()

    def _display_specification_result(self):
        self.fig.clear()

        ax1 = self.fig.add_subplot(2, 3, 1)
        ax1.imshow(self.img_original); ax1.set_title("Citra Asli", color='#cdd6f4', fontsize=9, fontweight='bold'); ax1.axis('off')

        ax2 = self.fig.add_subplot(2, 3, 2)
        ax2.imshow(self.img_reference); ax2.set_title("Citra Referensi", color='#cdd6f4', fontsize=9, fontweight='bold'); ax2.axis('off')

        ax3 = self.fig.add_subplot(2, 3, 3)
        ax3.imshow(self.img_specified); ax3.set_title("Hasil Specification", color='#cdd6f4', fontsize=9, fontweight='bold'); ax3.axis('off')

        ax4 = self.fig.add_subplot(2, 3, 4)
        self._plot_rgb_histogram(ax4, self.img_original, "Histogram Asli")

        ax5 = self.fig.add_subplot(2, 3, 5)
        self._plot_rgb_histogram(ax5, self.img_reference, "Histogram Referensi")

        ax6 = self.fig.add_subplot(2, 3, 6)
        self._plot_rgb_histogram(ax6, self.img_specified, "Histogram Hasil")
        self.canvas.draw()

    def reset_all(self):
        self.img_original = None
        self.img_reference = None
        self.img_equalized = None
        self.img_specified = None
        self.status_var.set("Siap. Silakan load citra asli untuk memulai.")
        self._show_welcome()


def main():
    root = tk.Tk()
    app = HistogramApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
