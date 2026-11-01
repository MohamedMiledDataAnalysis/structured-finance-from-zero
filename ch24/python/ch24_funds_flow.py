"""Chapter 24 - closing-day funds flow of Thames Residential
2027-1 (18 March 2027). Upfront costs are illustrative.
Run from the book folder:
  python3 ch24/python/ch24_funds_flow.py"""
from decimal import Decimal as D, ROUND_HALF_UP

def r2(x):
    return D(x).quantize(D("0.01"), rounding=ROUND_HALF_UP)

NOTES = {"A": "553000000.00", "B": "31800000.00",
         "C": "19100000.00", "D": "12700000.00",
         "E": "9500000.00", "Z": "9571146.31"}
COMM = {"A": D("0.0015")}          # B-E: 0.35%
SUB_LOAN = D("9391500.00")
PRICE = D("635671146.31")          # initial consideration
COSTS = {"Rating agency 1": "340000.00",
         "Rating agency 2": "310000.00",
         "Carver Whitlock LLP": "900000.00",
         "Pemberton Hale LLP": "132000.00",
         "Harper & Lane LLP (AUP)": "157532.50",
         "STS Verification Partners": "72000.00",
         "Albion Trustee Services": "18000.00",
         "Albion Bank plc (agency)": "6000.00",
         "Meridian Corporate Services": "12000.00",
         "FCA and LSE fees": "21385.00"}

placed = retained = comm = D("0")
for c, amt in NOTES.items():
    a = D(amt)
    if c == "Z":                   # Kingsbridge keeps all of Z
        retained += a
        continue
    keep = r2(a * D("0.05"))       # 5% vertical slice
    placed += a - keep
    retained += keep
    comm += r2((a - keep) * COMM.get(c, D("0.0035")))
costs = sum(D(v) for v in COSTS.values())

def show(label, x):
    print(f"{label:<38}{x:>16,}")

print("SOURCES AND USES")
show("Placed notes (95% of A-E)", placed)
show("Retained notes (5% of A-E, all of Z)", retained)
show("Subordinated loan", SUB_LOAN)
src = placed + retained + SUB_LOAN
show("Total sources", src)
show("Initial consideration to Kingsbridge", PRICE)
show("General reserve fund", SUB_LOAN)
use = PRICE + SUB_LOAN
show("Total uses", use)
show("Sources - uses", src - use)

print("\nHOW THE CONSIDERATION IS SETTLED")
show("Initial consideration", PRICE)
show("less retained notes delivered", -retained)
show("less JLM commission (deducted)", -comm)
show("less third-party costs paid", -costs)
show("less subordinated loan (netted)", -SUB_LOAN)
net = PRICE - retained - comm - costs - SUB_LOAN
show("Net cash to Kingsbridge", net)

print("\nTRANSACTION ACCOUNT ON 18 MARCH 2027")
show("JLMs pay in, net of commission", placed - comm)
show("Paid to third parties", -costs)
show("Paid to Kingsbridge", -net)
bal = placed - comm - costs - net
show("Balance after settlement", bal)
show("Check: balance - reserve required", bal - SUB_LOAN)
