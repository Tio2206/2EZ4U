"""M2: Stack & Queue.

- Tumpukan (stack) dibangun di atas Array milik sendiri (M1).
- ke_postfix / hitung: mesin kasir (infix -> postfix -> total).
- AntreanNaif (larik + geser) vs AntreanMelingkar (front/rear/count, modulo).
- ManajerAntrean: undo/redo atas aksi ENQUEUE, DEQUEUE, ORDER, HAPUS.

Kebijakan antrean melingkar penuh: TUMBUH 2x (disalin berurutan mulai dari front,
front direset ke 0). Alasan memakai `count`: front == rear ambigu (kosong atau penuh).
"""

from backend.m1_pesanan import Array


# ---------------------------------------------------------------- Tumpukan
class Tumpukan:
    def __init__(self):
        self.isi = Array()

    def push(self, x):
        self.isi.append(x)

    def pop(self):
        if self.isi.n == 0:
            raise IndexError("tumpukan kosong")
        return self.isi.pop_last()

    def peek(self):
        if self.isi.n == 0:
            raise IndexError("tumpukan kosong")
        return self.isi.data[self.isi.n - 1]

    def kosong(self):
        return self.isi.n == 0

    def ukuran(self):
        return self.isi.n

    def kosongkan(self):
        self.isi = Array()

    def teks(self):
        return self.isi.teks()


# ---------------------------------------------------------------- Kasir
OPERATOR = ("+", "-", "*", "/")


def _prioritas(op):
    if op == "*" or op == "/":
        return 2
    return 1


def tokenisasi(ekspresi):
    """Pecah struk jadi token. Angka berdigit banyak jadi satu token (12000)."""
    hasil = Array()
    i = 0
    n = len(ekspresi)
    while i < n:
        c = ekspresi[i]
        if c == " " or c == "\t":
            i += 1
        elif c in "()+-*/":
            hasil.append(c)
            i += 1
        elif c.isdigit() or c == ".":
            j = i
            titik = 0
            while j < n and (ekspresi[j].isdigit() or ekspresi[j] == "."):
                if ekspresi[j] == ".":
                    titik += 1
                j += 1
            token = ekspresi[i:j]
            if titik > 1 or token == ".":
                raise ValueError("angka tidak valid: %s" % token)
            hasil.append(token)
            i = j
        else:
            raise ValueError("karakter tidak dikenal: '%s'" % c)
    if hasil.n == 0:
        raise ValueError("ekspresi kosong")
    return hasil


def _angka(token):
    if "." in token:
        return float(token)
    return int(token)


def ke_postfix(ekspresi, jejak=None):
    """Infix -> postfix memakai stack operator. Mengembalikan Array token postfix.
    `jejak` (Array, opsional) diisi baris (langkah, token, tindakan, stack, keluaran)."""
    tokens = tokenisasi(ekspresi)
    keluar = Array()
    st = Tumpukan()
    for ti in range(tokens.n):
        t = tokens.get(ti)
        nomor = "1.%d" % (ti + 1)
        if t == "(":
            st.push(t)
            tindakan = "push ( ke stack"
        elif t == ")":
            ketemu = False
            while not st.kosong():
                x = st.pop()
                if x == "(":
                    ketemu = True
                    break
                keluar.append(x)
            if not ketemu:
                raise ValueError("kurung tutup tanpa pasangan")
            tindakan = "pop sampai ( , lalu buang ("
        elif t in OPERATOR:
            dipop = Array()
            while (not st.kosong()) and st.peek() != "(" and _prioritas(st.peek()) >= _prioritas(t):
                x = st.pop()
                keluar.append(x)
                dipop.append(x)
            st.push(t)
            if dipop.n == 0:
                tindakan = "push %s" % t
            else:
                tindakan = "pop %s (lebih kuat/sama kuat), push %s" % (dipop.teks(), t)
        else:
            keluar.append(t)
            tindakan = "operand, langsung ke output"
        if jejak is not None:
            jejak.append((nomor, t, tindakan, st.teks() or "kosong", keluar.teks()))
    sisa = Array()
    while not st.kosong():
        x = st.pop()
        if x == "(":
            raise ValueError("kurung buka tanpa pasangan")
        keluar.append(x)
        sisa.append(x)
    if jejak is not None:
        jejak.append(("1.akhir", "-",
                      "pop sisa stack: %s" % (sisa.teks() or "(kosong)"),
                      "kosong", keluar.teks()))
    return keluar


def _daftar_token(postfix):
    if isinstance(postfix, str):
        d = postfix.split()
        return d, len(d)
    if isinstance(postfix, Array):
        return postfix.data, postfix.n
    return postfix, len(postfix)


def _fmt_angka(v):
    if isinstance(v, float) and v == int(v):
        return str(int(v))
    return str(v)


def hitung(postfix, jejak=None):
    """Evaluasi postfix dengan stack angka. Yang keluar pertama = operand KANAN."""
    daftar, n = _daftar_token(postfix)
    st = Tumpukan()
    for i in range(n):
        t = daftar[i]
        nomor = "2.%d" % (i + 1)
        if t in OPERATOR:
            if st.ukuran() < 2:
                raise ValueError("ekspresi tidak valid (operand kurang untuk '%s')" % t)
            b = st.pop()
            a = st.pop()
            if t == "+":
                h = a + b
            elif t == "-":
                h = a - b
            elif t == "*":
                h = a * b
            else:
                if b == 0:
                    raise ValueError("pembagian dengan nol")
                h = a / b
                if h == int(h):
                    h = int(h)
            st.push(h)
            tindakan = "pop %s dan %s -> %s %s %s = %s" % (
                _fmt_angka(b), _fmt_angka(a), _fmt_angka(a), t, _fmt_angka(b), _fmt_angka(h))
        else:
            st.push(_angka(t))
            tindakan = "operand, push %s" % t
        if jejak is not None:
            jejak.append((nomor, t, tindakan, st.teks(), st.teks()))
    if st.ukuran() != 1:
        raise ValueError("ekspresi tidak valid (sisa %d nilai di stack)" % st.ukuran())
    return st.pop()


# ---------------------------------------------------------------- Antrean
class AntreanNaif:
    """Larik biasa; dequeue mengambil indeks 0 lalu menggeser seluruh sisa. O(n)."""

    def __init__(self):
        self.larik = Array()
        self.total_geser = 0

    def __len__(self):
        return self.larik.n

    def enqueue(self, x):
        self.larik.append(x)

    def dequeue(self):
        a = self.larik
        if a.n == 0:
            return None
        d = a.data
        x = d[0]
        for j in range(1, a.n):
            d[j - 1] = d[j]
        self.total_geser += a.n - 1
        a.n -= 1
        d[a.n] = None
        return x

    def dequeue_banyak(self, k):
        """Kembalikan (list item, jumlah elemen digeser)."""
        k = min(k, self.larik.n)
        hasil = [None] * k
        geser = 0
        for t in range(k):
            sebelum = self.larik.n
            hasil[t] = self.dequeue()
            geser += sebelum - 1
        return hasil, geser

    def pop_back(self):
        return self.larik.pop_last()

    def sisip_depan(self, daftar):
        """Kembalikan daftar ke DEPAN (urutan asli terjaga) dengan satu kali geser."""
        k = len(daftar)
        a = self.larik
        while a.n + k > a.kap:
            a._tumbuh()
        d = a.data
        for j in range(a.n - 1, -1, -1):
            d[j + k] = d[j]
        for t in range(k):
            d[t] = daftar[t]
        self.total_geser += a.n
        a.n += k

    def isi(self, i):
        return self.larik.data[i]

    def kapasitas(self):
        return self.larik.kap


class AntreanMelingkar:
    """Ring buffer: data, front, rear, count. dequeue = front maju satu langkah, O(1)."""

    def __init__(self, kapasitas=4):
        self.data = [None] * kapasitas
        self.K = kapasitas
        self.front = 0
        self.rear = 0
        self.count = 0
        self.total_geser = 0   # selalu 0, ditampilkan sebagai pembanding

    def __len__(self):
        return self.count

    def kosong(self):
        return self.count == 0

    def _tumbuh(self):
        baru = [None] * (self.K * 2)
        for t in range(self.count):
            baru[t] = self.data[(self.front + t) % self.K]
        self.data = baru
        self.K = self.K * 2
        self.front = 0
        self.rear = self.count

    def enqueue(self, x):
        if self.count == self.K:
            self._tumbuh()
        self.data[self.rear] = x
        self.rear = (self.rear + 1) % self.K
        self.count += 1

    def dequeue(self):
        if self.count == 0:
            return None
        x = self.data[self.front]
        self.data[self.front] = None
        self.front = (self.front + 1) % self.K
        self.count -= 1
        return x

    def dequeue_banyak(self, k):
        k = min(k, self.count)
        hasil = [None] * k
        for t in range(k):
            hasil[t] = self.dequeue()
        return hasil, 0

    def pop_back(self):
        if self.count == 0:
            raise IndexError("antrean kosong")
        self.rear = (self.rear - 1) % self.K
        x = self.data[self.rear]
        self.data[self.rear] = None
        self.count -= 1
        return x

    def push_front(self, x):
        if self.count == self.K:
            self._tumbuh()
        self.front = (self.front - 1) % self.K
        self.data[self.front] = x
        self.count += 1

    def sisip_depan(self, daftar):
        for t in range(len(daftar) - 1, -1, -1):
            self.push_front(daftar[t])

    def isi(self, i):
        return self.data[(self.front + i) % self.K]

    def kapasitas(self):
        return self.K


# ---------------------------------------------------------------- Undo / Redo
class ManajerAntrean:
    """Dua antrean berisi data sama + tumpukan undo dan redo.

    Aksi (tuple):
      ("ENQUEUE", rec)
      ("DEQUEUE", "naif"|"circular", daftar_rec)   <- simpan DAFTAR, bukan hitungan
      ("ORDER", "array"|"linked", jenis, rec, idx)
      ("HAPUS", "array"|"linked", rec, idx)
    """

    def __init__(self):
        self.naif = AntreanNaif()
        self.mel = AntreanMelingkar()
        self.undo = Tumpukan()
        self.redo = Tumpukan()
        self.arr = None
        self.ll = None

    def lampirkan_m1(self, arr, ll):
        self.arr = arr
        self.ll = ll

    def isi_awal(self, rec):
        self.naif.enqueue(rec)
        self.mel.enqueue(rec)

    def catat(self, aksi):
        self.undo.push(aksi)
        self.redo.kosongkan()          # aksi baru -> riwayat bercabang -> redo dibuang

    def _struktur(self, nama):
        if nama == "array":
            return self.arr
        return self.ll

    def _antrean(self, nama):
        if nama == "naif":
            return self.naif
        return self.mel

    # ----- aksi
    def enqueue(self, rec):
        self.naif.enqueue(rec)
        self.mel.enqueue(rec)
        self.catat(("ENQUEUE", rec))

    def dequeue(self, versi, k):
        q = self._antrean(versi)
        daftar, geser = q.dequeue_banyak(k)
        if len(daftar) > 0:
            self.catat(("DEQUEUE", versi, daftar))
        return daftar, geser

    # ----- undo / redo
    def undo_last(self):
        """Kembalikan (teks, daftar_rec) atau None bila tidak ada yang dibatalkan."""
        if self.undo.kosong():
            return None
        a = self.undo.pop()
        jenis = a[0]
        if jenis == "ENQUEUE":
            self.naif.pop_back()
            self.mel.pop_back()
            teks = "Pembatalan enqueue: %s dikeluarkan lagi dari belakang." % a[1][0]
            recs = [a[1]]
        elif jenis == "DEQUEUE":
            self._antrean(a[1]).sisip_depan(a[2])
            teks = "%d pesanan dikembalikan ke DEPAN antrean %s." % (len(a[2]), a[1])
            recs = a[2]
        elif jenis == "ORDER":
            self._struktur(a[1]).remove(a[4])
            teks = "Pembatalan tambah: %s dicabut dari %s indeks %d." % (a[3][0], a[1], a[4])
            recs = [a[3]]
        else:
            self._struktur(a[1]).insert(a[3], a[2])
            teks = "Pembatalan hapus: %s dipasang lagi di %s indeks %d." % (a[2][0], a[1], a[3])
            recs = [a[2]]
        self.redo.push(a)
        return teks, recs

    def redo_last(self):
        if self.redo.kosong():
            return None
        a = self.redo.pop()
        jenis = a[0]
        if jenis == "ENQUEUE":
            self.naif.enqueue(a[1])
            self.mel.enqueue(a[1])
            teks = "Enqueue dikerjakan lagi: %s masuk kembali ke belakang." % a[1][0]
            recs = [a[1]]
        elif jenis == "DEQUEUE":
            self._antrean(a[1]).dequeue_banyak(len(a[2]))
            teks = "%d pesanan keluar lagi dari antrean %s." % (len(a[2]), a[1])
            recs = a[2]
        elif jenis == "ORDER":
            self._struktur(a[1]).insert(a[4], a[3])
            teks = "Tambah dikerjakan lagi: %s masuk %s indeks %d." % (a[3][0], a[1], a[4])
            recs = [a[3]]
        else:
            self._struktur(a[1]).remove(a[3])
            teks = "Hapus dikerjakan lagi: %s dicabut dari %s indeks %d." % (a[2][0], a[1], a[3])
            recs = [a[2]]
        self.undo.push(a)              # kembali ke undo; redo TIDAK dikosongkan
        return teks, recs

    # ----- laporan
    @staticmethod
    def _deskripsi(a):
        if a[0] == "ENQUEUE":
            return "ENQUEUE %s" % a[1][0]
        if a[0] == "DEQUEUE":
            return "DEQUEUE x%d (%s)" % (len(a[2]), a[1])
        if a[0] == "ORDER":
            return "ORDER %s (%s, indeks %d)" % (a[3][0], a[1], a[4])
        return "HAPUS %s (%s, indeks %d)" % (a[2][0], a[1], a[3])

    def history(self):
        """Riwayat undo, dari paling lama sampai paling baru (puncak)."""
        n = self.undo.ukuran()
        hasil = [None] * n
        for i in range(n):
            hasil[i] = self._deskripsi(self.undo.isi.data[i])
        return hasil

    def stats(self):
        return (
            ("queue_len naif", len(self.naif)),
            ("queue_len circular", len(self.mel)),
            ("queue_capacity naif", self.naif.kapasitas()),
            ("queue_capacity circular", self.mel.kapasitas()),
            ("total geseran naif", self.naif.total_geser),
            ("total geseran circular", self.mel.total_geser),
            ("undo_depth", self.undo.ukuran()),
            ("redo_depth", self.redo.ukuran()),
        )
