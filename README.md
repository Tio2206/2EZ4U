# 2EZ4U APP

Engine backend layanan antar makanan mini. Struktur data dan algoritma ditulis sendiri
(tanpa `dict`, `set`, `sorted`, `.sort()`, `heapq`, `bisect`, `collections`, literal `{}`).

## Cara menjalankan
```
python app.py                            # butuh Python 3.11+ dan Tkinter
python -m unittest discover -s tests -v  # uji backend tanpa UI
```
Tekan **Load** dulu (membaca `data/pesanan.csv`, 200.000 baris).

## Isi
| Milestone | Berkas | Isi |
|---|---|---|
| M1 | `backend/m1_pesanan.py` | `Array` (tumbuh 2x), `LinkList` (head + tail); tambah REGULER / PRIORITAS / VIP, lihat, hapus |
| M2 | `backend/m2_antrean.py` | `Tumpukan`, `ke_postfix`, `hitung`, `AntreanNaif`, `AntreanMelingkar`, undo/redo |
| M3 | `backend/m3_laporan.py` | `insertion_sort`, `merge_sort`, `linear_search`, `binary_search` + `Pencacah` perbandingan |
| - | `backend/layanan.py` | fasad: satu pintu `jalankan(menu, argumen)` untuk UI |
| - | `frontend/ui.py`, `app.py` | jendela Tkinter |

## Keputusan desain
- **Array**: petak `[None] * kap`, penuh -> petak baru 2x lalu salin (amortized O(1)).
- **PRIORITAS** disisipkan di indeks `n // 2`, **VIP** di indeks 0, **REGULER** di belakang.
- **Antrean melingkar** memakai `count` (bukan `front == rear`, ambigu antara kosong dan penuh).
  Bila penuh, antrean **tumbuh 2x** (disalin berurutan dari `front`). `dequeue` saat kosong mengembalikan `None`.
- **Undo** menyimpan *daftar* pesanan yang di-dequeue (bukan hitungannya). Undo DEQUEUE mengembalikan ke
  DEPAN. Redo mengerjakan aksi aslinya. Aksi baru mengosongkan redo. Aksi M1 (tambah/hapus) ikut tercatat.
- **Insertion sort** memakai `>` dan **merge sort** memakai `<=` supaya keduanya stabil. Insertion sort
  menolak > 20.000 baris. Kunci `selesai` yang kosong dianggap paling besar (jatuh di belakang).
- **Binary search** memakai daftar terpisah yang terurut menurut `oid`, dibangun sekali dengan merge sort
  dan dibangun ulang bila array M1 berubah. Ongkos pembangunan ditampilkan.
- Setiap sort/search melaporkan **jumlah perbandingan**; binary search dihitung satu per langkah.

## Hasil ukur (mesin dev, data acak harga, bagian awal data)
| n | insertion: perbandingan | merge: perbandingan |
|---:|---:|---:|
| 2.000 | 962.430 | 19.269 |
| 4.000 | 3.831.520 | 42.417 |

n x2 -> insertion ~4x, merge ~2x. Linear search `O-137442`: 137.443 perbandingan; binary: 16.
