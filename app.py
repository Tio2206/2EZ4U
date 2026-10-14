"""Jalankan: python app.py"""
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from backend.layanan import Layanan


def main():
    try:
        import tkinter as tk
    except ImportError:
        print("Tkinter tidak tersedia. Linux: sudo apt install python3-tk")
        return
    from frontend.ui import Aplikasi
    root = tk.Tk()
    Aplikasi(root, Layanan(os.path.join(BASE, "data", "pesanan.csv")))
    root.mainloop()


if __name__ == "__main__":
    main()
