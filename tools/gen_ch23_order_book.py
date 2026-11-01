"""Chapter 23 - synthetic order book for Thames Residential 2027-1 (fictional investors).
Run from the book folder:  python3 tools/gen_ch23_order_book.py
Writes data/ch23_thames_order_book.csv (seed 20270304)."""
import random, csv
random.seed(20270304)
# class: (offered £, final margin bp, limit choices that drop out, n orders, size menu £m)
CLASSES = {
 "A": (525_350_000, 62, [63, 64, 65], 34, [5, 10, 15, 20, 25, 30, 40, 50, 60, 75]),
 "B": (30_210_000, 110, [112, 115], 12, [2, 3, 5, 7, 10]),
 "C": (18_145_000, 150, [152, 155], 10, [2, 3, 4, 5]),
 "D": (12_065_000, 220, [222, 225], 9, [2, 3, 4, 5]),
 "E": (9_025_000, 350, [355, 360], 8, [2, 3, 4]),
}
TYPES = [("Asset manager", 0.42), ("Bank treasury", 0.28),
         ("Insurer or pension", 0.15), ("Hedge fund", 0.15)]
def pick_type():
    u, c = random.random(), 0
    for t, p in TYPES:
        c += p
        if u < c: return t
    return TYPES[-1][0]
rows = []
for cls, (size, final, drops, n, menu) in CLASSES.items():
    for i in range(1, n + 1):
        t = pick_type()
        if cls in "DE" and t == "Bank treasury": t = "Hedge fund"
        lim = random.choice(drops) if random.random() < 0.22 else ""
        hh, mm = 8 + (i * 7) // 60, (i * 7) % 60 + random.randint(0, 6)
        rows.append({"order_id": f"{cls}{i:02d}", "note_class": cls, "investor_type": t,
                     "order_gbp": random.choice(menu) * 1_000_000,
                     "limit_margin_bp": lim, "time_entered": f"{hh:02d}:{min(mm,59):02d}"})
with open("data/ch23_thames_order_book.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(len(rows), "orders written")
