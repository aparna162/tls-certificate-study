"""
analyze_certificates.py
Reads certificates.csv (from collect_certificates.py) and produces:
  - A printed summary of key findings
  - Two charts saved as PNG files: key size distribution, expiry timeline

Usage: python analyze_certificates.py
"""

import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------------------------
# Load data
# ---------------------------------------------------------------
df = pd.read_csv("certificates.csv")
total = len(df)

ok = df[df["status"] == "OK"].copy()
failed = df[df["status"] != "OK"].copy()

print("=" * 60)
print("CERTIFICATE STUDY - SUMMARY OF FINDINGS")
print("=" * 60)

print(f"\nTotal sites tested: {total}")
print(f"Successfully verified: {len(ok)}")
print(f"Failed / flagged: {len(failed)}")

# ---------------------------------------------------------------
# 1. Breakdown of failures by type
# ---------------------------------------------------------------
print("\n--- Failure / Flag Breakdown ---")
for _, row in failed.iterrows():
    status = row["status"]
    if "expired" in status.lower():
        tag = "EXPIRED CERTIFICATE"
    elif "CHAIN_VERIFICATION_FAILED" in status:
        tag = "INCOMPLETE CHAIN"
    elif "timed out" in status.lower():
        tag = "TIMEOUT (no response)"
    else:
        tag = "OTHER"
    print(f"  [{tag}] {row['hostname']}")

# ---------------------------------------------------------------
# 2. Certificates expiring soon (within 30 days)
# ---------------------------------------------------------------
ok["days_until_expiry"] = pd.to_numeric(ok["days_until_expiry"], errors="coerce")
soon = ok[ok["days_until_expiry"] <= 30].sort_values("days_until_expiry")

print(f"\n--- Certificates Expiring Within 30 Days ({len(soon)} sites) ---")
for _, row in soon.iterrows():
    print(f"  {row['hostname']}: {row['days_until_expiry']} days left")

# ---------------------------------------------------------------
# 3. Key size / algorithm breakdown
# ---------------------------------------------------------------
print("\n--- Key Algorithm + Size Breakdown ---")
key_counts = ok.groupby(["key_algorithm", "key_size"]).size().reset_index(name="count")
for _, row in key_counts.iterrows():
    print(f"  {row['key_algorithm']} {row['key_size']}-bit: {row['count']} sites")

# Flag any weak keys (RSA under 2048)
weak_keys = ok[(ok["key_algorithm"] == "RSA") & (pd.to_numeric(ok["key_size"], errors="coerce") < 2048)]
if len(weak_keys) > 0:
    print(f"\n  WARNING: {len(weak_keys)} sites with weak RSA keys (<2048 bit):")
    for _, row in weak_keys.iterrows():
        print(f"    {row['hostname']}: RSA {row['key_size']}-bit")
else:
    print("\n  No weak RSA keys (<2048 bit) found. Good baseline across the sample.")

# ---------------------------------------------------------------
# 4. Signature algorithm check (flag old SHA-1/MD5)
# ---------------------------------------------------------------
old_algos = ok[ok["signature_algorithm"].str.contains("sha1|md5", case=False, na=False)]
if len(old_algos) > 0:
    print(f"\n  WARNING: {len(old_algos)} sites using outdated signature algorithms (SHA-1/MD5):")
    for _, row in old_algos.iterrows():
        print(f"    {row['hostname']}: {row['signature_algorithm']}")
else:
    print("  No outdated signature algorithms (SHA-1/MD5) found. All sites use SHA-256 or stronger.")

# ---------------------------------------------------------------
# 5. Which Certificate Authorities (issuers) are most common
# ---------------------------------------------------------------
print("\n--- Most Common Certificate Issuers ---")
# Extract just the "O=" (organization) part of the issuer for readability
def extract_org(issuer_str):
    for part in str(issuer_str).split(","):
        if part.strip().startswith("O="):
            return part.strip()[2:]
    return issuer_str

ok["issuer_org"] = ok["issuer"].apply(extract_org)
issuer_counts = ok["issuer_org"].value_counts().head(10)
for org, count in issuer_counts.items():
    print(f"  {org}: {count} sites")

# ---------------------------------------------------------------
# CHART 1: Key size / algorithm distribution (bar chart)
# ---------------------------------------------------------------
plt.figure(figsize=(8, 5))
key_labels = key_counts["key_algorithm"] + " " + key_counts["key_size"].astype(str) + "-bit"
plt.bar(key_labels, key_counts["count"], color="steelblue")
plt.title("Certificate Key Type and Size Distribution")
plt.xlabel("Key Algorithm / Size")
plt.ylabel("Number of Sites")
plt.xticks(rotation=20)
plt.tight_layout()
plt.savefig("chart_key_sizes.png")
print("\nSaved chart_key_sizes.png")

# ---------------------------------------------------------------
# CHART 2: Days until expiry (histogram)
# ---------------------------------------------------------------
plt.figure(figsize=(8, 5))
plt.hist(ok["days_until_expiry"].dropna(), bins=15, color="seagreen", edgecolor="black")
plt.title("Distribution of Days Until Certificate Expiry")
plt.xlabel("Days Until Expiry")
plt.ylabel("Number of Sites")
plt.axvline(30, color="red", linestyle="--", label="30-day warning line")
plt.legend()
plt.tight_layout()
plt.savefig("chart_expiry_distribution.png")
print("Saved chart_expiry_distribution.png")

print("\n" + "=" * 60)
print("Done. Use the printed summary + the two PNG charts in your report.")
print("=" * 60)
