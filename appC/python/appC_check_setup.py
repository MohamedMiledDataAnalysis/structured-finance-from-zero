"""Appendix C - checks that Python, pandas and the data folder work.
Run from the book folder:
  python3 appC/python/appC_check_setup.py data"""
import sys
from pathlib import Path
import pandas as pd

data = Path(sys.argv[1])
t = pd.read_csv(data / "thames_residential_2027_1_tape.csv")
r = pd.read_csv(data / "rhein_auto_2027_1_tape.csv")
print("Thames loans  :", len(t))
print("Thames balance:", f"{t.current_balance.sum():.2f}")
print("Rhein loans   :", len(r))
print("Rhein balance :", f"{r.current_balance.sum():.2f}")
print("Setup OK")
