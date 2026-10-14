"""Jalankan: python -m unittest discover -s tests -v   (dari root proyek)"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.m1_pesanan import Array, LinkList
from backend.m2_antrean import (ke_postfix, hitung, AntreanNaif, AntreanMelingkar,
                                ManajerAntrean)
from backend.m3_laporan import (Pencacah, insertion_sort, merge_sort,
                                linear_search, binary_search)
from backend.data import pisah_csv


def hit(e):
    return hitung(ke_postfix(e))


class TestM1(unittest.TestCase):
    def _cek(self, S):
        for i in range(10):
            S.append(i)
        self.assertEqual(S.tambah_vip(100), 0)
        self.assertEqual(S.tambah_prioritas(200), 5)
        self.assertEqual(S.tambah_reguler(300), 12)
        self.assertEqual(S.ke_list(), [100, 0, 1, 2, 3, 200, 4, 5, 6, 7, 8, 9, 300])
        self.assertEqual(S.remove(0), 100)
        self.assertEqual(S.remove(S.n - 1), 300)
        self.assertEqual(S.get(4), 200)
        self.assertEqual(S.n, 11)

    def test_array(self):
        self._cek(Array())

    def test_linklist(self):
        self._cek(LinkList())

    def test_array_tumbuh_dan_salinan(self):
        a = Array(4)
        for i in range(1000):
            a.append(i)
        self.assertEqual(a.ke_list(), list(range(1000)))
        self.assertLess(a.salinan, 2000)      # amortized O(1): total salinan < 2n

    def test_ll_tail_setelah_hapus_belakang(self):
        l = LinkList()
        for i in range(3):
            l.append(i)
        l.remove(2)
        l.append(9)
        self.assertEqual(l.ke_list(), [0, 1, 9])

    def test_batas(self):
        with self.assertRaises(IndexError):
            Array().get(0)
        with self.assertRaises(IndexError):
            LinkList().remove(0)


class TestM2(unittest.TestCase):
    def test_postfix(self):
        self.assertEqual(ke_postfix("( 3 * 12000 ) + ( 2 * 8500 ) - 5000").teks(),
                         "3 12000 * 2 8500 * + 5000 -")
        self.assertEqual(hit("( 3 * 12000 ) + ( 2 * 8500 ) - 5000"), 48000)

    def test_urutan_pop(self):
        self.assertEqual(hit("10 - 3 - 2"), 5)           # kiri ke kanan
        self.assertEqual(hit("100 / 5 / 2"), 10)
        self.assertEqual(hit("20 - ( 3 + 2 ) * 2"), 10)
        self.assertEqual(hit("((1+2)*(3+4))-5"), 16)     # kurung bersarang, tanpa spasi
        self.assertEqual(hit("2 + 3 * 4"), 14)

    def test_galat(self):
        for e in ("( 1 + 2", "1 + 2 )", "1 +", "1 / 0", "abc", ""):
            with self.assertRaises(ValueError):
                hit(e)

    def _antrean(self, q):
        for i in range(3):
            q.enqueue(i)
        self.assertEqual(q.dequeue(), 0)
        self.assertEqual(q.dequeue(), 1)
        for i in range(3, 6):
            q.enqueue(i)
        out = []
        while len(q) > 0:
            out.append(q.dequeue())
        self.assertEqual(out, [2, 3, 4, 5])
        self.assertIsNone(q.dequeue())

    def test_naif(self):
        self._antrean(AntreanNaif())

    def test_melingkar_putar_K4(self):
        q = AntreanMelingkar(4)
        for i in range(3):
            q.enqueue(i)
        q.dequeue()
        q.dequeue()
        for i in range(3, 6):
            q.enqueue(i)
        self.assertEqual(q.K, 4)                          # tidak tumbuh, penunjuk berputar
        self.assertEqual([q.isi(i) for i in range(len(q))], [2, 3, 4, 5])
        self._antrean(AntreanMelingkar(4))

    def test_melingkar_penuh_tumbuh(self):
        q = AntreanMelingkar(4)
        for i in range(10):
            q.enqueue(i)
        self.assertEqual([q.dequeue() for _ in range(10)], list(range(10)))

    def test_undo_redo(self):
        m = ManajerAntrean()
        for i in range(10):
            m.isi_awal(("O-%d" % i,))
        m.enqueue(("X",))
        daftar, _ = m.dequeue("circular", 4)
        self.assertEqual(len(m.mel), 7)
        m.undo_last()                                      # kembalikan 4 ke DEPAN
        self.assertEqual([m.mel.isi(i)[0] for i in range(4)], ["O-0", "O-1", "O-2", "O-3"])
        m.redo_last()
        self.assertEqual(len(m.mel), 7)
        m.undo_last()
        m.undo_last()                                      # batalkan enqueue
        self.assertEqual(len(m.mel), 10)
        self.assertEqual(len(m.naif), 10)
        m.enqueue(("Y",))                                  # aksi baru -> redo kosong
        self.assertEqual(m.redo.ukuran(), 0)
        self.assertIsNone(m.redo_last())
        self.assertEqual(len(m.history()), 1)

    def test_undo_dequeue_naif(self):
        m = ManajerAntrean()
        for i in range(5):
            m.isi_awal((i,))
        m.dequeue("naif", 3)
        m.undo_last()
        self.assertEqual([m.naif.isi(i)[0] for i in range(5)], [0, 1, 2, 3, 4])


class TestM3(unittest.TestCase):
    def _data(self):
        # (oid, ..., harga) dengan harga duplikat untuk uji stabil
        h = [5, 3, 5, 1, 3, 9, 1, 5, 2, 2]
        out = [None] * len(h)
        for i in range(len(h)):
            out[i] = ("O-%02d" % i, "p", "r", "m", h[i], 3, 0, None, "DONE")
        return out

    def test_sort_stabil_dan_sama(self):
        d = self._data()
        a = [x for x in d]
        b = merge_sort(d, 4, Pencacah())
        insertion_sort(a, 4, Pencacah())
        self.assertEqual(a, b)
        for i in range(len(b) - 1):
            self.assertLessEqual(b[i][4], b[i + 1][4])
            if b[i][4] == b[i + 1][4]:
                self.assertLess(b[i][0], b[i + 1][0])      # urutan asli terjaga

    def test_kasus_sort(self):
        import random
        random.seed(1)
        for n in (0, 1, 2, 7, 100):
            acak = [(i, "", "", "", random.randint(0, 9), 0, 0, None, "") for i in range(n)]
            for data in (acak, merge_sort(acak, 4, Pencacah()),
                         merge_sort(acak, 4, Pencacah())[::-1],
                         [(i, "", "", "", 5, 0, 0, None, "") for i in range(n)]):
                m = merge_sort(data, 4, Pencacah())
                ins = [x for x in data]
                insertion_sort(ins, 4, Pencacah())
                self.assertEqual(m, ins)
                self.assertEqual(len(m), n)
                for i in range(n - 1):
                    self.assertLessEqual(m[i][4], m[i + 1][4])

    def test_pertumbuhan_perbandingan(self):
        import random
        random.seed(2)
        def acak(n):
            return [(i, "", "", "", random.randint(0, 10 ** 6), 0, 0, None, "") for i in range(n)]
        hasil = []
        for n in (1000, 2000):
            d = acak(n)
            c1, c2 = Pencacah(), Pencacah()
            insertion_sort([x for x in d], 4, c1)
            merge_sort(d, 4, c2)
            hasil.append((c1.perbandingan, c2.perbandingan))
        self.assertGreater(hasil[1][0] / hasil[0][0], 3.5)  # ~4x
        self.assertLess(hasil[1][1] / hasil[0][1], 2.3)     # ~2x

    def test_search(self):
        A = [("O-%03d" % i,) for i in range(0, 100, 2)]
        c = Pencacah()
        self.assertEqual(binary_search(A, "O-000", c), 0)
        self.assertEqual(binary_search(A, "O-098", c), 49)
        self.assertEqual(binary_search(A, "O-050", c), 25)
        self.assertEqual(binary_search(A, "O-051", c), -1)
        self.assertEqual(binary_search(A, "O-999", c), -1)
        self.assertEqual(binary_search([], "O-001", c), -1)
        self.assertEqual(linear_search(A, "O-098", c), 49)
        self.assertEqual(linear_search(A, "O-001", c), -1)
        c2 = Pencacah()
        linear_search(A, "O-098", c2)
        self.assertEqual(c2.perbandingan, 50)


class TestCSV(unittest.TestCase):
    def test_koma_dalam_kutip(self):
        p = pisah_csv('O-000004,"Oskar Puspita, S.Sos",kafe-teknik,nasi-padang,25000,2,29632,,CANCEL')
        self.assertEqual(len(p), 9)
        self.assertEqual(p[1], "Oskar Puspita, S.Sos")
        self.assertEqual(p[7], "")


if __name__ == "__main__":
    unittest.main()
