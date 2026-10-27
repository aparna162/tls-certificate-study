"""
collect_certificates.py
Connects to each website in SITES, fetches its live TLS certificate,
and saves key details (issuer, key size, algorithm, expiry) to a CSV.

Usage: python collect_certificates.py
Output: certificates.csv
"""

import ssl
import socket
import csv
from datetime import datetime, timezone
from cryptography import x509
from cryptography.hazmat.backends import default_backend

# ---------------------------------------------------------------
# STEP 1: Your list of sites.
# Mix of categories as planned: banks, government, e-commerce, misc.
# Edit/expand this list freely — aim for 50-80 total.
# ---------------------------------------------------------------
SITES = [
    # Indian Banks
    "sbi.co.in", "hdfcbank.com", "icicibank.com", "axisbank.com", "pnbindia.in",
    "kotak.com", "indusind.com", "idfcfirstbank.com", "yesbank.in", "bankofbaroda.in",
    # Indian Government
    "www.india.gov.in", "www.incometax.gov.in", "uidai.gov.in", "digilocker.gov.in", "mygov.in",
    "cowin.gov.in", "passportindia.gov.in", "epfindia.gov.in", "gst.gov.in", "rbi.org.in",
    # Indian E-commerce
    "flipkart.com", "amazon.in", "myntra.com", "nykaa.com", "meesho.com",
    "ajio.com", "bigbasket.com", "zomato.com", "swiggy.com", "paytm.com",
    # Global Tech
    "google.com", "microsoft.com", "apple.com", "github.com", "cloudflare.com",
    "mozilla.org", "wikipedia.org", "reddit.com", "linkedin.com", "twitter.com",
    # Global Finance
    "paypal.com", "stripe.com", "visa.com", "mastercard.com", "americanexpress.com",
    # Research / Academic (includes the chain-verification finding sites)
    "mpi-inf.mpg.de", "mpi-sws.org", "mpi-sp.org", "arxiv.org", "huggingface.co",
    "mit.edu", "stanford.edu", "ox.ac.uk", "cam.ac.uk", "iisc.ac.in",
    # Security / Certificate-related (relevant to your topic)
    "letsencrypt.org", "digicert.com", "globalsign.com", "sectigo.com", "emudhra.com",
    # Smaller / lesser-known sites (good for contrast)
    "zoho.com", "freshworks.com", "razorpay.com", "cred.club", "groww.in",
]

TIMEOUT_SECONDS = 5


def get_certificate_info(hostname, port=443):
    """
    Connects to hostname:port, fetches the live certificate,
    and returns a dict of extracted fields. Returns None on failure
    (with the reason printed) so one bad site doesn't stop the run.
    """
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=TIMEOUT_SECONDS) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                # Get the raw certificate in DER format and parse it properly
                der_cert = ssock.getpeercert(binary_form=True)
                cert = x509.load_der_x509_certificate(der_cert, default_backend())

                # --- Extract fields ---
                issuer = cert.issuer.rfc4514_string()
                subject = cert.subject.rfc4514_string()

                public_key = cert.public_key()
                key_algorithm = type(public_key).__name__.replace("PublicKey", "")
                try:
                    key_size = public_key.key_size
                except AttributeError:
                    key_size = "N/A"  # e.g. some Ed25519 keys report differently

                signature_algorithm = cert.signature_algorithm_oid._name

                not_before = cert.not_valid_before_utc
                not_after = cert.not_valid_after_utc
                now = datetime.now(timezone.utc)
                days_until_expiry = (not_after - now).days

                return {
                    "hostname": hostname,
                    "issuer": issuer,
                    "subject": subject,
                    "key_algorithm": key_algorithm,
                    "key_size": key_size,
                    "signature_algorithm": signature_algorithm,
                    "not_before": not_before.strftime("%Y-%m-%d"),
                    "not_after": not_after.strftime("%Y-%m-%d"),
                    "days_until_expiry": days_until_expiry,
                    "status": "OK",
                }

    except ssl.SSLCertVerificationError as e:
        # This is a genuine finding, not just a script error:
        # the server's certificate chain could not be verified
        # (often an incomplete intermediate chain on the server's side).
        print(f"  CHAIN VERIFICATION FAILED: {hostname} -> {e}")
        return {
            "hostname": hostname,
            "issuer": "N/A",
            "subject": "N/A",
            "key_algorithm": "N/A",
            "key_size": "N/A",
            "signature_algorithm": "N/A",
            "not_before": "N/A",
            "not_after": "N/A",
            "days_until_expiry": "N/A",
            "status": f"CHAIN_VERIFICATION_FAILED: {str(e)[:100]}",
        }

    except Exception as e:
        print(f"  FAILED: {hostname} -> {e}")
        return {
            "hostname": hostname,
            "issuer": "N/A",
            "subject": "N/A",
            "key_algorithm": "N/A",
            "key_size": "N/A",
            "signature_algorithm": "N/A",
            "not_before": "N/A",
            "not_after": "N/A",
            "days_until_expiry": "N/A",
            "status": f"FAILED: {str(e)[:100]}",
        }


def main():
    results = []
    total = len(SITES)

    print(f"Starting collection for {total} sites...\n")

    for i, site in enumerate(SITES, start=1):
        print(f"[{i}/{total}] Checking {site} ...")
        info = get_certificate_info(site)
        results.append(info)

    # Save to CSV
    fieldnames = [
        "hostname", "issuer", "subject", "key_algorithm", "key_size",
        "signature_algorithm", "not_before", "not_after",
        "days_until_expiry", "status",
    ]
    with open("certificates.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    succeeded = sum(1 for r in results if r["status"] == "OK")
    failed = total - succeeded
    print(f"\nDone. {succeeded} succeeded, {failed} failed.")
    print("Saved results to certificates.csv")


if __name__ == "__main__":
    main()
