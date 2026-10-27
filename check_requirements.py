"""
check_requirements.py
Run this first to confirm your machine is ready for the certificate study project.
Usage: python check_requirements.py
"""

import sys

print("=" * 50)
print("Checking your setup for the Certificate Study project")
print("=" * 50)

# 1. Check Python version
print(f"\n1. Python version: {sys.version}")
major, minor = sys.version_info[0], sys.version_info[1]
if major == 3 and minor >= 8:
    print("   OK - Python 3.8+ detected")
else:
    print("   WARNING - Recommend Python 3.8 or higher")

# 2. Check built-in ssl and socket modules (these come with Python, no install needed)
try:
    import ssl
    import socket
    print("\n2. ssl and socket modules: OK (built into Python)")
except ImportError as e:
    print(f"\n2. ssl/socket modules: MISSING - {e}")
    print("   This is unusual since these are built-in. Check your Python install.")

# 3. Check 'cryptography' package (needs pip install)
try:
    import cryptography
    print(f"\n3. cryptography package: OK (version {cryptography.__version__})")
except ImportError:
    print("\n3. cryptography package: NOT INSTALLED")
    print("   Run this in your VS Code terminal:")
    print("   pip install cryptography")

# 4. Check 'pandas' (useful for saving/analyzing the CSV later)
try:
    import pandas as pd
    print(f"\n4. pandas package: OK (version {pd.__version__})")
except ImportError:
    print("\n4. pandas package: NOT INSTALLED")
    print("   Run this in your VS Code terminal:")
    print("   pip install pandas")

# 5. Check 'matplotlib' (for the charts in Day 2)
try:
    import matplotlib
    print(f"\n5. matplotlib package: OK (version {matplotlib.__version__})")
except ImportError:
    print("\n5. matplotlib package: NOT INSTALLED")
    print("   Run this in your VS Code terminal:")
    print("   pip install matplotlib")

# 6. Test actual internet connectivity + certificate fetch (the real test)
print("\n6. Testing a live certificate fetch from google.com ...")
try:
    hostname = "google.com"
    port = 443
    context = ssl.create_default_context()
    with socket.create_connection((hostname, port), timeout=5) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            cert = ssock.getpeercert()
            print("   OK - Successfully connected and fetched a real certificate")
            print(f"   Example field - Subject: {cert.get('subject')}")
except Exception as e:
    print(f"   FAILED - {e}")
    print("   Check your internet connection or firewall settings.")

print("\n" + "=" * 50)
print("If everything above says OK, you're ready to start.")
print("If anything is NOT INSTALLED, run the pip install commands shown,")
print("then re-run this script to confirm.")
print("=" * 50)
