"""Fasad backend: satu pintu `jalankan(kunci_menu, argumen)` -> Hasil.
UI hanya memanggil ini dan menampilkan Hasil beserta waktunya."""

import time

from backend.data import muat_pesanan, fmt_int, fmt_ms, fmt_jam, fmt_rupiah
from backend.m1_pesanan import Array, LinkList, REGULER, PRIORITAS, VIP
from backend.m2_antrean import ManajerAntrean, ke_postfix, hitung
from backend.m3_laporan import (Pencacah, insertion_sort, merge_sort, linear_search,
                                binary_search, OID, HARGA, T_SELESAI)

BATAS_INSERTION = 20000
BATAS_TAMPIL = 200

KOLOM_PESANAN = ("#", "oid", "pelanggan", "resto", "menu", "harga", "prio", "masuk", "selesai", "status")
KOLOM_DETAIL = ("kolom", "isi")
NAMA_JENIS = ("", "VIP", "PRIORITAS", "REGULER")


class Hasil:
    def __init__(self, perintah, modul, ringkas, kolom=(), baris=(), ms=0.0, catatan=""):
        self.perintah = perintah
        self.modul = modul
        self.ringkas = ringkas
        self.kolom = kolom
        self.baris = baris
        self.ms = ms
        self.catatan = catatan


def _int(teks, nama):
    try:
        return int(str(teks).strip().replace(".", ""))
    except ValueError:
        raise ValueError("%s harus berupa bilangan bulat" % nama)


def baris_pesanan(i, r):
    return (i, r[0], r[1], r[2], r[3], fmt_int(r[4]), r[5], fmt_jam(r[6]), fmt_jam(r[7]), r[8])


def baris_detail(r):
    return (("oid", r[0]), ("pelanggan", r[1]), ("resto", r[2]), ("menu", r[3]),
            ("harga", fmt_int(r[4])), ("prioritas", r[5]), ("masuk", fmt_jam(r[6])),
            ("selesai", fmt_jam(r[7])), ("status", r[8]))


def _tabel_dari(daftar_rec, mulai=0):
    jml = min(len(daftar_rec), BATAS_TAMPIL)
    out = [None] * jml
    for i in range(jml):
        out[i] = baris_pesanan(mulai + i, daftar_rec[i])
    return out


class Layanan:
    def __init__(self, path_data):
        self.path = path_data
        self.arr = None
        self.ll = None
        self.mgr = None
        self.next_oid = 1
        self.versi = 0
        self.idx_oid = None
        self.idx_versi = -1

    # ---------------------------------------------------------- util
    def _siap(self):
        if self.arr is None:
            raise RuntimeError("Data belum dimuat. Tekan tombol Load dulu.")

    def _struktur(self, nama):
        return self.arr if nama == "array" else self.ll

    def _pesanan_baru(self, nama, prio):
        nama = nama.strip()
        if nama == "":
            nama = "Pelanggan Baru"
        oid = "O-%06d" % self.next_oid
        self.next_oid += 1
        t = time.localtime()
        detik = t.tm_hour * 3600 + t.tm_min * 60 + t.tm_sec
        return (oid, nama, "kafe-teknik", "roti-bakar", 12000, prio, detik, None, "ANTRE")

    def _panjang_antrean(self):
        return "naif %s, circular %s" % (fmt_int(len(self.mgr.naif)), fmt_int(len(self.mgr.mel)))

    # ---------------------------------------------------------- dispatcher
    def jalankan(self, kunci, a):
        if kunci == "load":
            return self.load()
        self._siap()
        if kunci == "array_lihat":
            return self.lihat("array", a)
        if kunci == "ll_lihat":
            return self.lihat("linked", a)
        if kunci == "array_reguler":
            return self.tambah("array", REGULER, a)
        if kunci == "array_prioritas":
            return self.tambah("array", PRIORITAS, a)
        if kunci == "array_vip":
            return self.tambah("array", VIP, a)
        if kunci == "ll_reguler":
            return self.tambah("linked", REGULER, a)
        if kunci == "ll_prioritas":
            return self.tambah("linked", PRIORITAS, a)
        if kunci == "ll_vip":
            return self.tambah("linked", VIP, a)
        if kunci == "array_hapus":
            return self.hapus("array", a)
        if kunci == "ll_hapus":
            return self.hapus("linked", a)
        if kunci == "stack_postfix":
            return self.stack_postfix(a)
        if kunci == "stack_undo":
            return self.undo()
        if kunci == "stack_redo":
            return self.redo()
        if kunci == "queue_enqueue":
            return self.queue_enqueue(a)
        if kunci == "queue_dequeue_naive":
            return self.queue_dequeue("naif", a)
        if kunci == "queue_dequeue_circular":
            return self.queue_dequeue("circular", a)
        if kunci == "sort_insertion":
            return self.urutkan("insertion", a)
        if kunci == "sort_merge":
            return self.urutkan("merge", a)
        if kunci == "search_linear":
            return self.cari_linear(a)
        if kunci == "search_binary":
            return self.cari_binary(a)
        if kunci == "stats":
            return self.stats()
        raise ValueError("perintah tidak dikenal: %s" % kunci)

    # ---------------------------------------------------------- DATA
    def load(self):
        t0 = time.perf_counter()
        arr = muat_pesanan(self.path)
        ll = LinkList()
        mgr = ManajerAntrean()
        antre = 0
        for i in range(arr.n):
            r = arr.data[i]
            ll.append(r)
            if r[8] == "ANTRE":
                mgr.isi_awal(r)
                antre += 1
        mgr.lampirkan_m1(arr, ll)
        self.arr, self.ll, self.mgr = arr, ll, mgr
        self.next_oid = arr.n + 1
        self.versi += 1
        ms = (time.perf_counter() - t0) * 1000.0
        teks = ("%s pesanan dimuat ke array (kapasitas %s, %s elemen disalin saat tumbuh) dan linked list.\n"
                "%s pesanan berstatus ANTRE masuk ke KEDUA antrean."
                % (fmt_int(arr.n), fmt_int(arr.kap), fmt_int(arr.salinan), fmt_int(antre)))
        pratinjau = arr.lihat_rentang(0, 10)
        out = [None] * len(pratinjau)
        for t in range(len(pratinjau)):
            out[t] = baris_pesanan(pratinjau[t][0], pratinjau[t][1])
        return Hasil("load", "DATA - load", teks + "\nPratinjau 10 baris pertama.", KOLOM_PESANAN, out, ms)

    # ---------------------------------------------------------- M1
    def lihat(self, nama, a):
        s = self._struktur(nama)
        i = _int(a[0], "indeks")
        k = _int(a[1], "jumlah")
        if k < 1:
            raise ValueError("jumlah minimal 1")
        t0 = time.perf_counter()
        pasangan = s.lihat_rentang(i, k)
        ms = (time.perf_counter() - t0) * 1000.0
        jml = len(pasangan)
        out = [None] * min(jml, BATAS_TAMPIL)
        for t in range(len(out)):
            out[t] = baris_pesanan(pasangan[t][0], pasangan[t][1])
        if nama == "array":
            teks = "Array: akses langsung ke indeks %d, O(1), 0 elemen dilewati." % i
        else:
            teks = "Linked list: menelusuri %s simpul dari head sampai indeks %d, O(n)." % (fmt_int(s.langkah), i)
        teks += "\nMenampilkan %d pesanan dari total %s." % (len(out), fmt_int(s.n))
        modul = "M1 - array" if nama == "array" else "M1 - linked"
        return Hasil("%s_lihat" % ("array" if nama == "array" else "linkedlist"), modul, teks,
                     KOLOM_PESANAN, out, ms)

    def tambah(self, nama, jenis, a):
        s = self._struktur(nama)
        rec = self._pesanan_baru(a[0], jenis)
        salinan_sebelum = self.arr.salinan if nama == "array" else 0
        t0 = time.perf_counter()
        if jenis == REGULER:
            idx = s.tambah_reguler(rec)
        elif jenis == PRIORITAS:
            idx = s.tambah_prioritas(rec)
        else:
            idx = s.tambah_vip(rec)
        ms = (time.perf_counter() - t0) * 1000.0
        self.mgr.catat(("ORDER", nama, jenis, rec, idx))
        if nama == "array":
            self.versi += 1
            teks = "%s masuk sebagai %s di indeks %s dari %s pesanan.\nArray menggeser %s elemen." % (
                rec[0], NAMA_JENIS[jenis], fmt_int(idx), fmt_int(s.n), fmt_int(s.langkah))
            if self.arr.salinan != salinan_sebelum:
                teks += " Kapasitas dilipatkan, %s elemen disalin." % fmt_int(self.arr.salinan - salinan_sebelum)
            modul = "M1 - array"
        else:
            teks = "%s masuk sebagai %s di indeks %s dari %s pesanan.\nLinked list menelusuri %s simpul." % (
                rec[0], NAMA_JENIS[jenis], fmt_int(idx), fmt_int(s.n), fmt_int(s.langkah))
            modul = "M1 - linked"
        awal = idx - 2 if idx >= 2 else 0
        tetangga = s.lihat_rentang(awal, 5)
        out = [None] * len(tetangga)
        for t in range(len(tetangga)):
            out[t] = baris_pesanan(tetangga[t][0], tetangga[t][1])
        nm = {REGULER: "reguler", PRIORITAS: "prioritas", VIP: "vip"}
        return Hasil("%s_%s" % ("array" if nama == "array" else "linkedlist", "tambah_" + nm[jenis]),
                     modul, teks, KOLOM_PESANAN, out, ms,
                     "Baris di tabel: pesanan baru dan tetangganya.")

    def hapus(self, nama, a):
        s = self._struktur(nama)
        i = _int(a[0], "indeks")
        t0 = time.perf_counter()
        rec = s.remove(i)
        ms = (time.perf_counter() - t0) * 1000.0
        self.mgr.catat(("HAPUS", nama, rec, i))
        if nama == "array":
            self.versi += 1
            teks = "%s dihapus dari indeks %d. Array menggeser %s elemen." % (rec[0], i, fmt_int(s.langkah))
            modul = "M1 - array"
        else:
            teks = "%s dihapus dari indeks %d. Linked list menelusuri %s simpul." % (rec[0], i, fmt_int(s.langkah))
            modul = "M1 - linked"
        return Hasil("%s_hapus" % ("array" if nama == "array" else "linkedlist"), modul, teks,
                     KOLOM_PESANAN, [baris_pesanan(i, rec)], ms,
                     "Sisa pesanan: %s." % fmt_int(s.n))

    # ---------------------------------------------------------- M2
    def stack_postfix(self, a):
        ekspresi = a[0]
        j1 = Array()
        j2 = Array()
        t0 = time.perf_counter()
        postfix = ke_postfix(ekspresi, j1)
        total = hitung(postfix, j2)
        ms = (time.perf_counter() - t0) * 1000.0
        baris = j1.ke_list() + j2.ke_list()
        teks = "Struk : %s\nPostfix: %s\nTOTAL : %s" % (ekspresi.strip(), postfix.teks(), fmt_rupiah(total))
        return Hasil("stack_postfix", "M2 - stack", teks,
                     ("langkah", "token", "tindakan", "stack", "output"), baris, ms,
                     "Baris 1.x = konversi infix -> postfix, 2.x = evaluasi. Operand kanan keluar pertama (b = pop, a = pop, a-b).")

    def queue_enqueue(self, a):
        rec = self._pesanan_baru(a[0], REGULER)
        t0 = time.perf_counter()
        self.mgr.enqueue(rec)
        ms = (time.perf_counter() - t0) * 1000.0
        teks = "%s masuk ke barisan paling belakang pada KEDUA antrean.\nPanjang sekarang: %s." % (
            rec[0], self._panjang_antrean())
        return Hasil("queue_enqueue", "M2 - queue", teks, KOLOM_DETAIL, baris_detail(rec), ms,
                     "enqueue menempel di belakang, jadi O(1) pada kedua versi. Bedanya baru muncul saat dequeue.")

    def queue_dequeue(self, versi, a):
        k = _int(a[0], "jumlah")
        if k < 1:
            raise ValueError("jumlah minimal 1")
        t0 = time.perf_counter()
        daftar, geser = self.mgr.dequeue(versi, k)
        ms = (time.perf_counter() - t0) * 1000.0
        jml = len(daftar)
        if jml == 0:
            return Hasil("queue_dequeue_" + ("naive" if versi == "naif" else "circular"),
                         "M2 - queue", "Antrean kosong, tidak ada yang dilayani.", (), (), ms)
        if versi == "naif":
            teks = "%d pesanan keluar dari depan antrean naif.\nTotal %s elemen digeser, rata-rata %s geseran per dequeue.\nSisa antrean naif %s." % (
                jml, fmt_int(geser), fmt_int(geser // jml), fmt_int(len(self.mgr.naif)))
            modul = "M2 - queue naif"
            perintah = "queue_dequeue_naive"
        else:
            q = self.mgr.mel
            teks = "%d pesanan keluar dari depan antrean circular.\nTidak ada elemen yang digeser. front sekarang %d, rear %s, kapasitas %s.\nSisa antrean circular %s." % (
                jml, q.front, fmt_int(q.rear), fmt_int(q.K), fmt_int(len(q)))
            modul = "M2 - queue circular"
            perintah = "queue_dequeue_circular"
        return Hasil(perintah, modul, teks, KOLOM_PESANAN, _tabel_dari(daftar), ms,
                     "Isi kedua antrean sama persis; jalankan versi naif dan circular lalu bandingkan waktunya.")

    def _lapor_riwayat(self, perintah, r, kosong_teks):
        m = self.mgr
        if r is None:
            return Hasil(perintah, "M2 - stack", kosong_teks, (), (), 0.0)
        teks, recs = r
        teks += "\nPanjang antrean sekarang: %s. Tumpukan undo %d, redo %d." % (
            self._panjang_antrean(), m.undo.ukuran(), m.redo.ukuran())
        self.versi += 1
        return Hasil(perintah, "M2 - stack", teks, KOLOM_PESANAN, _tabel_dari(recs), 0.0)

    def undo(self):
        t0 = time.perf_counter()
        r = self.mgr.undo_last()
        ms = (time.perf_counter() - t0) * 1000.0
        h = self._lapor_riwayat("stack_undo", r, "Tumpukan undo kosong, tidak ada yang dibatalkan.")
        h.ms = ms
        return h

    def redo(self):
        t0 = time.perf_counter()
        r = self.mgr.redo_last()
        ms = (time.perf_counter() - t0) * 1000.0
        h = self._lapor_riwayat("stack_redo", r, "Tumpukan redo kosong, tidak ada yang diulang.")
        h.ms = ms
        return h

    # ---------------------------------------------------------- M3
    def _kunci(self, nama):
        if nama == "oid":
            return OID
        if nama == "harga":
            return HARGA
        if nama == "selesai":
            return T_SELESAI
        raise ValueError("kunci harus oid, harga, atau selesai")

    def urutkan(self, algoritma, a):
        jumlah = _int(a[0], "jumlah baris")
        kunci_nama = a[1].strip().lower()
        k = self._kunci(kunci_nama)
        if jumlah < 1:
            raise ValueError("jumlah minimal 1")
        if jumlah > self.arr.n:
            raise ValueError("jumlah melebihi data (%s baris)" % fmt_int(self.arr.n))
        if algoritma == "insertion" and jumlah > BATAS_INSERTION:
            raise ValueError("DITOLAK: batasnya %s baris, pakai merge sort untuk data penuh." % fmt_int(BATAS_INSERTION))
        salinan = [None] * jumlah
        for i in range(jumlah):
            salinan[i] = self.arr.data[i]
        cnt = Pencacah()
        t0 = time.perf_counter()
        if algoritma == "insertion":
            hasil = insertion_sort(salinan, k, cnt)
        else:
            hasil = merge_sort(salinan, k, cnt)
        ms = (time.perf_counter() - t0) * 1000.0
        tampil = min(jumlah, BATAS_TAMPIL)
        out = [None] * tampil
        for i in range(tampil):
            r = hasil[i]
            out[i] = (i + 1, r[0], fmt_int(r[4]), fmt_jam(r[7]), r[2], r[3])
        teks = "%s pesanan diurutkan menurut %s.\n%s perbandingan, %s pemindahan." % (
            fmt_int(jumlah), kunci_nama, fmt_int(cnt.perbandingan), fmt_int(cnt.pemindahan))
        if jumlah > tampil:
            teks += "\nMenampilkan %d baris pertama." % tampil
        nama_cmd = "insertion_sort" if algoritma == "insertion" else "merge_sort"
        modul = "M3 - insertion sort" if algoritma == "insertion" else "M3 - merge sort"
        cat = ("Setiap elemen digeser mundur sampai menemukan tempatnya, jadi biayanya tumbuh kuadratik."
               if algoritma == "insertion" else
               "Dibelah dua terus-menerus lalu digabung; kedalaman log n, tiap lapis O(n). Hasil sama persis dengan insertion sort (stabil).")
        return Hasil(nama_cmd, modul, teks, ("#", "oid", "harga", "selesai", "resto", "menu"), out, ms, cat)

    def _oid_target(self, teks):
        t = teks.strip().upper()
        if t.isdigit():
            t = "O-%06d" % int(t)
        if t == "":
            raise ValueError("nomor pesanan kosong")
        return t

    def cari_linear(self, a):
        target = self._oid_target(a[0])
        cnt = Pencacah()
        t0 = time.perf_counter()
        idx = linear_search(self.arr.data, target, cnt, OID, self.arr.n)
        ms = (time.perf_counter() - t0) * 1000.0
        if idx < 0:
            return Hasil("linear_search", "M3 - linear",
                         "%s tidak ditemukan.\n%s perbandingan (seluruh data dilewati)." % (
                             target, fmt_int(cnt.perbandingan)), (), (), ms)
        rec = self.arr.data[idx]
        teks = "Ditemukan pada indeks %s.\n%s perbandingan." % (fmt_int(idx), fmt_int(cnt.perbandingan))
        return Hasil("linear_search", "M3 - linear", teks, KOLOM_DETAIL, baris_detail(rec), ms,
                     "Data tidak perlu terurut, tetapi setiap pesanan diperiksa satu per satu dari depan.")

    def _indeks_oid(self):
        """Daftar terurut oid; dibangun sekali dengan merge sort, dibangun ulang bila data M1 berubah."""
        if self.idx_oid is not None and self.idx_versi == self.versi:
            return self.idx_oid, 0.0, False
        salinan = [None] * self.arr.n
        for i in range(self.arr.n):
            salinan[i] = self.arr.data[i]
        t0 = time.perf_counter()
        self.idx_oid = merge_sort(salinan, OID, Pencacah())
        ms = (time.perf_counter() - t0) * 1000.0
        self.idx_versi = self.versi
        return self.idx_oid, ms, True

    def cari_binary(self, a):
        target = self._oid_target(a[0])
        daftar, ms_bangun, baru = self._indeks_oid()
        cnt = Pencacah()
        t0 = time.perf_counter()
        idx = binary_search(daftar, target, cnt, OID, len(daftar))
        ms = (time.perf_counter() - t0) * 1000.0
        if baru:
            baris1 = "Daftar terurut oid dibangun sekali dengan merge sort, %s." % fmt_ms(ms_bangun)
        else:
            baris1 = "Memakai daftar terurut oid yang sudah dibangun (data M1 tidak berubah)."
        if idx < 0:
            return Hasil("binary_search", "M3 - binary",
                         "%s\n%s tidak ditemukan. %d perbandingan." % (baris1, target, cnt.perbandingan),
                         (), (), ms)
        rec = daftar[idx]
        teks = "%s\nDitemukan pada baris ke-%s dari %s baris.\n%d perbandingan, bandingkan dengan linear search." % (
            baris1, fmt_int(idx + 1), fmt_int(len(daftar)), cnt.perbandingan)
        return Hasil("binary_search", "M3 - binary", teks, KOLOM_DETAIL, baris_detail(rec), ms,
                     "Setiap perbandingan membuang separuh sisa daftar. Syaratnya daftar sudah terurut menurut oid; ongkos pengurutan tidak gratis.")

    # ---------------------------------------------------------- statistik
    def stats(self):
        m = self.mgr
        rows = Array()
        rows.append(("array_len", fmt_int(self.arr.n)))
        rows.append(("array_kapasitas", fmt_int(self.arr.kap)))
        rows.append(("array_total_salinan", fmt_int(self.arr.salinan)))
        rows.append(("linkedlist_len", fmt_int(self.ll.n)))
        st = m.stats()
        for i in range(len(st)):
            rows.append((st[i][0], fmt_int(st[i][1])))
        h = m.history()
        tampil = min(len(h), 20)
        for i in range(tampil):
            rows.append(("riwayat %d" % (len(h) - i), h[len(h) - 1 - i]))
        return Hasil("stats", "M2 - stats", "Statistik struktur data dan riwayat undo (terbaru di atas).",
                     KOLOM_DETAIL, rows.ke_list(), 0.0)
