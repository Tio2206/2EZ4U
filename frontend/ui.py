"""Antarmuka Tkinter: menu di kiri, form + hasil di kanan, panel COMMAND di bawah."""

import time
import tkinter as tk
from tkinter import ttk

from backend.data import fmt_ms

BIRU = "#2b3a55"
BG = "#f4f4f4"

# Param: (label, nilai awal, opsi combobox atau None, petunjuk)
# Menu : ("H", judul bagian)  atau  ("M", kunci, label, judul, deskripsi, params, teks tombol)
P_NAMA = (("Nama pelanggan", "Pelanggan Baru", None, "nama untuk pesanan yang akan dibuat"),)
MENU = (
    ("H", "DATA"),
    ("M", "load", "Load", "Muat data", "Membaca data/pesanan.csv ke array, linked list, dan kedua antrean.", (), "LOAD"),

    ("H", "M1 - DATA PESANAN"),
    ("M", "array_lihat", "ARRAY - LIHAT PESANAN", "Array: lihat pesanan ke-i",
     "Akses langsung lewat indeks, O(1).",
     (("Indeks (mulai 0)", "0", None, "posisi pesanan"), ("Jumlah baris", "10", None, "berapa baris ditampilkan")), "LIHAT"),
    ("M", "array_reguler", "ARRAY - TAMBAH PESANAN REGULER", "Array: pesanan REGULER, masuk paling belakang",
     "append: amortized O(1).", P_NAMA, "TAMBAH"),
    ("M", "array_prioritas", "ARRAY - TAMBAH PESANAN PRIORITAS", "Array: pesanan PRIORITAS, menyerobot ke tengah",
     "Elemen separuh belakang digeser, O(n).", P_NAMA, "TAMBAH"),
    ("M", "array_vip", "ARRAY - TAMBAH PESANAN VIP", "Array: pesanan VIP, langsung ke urutan pertama",
     "Seluruh isi digeser satu langkah, O(n).", P_NAMA, "TAMBAH"),
    ("M", "array_hapus", "ARRAY - HAPUS PESANAN", "Array: hapus pesanan ke-i",
     "Elemen di kanannya digeser menutup celah, O(n).",
     (("Indeks (mulai 0)", "0", None, "pesanan yang dicabut"),), "HAPUS"),
    ("M", "ll_lihat", "LINKEDLIST - LIHAT PESANAN", "Linked list: lihat pesanan ke-i",
     "Harus menelusuri simpul dari head, O(n).",
     (("Indeks (mulai 0)", "0", None, "posisi pesanan"), ("Jumlah baris", "10", None, "berapa baris ditampilkan")), "LIHAT"),
    ("M", "ll_reguler", "LINKEDLIST - TAMBAH PESANAN REGULER", "Linked list: pesanan REGULER, di belakang",
     "Lewat penunjuk tail, O(1).", P_NAMA, "TAMBAH"),
    ("M", "ll_prioritas", "LINKEDLIST - TAMBAH PESANAN PRIORITAS", "Linked list: pesanan PRIORITAS, ke tengah",
     "Telusur ke tengah O(n), menyambung O(1).", P_NAMA, "TAMBAH"),
    ("M", "ll_vip", "LINKEDLIST - TAMBAH PESANAN VIP", "Linked list: pesanan VIP, ke urutan pertama",
     "Cukup mengubah head, O(1).", P_NAMA, "TAMBAH"),
    ("M", "ll_hapus", "LINKEDLIST - HAPUS PESANAN", "Linked list: hapus pesanan ke-i",
     "Telusur ke simpul sebelumnya lalu putus sambung, O(n).",
     (("Indeks (mulai 0)", "0", None, "pesanan yang dicabut"),), "HAPUS"),

    ("H", "M2 - STACK DAN QUEUE"),
    ("M", "stack_postfix", "STACK - POSTFIX (MESIN KASIR)", "Stack: hitung struk lewat postfix",
     "Tahap 1 infix menjadi postfix, tahap 2 postfix dievaluasi. Keduanya memakai stack.",
     (("Struk belanja (infix)", "( 3 * 12000 ) + ( 2 * 8500 ) - 5000", None,
       "angka, + - * / dan tanda kurung, dipisah spasi atau rapat"),), "HITUNG"),
    ("M", "stack_undo", "STACK - UNDO", "Stack: batalkan aksi terakhir",
     "Mengambil catatan teratas tumpukan undo lalu menjalankan kebalikannya.", (), "UNDO"),
    ("M", "stack_redo", "STACK - REDO", "Stack: kerjakan lagi aksi yang dibatalkan",
     "Mengerjakan aksi aslinya, bukan kebalikannya. Aksi baru apa pun mengosongkan tumpukan ini.", (), "REDO"),
    ("M", "queue_enqueue", "QUEUE - ENQUEUE", "Queue: pesanan baru masuk ke belakang",
     "Menambah pesanan di ujung belakang KEDUA antrean (naif dan circular).", P_NAMA, "ENQUEUE"),
    ("M", "queue_dequeue_naive", "QUEUE - DEQUEUE NAIF", "Queue naif: ambil dari depan dengan menggeser isi",
     "Mengambil indeks 0 lalu menggeser seluruh sisa satu petak ke kiri. O(n) setiap dequeue.",
     (("Berapa kali dequeue", "1", None, "sampai panjang antrean; coba 1 lalu 100"),), "DEQUEUE"),
    ("M", "queue_dequeue_circular", "QUEUE - DEQUEUE CIRCULAR", "Queue circular: ambil dari depan dengan memajukan penunjuk",
     "Hanya penunjuk front yang maju; isi larik tidak digeser. O(1).",
     (("Berapa kali dequeue", "1", None, "sampai panjang antrean; coba 1 lalu 100"),), "DEQUEUE"),

    ("H", "M3 - SORT DAN SEARCH"),
    ("M", "sort_insertion", "SORT - INSERTION SORT", "Sort: insertion sort, O(n^2)",
     "Setiap elemen digeser mundur sampai menemukan tempatnya. Stabil, di tempat. Batas 20.000 baris.",
     (("Jumlah baris diurutkan", "2000", None, "diambil dari awal data; coba 1.000 lalu 2.000 lalu 4.000"),
      ("Diurutkan menurut", "harga", ("oid", "harga", "selesai"), "oid (teks), harga (angka), selesai (waktu selesai)")),
     "URUTKAN"),
    ("M", "sort_merge", "SORT - MERGE SORT", "Sort: merge sort, O(n log n)",
     "Dibelah terus lalu digabung kembali. Stabil, sanggup mengurutkan seluruh data.",
     (("Jumlah baris diurutkan", "4000", None, "diambil dari awal data; coba 1.000 lalu 2.000 lalu 4.000"),
      ("Diurutkan menurut", "oid", ("oid", "harga", "selesai"), "oid (teks), harga (angka), selesai (waktu selesai)")),
     "URUTKAN"),
    ("M", "search_linear", "SEARCH - LINEAR SEARCH", "Search: linear search, O(n)",
     "Memeriksa pesanan satu per satu dari depan. Tidak menuntut data terurut.",
     (("Nomor pesanan (oid)", "O-137442", None, "format O-000001 sampai O-200000, atau angkanya saja"),), "CARI"),
    ("M", "search_binary", "SEARCH - BINARY SEARCH", "Search: binary search, O(log n)",
     "Membuang separuh sisa daftar tiap langkah. Menuntut daftar terurut menurut oid.",
     (("Nomor pesanan (oid)", "O-137442", None, "format O-000001 sampai O-200000, atau angkanya saja"),), "CARI"),

    ("H", "STATISTIK"),
    ("M", "stats", "STATISTIK DAN RIWAYAT", "Statistik struktur data",
     "Panjang dan kapasitas struktur, total geseran, kedalaman undo/redo, dan riwayat aksi.", (), "TAMPILKAN"),
)


class Aplikasi:
    def __init__(self, root, layanan):
        self.root = root
        self.layanan = layanan
        self.aktif = None          # indeks MENU yang sedang dipilih
        self.vars = []             # StringVar untuk parameter menu aktif
        self.tombol_menu = [None] * len(MENU)

        root.title("2EZ4U Food Delivery")
        root.geometry("1180x740")
        root.minsize(900, 560)
        root.configure(bg=BIRU)

        judul = tk.Label(root, text="2EZ4U Food Delivery", bg=BIRU, fg="white",
                         font=("Helvetica", 15, "bold"), anchor="w", padx=12, pady=8)
        judul.pack(fill="x")

        badan = tk.Frame(root, bg=BG)
        badan.pack(fill="both", expand=True)
        badan.columnconfigure(1, weight=1)
        badan.rowconfigure(0, weight=1)

        self._bangun_menu(badan)
        self._bangun_kanan(badan)
        self._bangun_bawah(root)
        self.pilih(1)              # Load

    # ------------------------------------------------------------ kiri
    def _bangun_menu(self, induk):
        kiri = tk.Frame(induk, bg=BG, width=290)
        kiri.grid(row=0, column=0, sticky="ns")
        kiri.grid_propagate(False)
        kanvas = tk.Canvas(kiri, bg=BG, highlightthickness=0, width=270)
        sb = ttk.Scrollbar(kiri, orient="vertical", command=kanvas.yview)
        dalam = tk.Frame(kanvas, bg=BG)
        dalam.bind("<Configure>", lambda e: kanvas.configure(scrollregion=kanvas.bbox("all")))
        kanvas.create_window((0, 0), window=dalam, anchor="nw")
        kanvas.configure(yscrollcommand=sb.set)
        kanvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        # roda mouse (Windows/macOS dan Linux)
        kanvas.bind_all("<MouseWheel>", lambda e: kanvas.yview_scroll(-1 if e.delta > 0 else 1, "units"))
        kanvas.bind_all("<Button-4>", lambda e: kanvas.yview_scroll(-1, "units"))
        kanvas.bind_all("<Button-5>", lambda e: kanvas.yview_scroll(1, "units"))

        for i in range(len(MENU)):
            m = MENU[i]
            if m[0] == "H":
                tk.Label(dalam, text=m[1], bg=BG, fg="#555", anchor="w",
                         font=("Helvetica", 8, "bold")).pack(fill="x", padx=8, pady=(10, 1))
            else:
                b = tk.Button(dalam, text=m[2], anchor="w", relief="groove", bd=1,
                              font=("Helvetica", 8), padx=6, pady=2,
                              command=lambda idx=i: self.pilih(idx))
                b.pack(fill="x", padx=8, pady=1)
                self.tombol_menu[i] = b
                self.bg_tombol = b.cget("bg")

    # ------------------------------------------------------------ kanan
    def _bangun_kanan(self, induk):
        kanan = tk.Frame(induk, bg="white", padx=12, pady=8)
        kanan.grid(row=0, column=1, sticky="nsew")
        kanan.columnconfigure(0, weight=1)
        kanan.rowconfigure(3, weight=1)

        self.lbl_judul = tk.Label(kanan, text="", bg="white", anchor="w", font=("Helvetica", 12, "bold"))
        self.lbl_judul.grid(row=0, column=0, sticky="ew")
        self.lbl_desk = tk.Label(kanan, text="", bg="white", fg="#666", anchor="w", justify="left",
                                 font=("Helvetica", 8), wraplength=760)
        self.lbl_desk.grid(row=1, column=0, sticky="ew")

        self.form = tk.Frame(kanan, bg="white")
        self.form.grid(row=2, column=0, sticky="ew", pady=(6, 4))

        # hasil: ringkasan + tabel
        hasil = tk.Frame(kanan, bg="white")
        hasil.grid(row=3, column=0, sticky="nsew")
        hasil.columnconfigure(0, weight=1)
        hasil.rowconfigure(1, weight=1)
        self.lbl_ringkas = tk.Label(hasil, text="", bg="white", anchor="w", justify="left",
                                    font=("Menlo", 9), wraplength=760)
        self.lbl_ringkas.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(2, 4))
        self.tabel = ttk.Treeview(hasil, show="headings", height=12)
        sy = ttk.Scrollbar(hasil, orient="vertical", command=self.tabel.yview)
        sx = ttk.Scrollbar(hasil, orient="horizontal", command=self.tabel.xview)
        self.tabel.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        self.tabel.grid(row=1, column=0, sticky="nsew")
        sy.grid(row=1, column=1, sticky="ns")
        sx.grid(row=2, column=0, sticky="ew")
        self.lbl_catatan = tk.Label(kanan, text="", bg="#fff8dc", fg="#555", anchor="w", justify="left",
                                    font=("Helvetica", 8), wraplength=760, padx=6, pady=3)
        self.lbl_catatan.grid(row=4, column=0, sticky="ew", pady=(4, 0))

    # ------------------------------------------------------------ bawah
    def _bangun_bawah(self, root):
        bawah = tk.Frame(root, bg=BG, padx=10, pady=4)
        bawah.pack(fill="x")
        tk.Label(bawah, text="COMMAND", bg=BG, fg="#555", anchor="w", font=("Helvetica", 8, "bold")).pack(fill="x")
        isi = tk.Frame(bawah)
        isi.pack(fill="x")
        self.log = tk.Text(isi, height=5, font=("Menlo", 9), state="disabled", bg="white")
        sb = ttk.Scrollbar(isi, orient="vertical", command=self.log.yview)
        self.log.configure(yscrollcommand=sb.set)
        self.log.pack(side="left", fill="x", expand=True)
        sb.pack(side="right", fill="y")
        self.status = tk.Label(root, text="siap", bg=BIRU, fg="white", anchor="w", padx=10,
                               font=("Menlo", 9))
        self.status.pack(fill="x")

    # ------------------------------------------------------------ logika
    def pilih(self, idx):
        m = MENU[idx]
        if m[0] != "M":
            return
        if self.aktif is not None:
            self.tombol_menu[self.aktif].configure(bg=self.bg_tombol)
        self.aktif = idx
        self.tombol_menu[idx].configure(bg="#cfe0f7")
        self.lbl_judul.configure(text=m[3])
        self.lbl_desk.configure(text=m[4])
        for w in self.form.winfo_children():
            w.destroy()
        self.vars = []
        params = m[5]
        for r in range(len(params)):
            label, awal, opsi, petunjuk = params[r]
            tk.Label(self.form, text=label, bg="white", font=("Helvetica", 9, "bold")).grid(
                row=r * 2, column=0, sticky="w", padx=(0, 8))
            v = tk.StringVar(value=awal)
            self.vars.append(v)
            if opsi is not None:
                w = ttk.Combobox(self.form, textvariable=v, values=list(opsi), state="readonly", width=16)
            else:
                w = ttk.Entry(self.form, textvariable=v, width=44 if len(awal) > 12 else 18)
                w.bind("<Return>", lambda e: self.jalankan())
            w.grid(row=r * 2, column=1, sticky="w")
            tk.Label(self.form, text=petunjuk, bg="white", fg="#888", font=("Helvetica", 8)).grid(
                row=r * 2 + 1, column=1, sticky="w", pady=(0, 3))
        tk.Button(self.form, text=m[6], width=14, bg=BIRU, fg="white", activebackground="#41547a",
                  command=self.jalankan).grid(row=0, column=2, rowspan=2, padx=16, sticky="n")

    def _isi_tabel(self, kolom, baris):
        self.tabel.delete(*self.tabel.get_children())
        self.tabel.configure(columns=kolom if len(kolom) > 0 else ("-",))
        if len(kolom) == 0:
            self.tabel.heading("-", text="")
            self.tabel.column("-", width=10)
            return
        for c in range(len(kolom)):
            self.tabel.heading(kolom[c], text=kolom[c])
            nama = kolom[c]
            if nama == "#" or nama == "prio" or nama == "langkah":
                lebar, rata = 60, "center"
            elif nama in ("tindakan", "isi"):
                lebar, rata = 330, "w"
            elif nama in ("stack", "output", "pelanggan"):
                lebar, rata = 190, "w"
            else:
                lebar, rata = 100, "w"
            self.tabel.column(nama, width=lebar, anchor=rata, stretch=True)
        for r in range(len(baris)):
            self.tabel.insert("", "end", values=baris[r])

    def jalankan(self):
        if self.aktif is None:
            return
        m = MENU[self.aktif]
        nilai = [None] * len(self.vars)
        for i in range(len(self.vars)):
            nilai[i] = self.vars[i].get()
        self.status.configure(text="memproses...")
        self.root.update_idletasks()
        mulai = time.perf_counter()
        try:
            h = self.layanan.jalankan(m[1], nilai)
        except (ValueError, RuntimeError, IndexError) as e:
            self.lbl_ringkas.configure(text="Galat: %s" % e, fg="#b00020")
            self.lbl_catatan.configure(text="")
            self._isi_tabel((), ())
            self.status.configure(text="[%s] galat" % m[2])
            self._catat("%-24s -> galat: %s" % (m[1], e))
            return
        total = (time.perf_counter() - mulai) * 1000.0
        self.lbl_ringkas.configure(text=h.ringkas, fg="black")
        self.lbl_catatan.configure(text=h.catatan, bg="#fff8dc" if h.catatan else "white")
        self._isi_tabel(h.kolom, h.baris)
        waktu = fmt_ms(h.ms)
        self.status.configure(text="[%s] %s" % (h.modul, waktu))
        self._catat("%-24s -> %s  %s" % (h.perintah, h.modul, waktu))

    def _catat(self, baris):
        self.log.configure(state="normal")
        self.log.insert("1.0", baris + "\n")
        self.log.configure(state="disabled")
