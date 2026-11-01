"""Chapter 13 - run the Thames waterfall engine on ILLUSTRATIVE
quarters (not real Thames IPDs; Chapter 26 runs the real ones).
Run from the book folder:
  python3 ch13/python/ch13_waterfall.py \
      data/ch13_illustrative_scenarios.csv [scenario ...]
Default scenarios: normal stressed.
"""
import sys
import csv
from decimal import Decimal as D
from waterfall import (State, Period, CLASSES, run_ipd,
                       run_post_enforcement)


def load(path):
    """Read the scenario file into {name: (State, Period)}."""
    out = {}
    with open(path) as f:
        for r in csv.DictReader(f):
            st = State(
                pool=D(r["pool"]),
                notes={c: D(r[f"note_{c}"]) for c in CLASSES},
                pdl={c: D(r[f"pdl_{c}"]) for c in CLASSES},
                deferred={c: D(r.get(f"def_{c}", "0.00"))
                          for c in CLASSES},
                reserve=D(r["reserve"]),
                subloan=D(r["subloan"]),
                subloan_unpaid_int=D(r["subloan_unpaid_int"]))
            pe = Period(
                days=int(r["days"]), sonia=D(r["sonia"]),
                revenue=D(r["revenue"]),
                sched_principal=D(r["sched_principal"]),
                prepayments=D(r["prepayments"]),
                recoveries=D(r["recoveries"]),
                losses=D(r["losses"]),
                swap_notional=D(r["swap_notional"]))
            out[r["scenario"]] = (st, pe)
    return out


def m(x):
    return f"{x + 0:,.2f}"


def table(results):
    """Rows (label, [value per scenario]) for side-by-side
    printing of one or two scenarios."""
    rs = list(results.values())
    i = [r["info"] for r in rs]
    st = [r["state"] for r in rs]
    out = [("Available revenue receipts",
            [x["available_revenue"] for x in i]),
           (" of which swap receipt",
            [x["swap_receipt"] for x in i]),
           ("Principal addition amounts", [x["paa"] for x in i]),
           ("REVENUE PAID", None)]
    for k, (item, label, _, _) in enumerate(rs[0]["lines"]):
        out.append((f"({item:>2}) {label[:24]}",
                    [r["lines"][k][3] for r in rs]))
    out.append(("PRINCIPAL PAID", None))
    for k, (label, _) in enumerate(rs[0]["principal"]):
        lab = label.replace(" principal", "")
        lab = lab.replace("Principal addition amounts",
                          "Principal addition amts")
        out.append(("     " + lab,
                    [r["principal"][k][1] for r in rs]))
    out.append(("AFTER THE IPD", None))
    out.append(("Reserve fund", [x.reserve for x in st]))
    out.append(("Reserve draw", [x["reserve_draw"] for x in i]))
    for c in CLASSES:
        out.append((f"Class {c} note", [x.notes[c] for x in st]))
    out.append(("PDL balance (all classes)",
                [sum(x.pdl.values()) for x in st]))
    out.append(("Deferred interest B-E",
                [sum(x.deferred.values()) for x in st]))
    out.append(("Pool balance", [x.pool for x in st]))
    out.append(("Check: notes - PDL - pool",
                [x["balance_check"] for x in i]))
    out.append(("Senior interest unpaid",
                [x["eod_interest"] for x in i]))
    return out


def show(results):
    print(f"{'ILLUSTRATIVE quarter':<29}" + "".join(
        f"{n:>16}" for n in results))
    for label, vals in table(results):
        if vals is None:
            print(label)
            continue
        cells = "".join(f"{v!s:>16}" if isinstance(v, bool)
                        else f"{m(v):>16}" for v in vals)
        print(f"{label:<29}{cells}")


if __name__ == "__main__":
    sc = load(sys.argv[1])
    names = sys.argv[2:] or ["normal", "stressed"]
    if names == ["enforcement"]:
        st, pe = sc["severe"]
        r = run_post_enforcement(st, pe)
        print("Severe quarter, post-enforcement (ILLUSTRATIVE)")
        print(f"{'All receipts and reserve':<29}"
              f"{m(r['pot_start']):>32}")
        print(f"{'':<29}{'due':>16}{'paid':>16}")
        for label, due, paid in r["lines"]:
            print(f"{label:<29}{m(due):>16}{m(paid):>16}")
    else:
        show({n: run_ipd(*sc[n]) for n in names})
