"""
==========================================================
Program Convolution / Mask Processing (Peningkatan Mutu Citra)
Pengolahan Citra Digital - Python (Tkinter GUI)
==========================================================
Mendukung citra BERWARNA (RGB) - konvolusi per channel R, G, B
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


# ============== Kernel Definitions ==============
KERNELS = {
    "Mean Filter 3x3": np.ones((3, 3)) / 9,
    "Mean Filter 5x5": np.ones((5, 5)) / 25,
    "Gaussian 3x3": np.array([[1, 2, 1],
                               [2, 4, 2],
                               [1, 2, 1]]) / 16,
    "Gaussian 5x5": np.array([[1,  4,  6,  4, 1],
                               [4, 16, 24, 16, 4],
                               [6, 24, 36, 24, 6],
                               [4, 16, 24, 16, 4],
                               [1,  4,  6,  4, 1]]) / 256,
    "Sharpen (Laplacian)": np.array([[ 0, -1,  0],
                                      [-1,  5, -1],
                                      [ 0, -1,  0]]),
    "Sharpen (High-Boost)": np.array([[-1, -1, -1],
                                       [-1,  9, -1],
                                       [-1, -1, -1]]),
    "Edge - Laplacian": np.array([[ 0, -1,  0],
                                   [-1,  4, -1],
                                   [ 0, -1,  0]]),
    "Edge - Sobel Horizontal": np.array([[-1, -2, -1],
                                          [ 0,  0,  0],
                                          [ 1,  2,  1]]),
    "Edge - Sobel Vertical": np.array([[-1, 0, 1],
                                        [-2, 0, 2],
                                        [-1, 0, 1]]),
    "Edge - Prewitt Horizontal": np.array([[-1, -1, -1],
                                            [ 0,  0,  0],
                                            [ 1,  1,  1]]),
    "Edge - Prewitt Vertical": np.array([[-1, 0, 1],
                                          [-1, 0, 1],
                                          [-1, 0, 1]]),
    "Emboss": np.array([[-2, -1, 0],
                         [-1,  1, 1],
                         [ 0,  1, 2]]),
}


class ConvolutionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Convolution (Mask Processing) - Pengolahan Citra Digital")
        self.root.geometry("1400x900")
        self.root.configure(bg="#1e1e2e")
        self.root.minsize(1200, 750)

        self.img_original = None   # numpy RGB
        self.img_result = None     # numpy RGB
        self.current_kernel_name = None

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
        style.configure("Sidebar.TFrame", background="#181825")
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"),
                         foreground="#1e1e2e", background="#89b4fa",
                         padding=(12, 7))
        style.map("Accent.TButton", background=[('active', '#74c7ec')])
        style.configure("Apply.TButton", font=("Segoe UI", 11, "bold"),
                         foreground="#1e1e2e", background="#a6e3a1",
                         padding=(14, 8))
        style.map("Apply.TButton", background=[('active', '#94e2d5')])
        style.configure("SideLabel.TLabel", font=("Segoe UI", 10),
                         foreground="#cdd6f4", background="#181825")
        style.configure("Status.TLabel", font=("Segoe UI", 9),
                         foreground="#a6adc8", background="#181825",
                         padding=(8, 4))

    def _build_ui(self):
        # Header
        header = ttk.Frame(self.root, style="Main.TFrame")
        header.pack(fill=tk.X, padx=20, pady=(15, 5))
        ttk.Label(header, text="🔲 Convolution / Mask Processing (RGB)",
                  style="Title.TLabel").pack(side=tk.LEFT)
        ttk.Label(header, text="Citra Berwarna", style="Sub.TLabel").pack(
            side=tk.LEFT, padx=(15, 0))

        # Body
        body = ttk.Frame(self.root, style="Main.TFrame")
        body.pack(fill=tk.BOTH, expand=True, padx=20, pady=8)

        # Sidebar
        sidebar = ttk.Frame(body, style="Sidebar.TFrame", width=280)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))
        sidebar.pack_propagate(False)

        px, py = 12, 6

        ttk.Label(sidebar, text="📂 Load Citra", style="SideLabel.TLabel").pack(
            anchor=tk.W, padx=px, pady=(15, 4))
        ttk.Button(sidebar, text="Pilih Gambar", style="Accent.TButton",
                   command=self.load_image).pack(fill=tk.X, padx=px, pady=py)

        ttk.Separator(sidebar, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=px, pady=10)

        ttk.Label(sidebar, text="🧩 Pilih Kernel / Mask", style="SideLabel.TLabel").pack(
            anchor=tk.W, padx=px, pady=(5, 4))

        self.kernel_var = tk.StringVar(value="Mean Filter 3x3")
        kernel_combo = ttk.Combobox(sidebar, textvariable=self.kernel_var,
                                     values=list(KERNELS.keys()),
                                     state='readonly', font=("Segoe UI", 10))
        kernel_combo.pack(fill=tk.X, padx=px, pady=py)
        kernel_combo.bind("<<ComboboxSelected>>", self._on_kernel_select)

        ttk.Label(sidebar, text="Kernel Matrix:", style="SideLabel.TLabel").pack(
            anchor=tk.W, padx=px, pady=(10, 2))

        self.kernel_display = tk.Text(sidebar, height=7, width=30,
                                       font=("Consolas", 10),
                                       bg="#313244", fg="#fab387",
                                       relief=tk.FLAT, padx=8, pady=8,
                                       state=tk.DISABLED)
        self.kernel_display.pack(fill=tk.X, padx=px, pady=py)

        ttk.Separator(sidebar, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=px, pady=10)

        ttk.Label(sidebar, text="✏️ Custom Kernel (3x3)", style="SideLabel.TLabel").pack(
            anchor=tk.W, padx=px, pady=(5, 4))

        custom_frame = ttk.Frame(sidebar, style="Sidebar.TFrame")
        custom_frame.pack(fill=tk.X, padx=px, pady=py)

        self.custom_entries = []
        for i in range(3):
            row = []
            for j in range(3):
                e = tk.Entry(custom_frame, width=5, font=("Consolas", 11),
                             bg="#313244", fg="#cdd6f4", justify=tk.CENTER,
                             relief=tk.FLAT, insertbackground='#cdd6f4')
                e.grid(row=i, column=j, padx=3, pady=3, ipady=4)
                e.insert(0, "0")
                row.append(e)
            self.custom_entries.append(row)

        ttk.Button(sidebar, text="Gunakan Custom Kernel",
                   style="Accent.TButton",
                   command=self.use_custom_kernel).pack(fill=tk.X, padx=px, pady=(8, 4))

        ttk.Separator(sidebar, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=px, pady=10)

        ttk.Button(sidebar, text="▶ Terapkan Konvolusi",
                   style="Apply.TButton",
                   command=self.apply_convolution).pack(fill=tk.X, padx=px, pady=py)
        ttk.Button(sidebar, text="💾 Simpan Hasil",
                   style="Accent.TButton",
                   command=self.save_result).pack(fill=tk.X, padx=px, pady=py)
        ttk.Button(sidebar, text="🔄 Reset",
                   style="Accent.TButton",
                   command=self.reset_all).pack(fill=tk.X, padx=px, pady=py)

        # Canvas
        canvas_frame = ttk.Frame(body, style="Main.TFrame")
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.fig = Figure(figsize=(10, 7), facecolor='#1e1e2e')
        self.fig.subplots_adjust(hspace=0.5, wspace=0.35)
        self.canvas = FigureCanvasTkAgg(self.fig, master=canvas_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Status
        self.status_var = tk.StringVar(value="Siap. Pilih gambar untuk memulai konvolusi.")
        ttk.Label(self.root, textvariable=self.status_var,
                  style="Status.TLabel", anchor=tk.W).pack(fill=tk.X, side=tk.BOTTOM)

        self._update_kernel_display()
        self._show_welcome()

    def _show_welcome(self):
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.set_facecolor('#1e1e2e')
        ax.text(0.5, 0.55, "Convolution / Mask Processing", fontsize=26,
                ha='center', va='center', color='#89b4fa', fontweight='bold',
                transform=ax.transAxes)
        ax.text(0.5, 0.40, "Mendukung Citra Berwarna (RGB)", fontsize=14,
                ha='center', va='center', color='#a6adc8', transform=ax.transAxes)
        ax.text(0.5, 0.28, "Pilih gambar dan kernel dari sidebar",
                fontsize=11, ha='center', va='center', color='#585b70',
                transform=ax.transAxes)
        ax.axis('off')
        self.canvas.draw()

    def _on_kernel_select(self, event=None):
        self._update_kernel_display()

    def _update_kernel_display(self):
        name = self.kernel_var.get()
        kernel = KERNELS.get(name)
        if kernel is None:
            return
        self._show_kernel_in_text(kernel)

    def _show_kernel_in_text(self, kernel):
        self.kernel_display.config(state=tk.NORMAL)
        self.kernel_display.delete("1.0", tk.END)
        rows = []
        for r in range(kernel.shape[0]):
            row_str = "  ".join(f"{kernel[r, c]:7.3f}" for c in range(kernel.shape[1]))
            rows.append(f"[ {row_str} ]")
        self.kernel_display.insert(tk.END, "\n".join(rows))
        self.kernel_display.config(state=tk.DISABLED)

    def _ensure_rgb(self, img_array):
        if len(img_array.shape) == 2:
            return np.stack([img_array]*3, axis=-1)
        if img_array.shape[2] == 4:
            return img_array[:, :, :3]
        return img_array

    def _plot_rgb_histogram(self, ax, img, title_text):
        colors = ['#ff6b6b', '#51cf66', '#339af0']
        labels = ['Red', 'Green', 'Blue']
        for i, (c, lbl) in enumerate(zip(colors, labels)):
            ax.hist(img[:, :, i].flatten(), bins=256, range=(0, 256),
                    color=c, alpha=0.5, label=lbl, edgecolor='none')
        ax.set_title(title_text, color='#cdd6f4', fontsize=10, fontweight='bold')
        ax.legend(fontsize=7, loc='upper right',
                  facecolor='#313244', edgecolor='#45475a', labelcolor='#cdd6f4')
        ax.set_facecolor('#313244')
        ax.tick_params(colors='#a6adc8', labelsize=7)
        for s in ax.spines.values():
            s.set_color('#45475a')

    # ================ Core ================

    def load_image(self):
        path = filedialog.askopenfilename(
            title="Pilih Citra",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff")])
        if not path:
            return
        try:
            img = np.array(Image.open(path))
            self.img_original = self._ensure_rgb(img)
            self.img_result = None
            self.status_var.set(f"Citra dimuat: {os.path.basename(path)} "
                                f"({self.img_original.shape[1]}x{self.img_original.shape[0]}, RGB)")
            self._display_original()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuka citra:\n{e}")

    def use_custom_kernel(self):
        try:
            kernel = np.zeros((3, 3))
            for i in range(3):
                for j in range(3):
                    kernel[i, j] = float(self.custom_entries[i][j].get().strip())
            self.kernel_var.set("Custom 3x3")
            KERNELS["Custom 3x3"] = kernel
            self._show_kernel_in_text(kernel)
            self.status_var.set("Custom kernel telah diset.")
        except ValueError:
            messagebox.showerror("Error", "Nilai kernel harus berupa angka!")

    def convolve2d(self, image, kernel):
        """Konvolusi 2D manual untuk satu channel."""
        img_h, img_w = image.shape
        k_h, k_w = kernel.shape
        pad_h, pad_w = k_h // 2, k_w // 2
        padded = np.pad(image.astype(np.float64),
                        ((pad_h, pad_h), (pad_w, pad_w)), mode='edge')
        output = np.zeros_like(image, dtype=np.float64)
        for i in range(img_h):
            for j in range(img_w):
                output[i, j] = np.sum(padded[i:i+k_h, j:j+k_w] * kernel)
        return np.clip(output, 0, 255).astype(np.uint8)

    def apply_convolution(self):
        if self.img_original is None:
            messagebox.showwarning("Peringatan", "Silakan load citra terlebih dahulu!")
            return

        kernel_name = self.kernel_var.get()
        kernel = KERNELS.get(kernel_name)
        if kernel is None:
            messagebox.showerror("Error", "Kernel tidak ditemukan!")
            return

        self.status_var.set(f"Memproses konvolusi RGB: {kernel_name}...")
        self.root.update_idletasks()

        # Konvolusi per channel R, G, B
        result = np.zeros_like(self.img_original)
        for ch in range(3):
            result[:, :, ch] = self.convolve2d(self.img_original[:, :, ch], kernel)

        self.img_result = result
        self.current_kernel_name = kernel_name
        self.status_var.set(f"Konvolusi selesai: {kernel_name} (RGB)")
        self._display_result()

    def save_result(self):
        if self.img_result is None:
            messagebox.showwarning("Peringatan", "Belum ada hasil untuk disimpan!")
            return
        path = filedialog.asksaveasfilename(
            title="Simpan Hasil", defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp")])
        if path:
            Image.fromarray(self.img_result).save(path)
            self.status_var.set(f"Hasil disimpan: {path}")

    # ================ Display ================

    def _display_original(self):
        self.fig.clear()
        ax = self.fig.add_subplot(1, 1, 1)
        ax.imshow(self.img_original)
        ax.set_title("Citra Asli (RGB)", color='#cdd6f4', fontsize=13, fontweight='bold')
        ax.axis('off')
        self.canvas.draw()

    def _display_result(self):
        self.fig.clear()

        ax1 = self.fig.add_subplot(2, 2, 1)
        ax1.imshow(self.img_original)
        ax1.set_title("Citra Asli", color='#cdd6f4', fontsize=11, fontweight='bold')
        ax1.axis('off')

        ax2 = self.fig.add_subplot(2, 2, 2)
        ax2.imshow(self.img_result)
        title = f"Hasil: {self.current_kernel_name}" if self.current_kernel_name else "Hasil Konvolusi"
        ax2.set_title(title, color='#cdd6f4', fontsize=11, fontweight='bold')
        ax2.axis('off')

        ax3 = self.fig.add_subplot(2, 2, 3)
        self._plot_rgb_histogram(ax3, self.img_original, "Histogram Asli (RGB)")

        ax4 = self.fig.add_subplot(2, 2, 4)
        self._plot_rgb_histogram(ax4, self.img_result, "Histogram Hasil (RGB)")

        self.canvas.draw()

    def reset_all(self):
        self.img_original = None
        self.img_result = None
        self.current_kernel_name = None
        self.status_var.set("Siap. Pilih gambar untuk memulai konvolusi.")
        self._show_welcome()


def main():
    root = tk.Tk()
    app = ConvolutionApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
