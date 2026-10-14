"""M3: Sort & Search. Semua algoritma menghitung PERBANDINGAN lewat Pencacah.

- insertion_sort : di tempat, stabil (geser hanya bila kunci kiri > kunci sekarang), O(n^2)
- merge_sort     : stabil (ambil kiri bila kunci kiri <= kunci kanan), O(n log n),
                   bottom-up supaya tidak rekursif; sisa kedua sisi disalin
- linear_search  : O(n), data boleh acak
- binary_search  : O(log n), data HARUS terurut menurut kunci yang dicari

Kunci = indeks kolom pada tuple pesanan. Nilai None (belum selesai) dianggap
paling besar sehingga jatuh di ujung belakang.
"""

OID, PELANGGAN, RESTO, MENU, HARGA, PRIORITAS, T_MASUK, T_SELESAI, STATUS = 0, 1, 2, 3, 4, 5, 6, 7, 8
BESAR = 10 ** 12


class Pencacah:
    """Pencacah sederhana yang dititipkan ke algoritma."""

    def __init__(self):
        self.perbandingan = 0
        self.pemindahan = 0


def _kunci_list(A, kunci):
    n = len(A)
    K = [None] * n
    for i in range(n):
        v = A[i][kunci]
        if v is None:
            v = BESAR
        K[i] = v
    return K


def insertion_sort(A, kunci, cnt):
    """Urutkan list A di tempat. Mengembalikan A."""
    K = _kunci_list(A, kunci)
    n = len(A)
    cmp = 0
    pindah = 0
    for i in range(1, n):
        x = A[i]
        kx = K[i]
        j = i - 1
        while j >= 0:
            cmp += 1
            if K[j] > kx:            # '>' bukan '>=' -> stabil
                A[j + 1] = A[j]
                K[j + 1] = K[j]
                pindah += 1
                j -= 1
            else:
                break
        if j + 1 != i:
            A[j + 1] = x
            K[j + 1] = kx
            pindah += 1
    cnt.perbandingan += cmp
    cnt.pemindahan += pindah
    return A


def merge_sort(A, kunci, cnt):
    """Kembalikan list BARU yang terurut; A tidak diubah."""
    n = len(A)
    src_r = [None] * n
    for i in range(n):
        src_r[i] = A[i]
    src_k = _kunci_list(A, kunci)
    dst_r = [None] * n
    dst_k = [None] * n
    cmp = 0
    pindah = 0
    w = 1
    while w < n:
        lo = 0
        while lo < n:
            mid = lo + w
            if mid > n:
                mid = n
            hi = lo + 2 * w
            if hi > n:
                hi = n
            i = lo
            j = mid
            o = lo
            while i < mid and j < hi:
                cmp += 1
                if src_k[i] <= src_k[j]:     # '<=' -> elemen kiri didahulukan -> stabil
                    dst_r[o] = src_r[i]
                    dst_k[o] = src_k[i]
                    i += 1
                else:
                    dst_r[o] = src_r[j]
                    dst_k[o] = src_k[j]
                    j += 1
                o += 1
            while i < mid:                    # sisa kiri jangan sampai hilang
                dst_r[o] = src_r[i]
                dst_k[o] = src_k[i]
                i += 1
                o += 1
            while j < hi:                     # sisa kanan
                dst_r[o] = src_r[j]
                dst_k[o] = src_k[j]
                j += 1
                o += 1
            pindah += hi - lo
            lo += 2 * w
        src_r, dst_r = dst_r, src_r
        src_k, dst_k = dst_k, src_k
        w *= 2
    cnt.perbandingan += cmp
    cnt.pemindahan += pindah
    return src_r


def linear_search(A, target, cnt, kunci=OID, n=None):
    """Indeks pertama yang cocok, atau -1. Satu perbandingan per elemen dilewati."""
    if n is None:
        n = len(A)
    cmp = 0
    for i in range(n):
        cmp += 1
        if A[i][kunci] == target:
            cnt.perbandingan += cmp
            return i
    cnt.perbandingan += cmp
    return -1


def binary_search(A, target, cnt, kunci=OID, n=None):
    """A harus terurut menaik menurut `kunci`. Indeks atau -1."""
    if n is None:
        n = len(A)
    lo = 0
    hi = n - 1
    cmp = 0
    while lo <= hi:                           # '<=' bukan '<'
        mid = (lo + hi) // 2
        v = A[mid][kunci]
        cmp += 1
        if v == target:
            cnt.perbandingan += cmp
            return mid
        if v < target:                        # perbandingan tiga arah dihitung satu
            lo = mid + 1
        else:
            hi = mid - 1
    cnt.perbandingan += cmp
    return -1
