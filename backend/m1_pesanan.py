"""M1: Array (larik dinamis) vs Linked List.

Aturan: tanpa dict/set/sorted/.sort()/heapq/bisect/collections.
List Python hanya dipakai sebagai petak memori primitif: [None] * kapasitas,
diakses lewat indeks. Pertumbuhan, penggeseran, dan penelusuran ditulis sendiri.

Setiap operasi menyimpan ongkosnya di atribut `langkah`:
  Array     -> jumlah elemen yang digeser
  LinkList  -> jumlah simpul yang ditelusuri
"""

REGULER, PRIORITAS, VIP = 3, 2, 1


class Array:
    """Larik dinamis. Penuh -> petak baru 2x, salin, buang petak lama (amortized O(1))."""

    def __init__(self, kapasitas=4):
        self.data = [None] * kapasitas
        self.n = 0
        self.kap = kapasitas
        self.salinan = 0   # total elemen yang pernah disalin saat tumbuh
        self.langkah = 0   # elemen digeser pada operasi terakhir

    def _tumbuh(self):
        baru = [None] * (self.kap * 2)
        lama = self.data
        for i in range(self.n):
            baru[i] = lama[i]
        self.salinan += self.n
        self.data = baru
        self.kap = self.kap * 2

    def get(self, i):                      # O(1)
        if i < 0 or i >= self.n:
            raise IndexError("indeks %d di luar rentang 0..%d" % (i, self.n - 1))
        return self.data[i]

    def ubah(self, i, v):
        if i < 0 or i >= self.n:
            raise IndexError("indeks %d di luar rentang" % i)
        self.data[i] = v

    def append(self, v):                   # O(1) amortized
        if self.n == self.kap:
            self._tumbuh()
        self.data[self.n] = v
        self.n += 1
        self.langkah = 0

    def insert(self, i, v):                # O(n)
        if i < 0 or i > self.n:
            raise IndexError("posisi sisip %d di luar rentang 0..%d" % (i, self.n))
        if self.n == self.kap:
            self._tumbuh()
        d = self.data
        j = self.n
        while j > i:
            d[j] = d[j - 1]
            j -= 1
        d[i] = v
        self.langkah = self.n - i
        self.n += 1

    def pop_last(self):                    # O(1)
        if self.n == 0:
            raise IndexError("array kosong")
        self.n -= 1
        v = self.data[self.n]
        self.data[self.n] = None
        self.langkah = 0
        return v

    def remove(self, i):                   # O(n)
        if i < 0 or i >= self.n:
            raise IndexError("indeks %d di luar rentang 0..%d" % (i, self.n - 1))
        d = self.data
        v = d[i]
        for j in range(i, self.n - 1):
            d[j] = d[j + 1]
        self.langkah = self.n - 1 - i
        self.n -= 1
        d[self.n] = None
        return v

    # --- tiga jenis penyisipan; mengembalikan indeks tempat pesanan mendarat
    def tambah_reguler(self, v):
        self.append(v)
        return self.n - 1

    def tambah_prioritas(self, v):
        i = self.n // 2
        self.insert(i, v)
        return i

    def tambah_vip(self, v):
        self.insert(0, v)
        return 0

    def lihat_rentang(self, i, k):
        """Kembalikan list (indeks, nilai) sebanyak <= k mulai dari i. Akses awal O(1)."""
        if i < 0 or i >= self.n:
            raise IndexError("indeks %d di luar rentang 0..%d" % (i, self.n - 1))
        jml = min(k, self.n - i)
        hasil = [None] * jml
        for t in range(jml):
            hasil[t] = (i + t, self.data[i + t])
        self.langkah = 0
        return hasil

    def ke_list(self):
        hasil = [None] * self.n
        for i in range(self.n):
            hasil[i] = self.data[i]
        return hasil

    def teks(self):
        return " ".join([str(self.data[i]) for i in range(self.n)])

    def __len__(self):
        return self.n


class Node:
    __slots__ = ("nilai", "nxt")

    def __init__(self, nilai):
        self.nilai = nilai
        self.nxt = None


class LinkList:
    """Singly linked list dengan penunjuk head dan tail."""

    def __init__(self):
        self.head = None
        self.tail = None
        self.n = 0
        self.langkah = 0   # simpul ditelusuri pada operasi terakhir

    def append(self, v):                   # O(1) berkat tail
        node = Node(v)
        if self.tail is None:
            self.head = node
            self.tail = node
        else:
            self.tail.nxt = node
            self.tail = node
        self.n += 1
        self.langkah = 0

    def prepend(self, v):                  # O(1)
        node = Node(v)
        node.nxt = self.head
        self.head = node
        if self.tail is None:
            self.tail = node
        self.n += 1
        self.langkah = 0

    def _simpul(self, i):
        cur = self.head
        for _ in range(i):
            cur = cur.nxt
        return cur

    def get(self, i):                      # O(n)
        if i < 0 or i >= self.n:
            raise IndexError("indeks %d di luar rentang 0..%d" % (i, self.n - 1))
        self.langkah = i
        return self._simpul(i).nilai

    def insert(self, i, v):                # O(n) telusur, O(1) sambung
        if i < 0 or i > self.n:
            raise IndexError("posisi sisip %d di luar rentang 0..%d" % (i, self.n))
        if i == 0:
            self.prepend(v)
        elif i == self.n:
            self.append(v)
        else:
            prev = self._simpul(i - 1)
            node = Node(v)
            node.nxt = prev.nxt
            prev.nxt = node
            self.n += 1
            self.langkah = i - 1

    def remove(self, i):                   # O(n) telusur
        if i < 0 or i >= self.n:
            raise IndexError("indeks %d di luar rentang 0..%d" % (i, self.n - 1))
        if i == 0:
            node = self.head
            self.head = node.nxt
            if self.head is None:
                self.tail = None
            self.langkah = 0
        else:
            prev = self._simpul(i - 1)
            node = prev.nxt
            prev.nxt = node.nxt
            if node is self.tail:
                self.tail = prev
            self.langkah = i - 1
        self.n -= 1
        return node.nilai

    def tambah_reguler(self, v):
        self.append(v)
        return self.n - 1

    def tambah_prioritas(self, v):
        i = self.n // 2
        self.insert(i, v)
        return i

    def tambah_vip(self, v):
        self.prepend(v)
        return 0

    def lihat_rentang(self, i, k):
        """Telusuri i simpul sekali, lalu ikuti penunjuk sebanyak k simpul."""
        if i < 0 or i >= self.n:
            raise IndexError("indeks %d di luar rentang 0..%d" % (i, self.n - 1))
        jml = min(k, self.n - i)
        hasil = [None] * jml
        cur = self._simpul(i)
        for t in range(jml):
            hasil[t] = (i + t, cur.nilai)
            cur = cur.nxt
        self.langkah = i
        return hasil

    def ke_list(self):
        hasil = [None] * self.n
        cur = self.head
        for i in range(self.n):
            hasil[i] = cur.nilai
            cur = cur.nxt
        return hasil

    def __len__(self):
        return self.n
