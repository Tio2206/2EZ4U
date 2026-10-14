"""Pembaca CSV buatan sendiri (menangani nama ber-koma dalam tanda kutip) + format tampilan."""

from backend.m1_pesanan import Array


def pisah_csv(baris):
    if '"' not in baris:
        return baris.split(",")
    buf = [None] * 16
    k = 0
    cur = ""
    kutip = False
    i = 0
    n = len(baris)
    while i < n:
        c = baris[i]
        if kutip:
            if c == '"':
                if i + 1 < n and baris[i + 1] == '"':
                    cur += '"'
                    i += 1
                else:
                    kutip = False
            else:
                cur += c
        elif c == '"':
            kutip = True
        elif c == ",":
            buf[k] = cur
            k += 1
            cur = ""
        else:
            cur += c
        i += 1
    buf[k] = cur
    k += 1
    return buf[:k]


def muat_pesanan(path):
    """Baca CSV -> Array of tuple (oid, pelanggan, resto, menu, harga, prioritas, t_masuk, t_selesai, status)."""
    arr = Array(1024)
    pertama = True
    with open(path, encoding="utf-8", newline="") as f:
        for baris in f:
            baris = baris.rstrip("\r\n")
            if pertama:
                pertama = False
                continue
            if baris == "":
                continue
            p = pisah_csv(baris)
            sel = int(p[7]) if p[7] != "" else None
            arr.append((p[0], p[1], p[2], p[3], int(p[4]), int(p[5]), int(p[6]), sel, p[8]))
    return arr


# ---------------------------------------------------------------- format
def fmt_int(n):
    s = str(abs(int(n)))
    hasil = ""
    c = 0
    for i in range(len(s) - 1, -1, -1):
        hasil = s[i] + hasil
        c += 1
        if c % 3 == 0 and i > 0:
            hasil = "." + hasil
    if n < 0:
        hasil = "-" + hasil
    return hasil


def fmt_ms(ms):
    if ms >= 1000:
        t = "%.2f s" % (ms / 1000.0)
    else:
        t = "%.2f ms" % ms
    return t.replace(".", ",")


def fmt_jam(detik):
    if detik is None:
        return "-"
    return "%02d:%02d:%02d" % ((detik // 3600) % 24, (detik % 3600) // 60, detik % 60)


def fmt_rupiah(v):
    if isinstance(v, float) and v != int(v):
        return ("Rp %.2f" % v).replace(".", ",")
    return "Rp " + fmt_int(int(v))
