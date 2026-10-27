# TLS Certificate Hygiene Study: 65 Major Indian and Global Websites

**Author:** Aparna Mohanty
**Date:** October 2026

## Motivation

In October 2026, two security incidents highlighted how certificate and key management failures can affect trust at scale. First, India's eMudhra, a government-recognized certificate authority, disclosed that eight of its intermediate TLS certificates had been issued with cryptographically weak private keys, some recoverable by testing a few hundred possible values, after sitting unnoticed in production for roughly a year and a half. Second, the State Bank of India confirmed a leak exposing personal details of nearly 4,000 customers. Both cases raised a basic question: how carefully is certificate infrastructure actually maintained across websites people rely on every day?

This project investigates that question directly, not by analyzing either incident forensically, but by independently testing TLS certificate configuration and hygiene across a broad sample of Indian and international websites: banks, government portals, e-commerce platforms, global tech companies, research institutions, and certificate authorities themselves.

## Research Question

How consistent is TLS certificate hygiene, measured through expiry management, key strength, signature algorithm choice, and chain completeness, across a representative sample of high-traffic websites, and are there any live, concrete misconfigurations currently in production?

## Method

A Python script connected directly to 65 websites on port 443, retrieved each site's live TLS certificate using Python's `ssl` module, and parsed it with the `cryptography` library to extract:

- Issuing Certificate Authority and organization
- Public key algorithm and key size
- Signature algorithm
- Validity period and days remaining until expiry
- Whether the full certificate chain could be independently verified

Sites were chosen across six categories to allow comparison: Indian banks, Indian government services, Indian e-commerce, global technology companies, global finance, research institutions, certificate authorities, and a small set of smaller companies for contrast. All data was collected on a single date in October 2026 using only publicly available connection metadata; no site was probed beyond a standard TLS handshake, and no attempt was made to access any system beyond what a normal browser visit would do.

## Findings

**Overall:** 60 of 65 sites (92%) returned a fully valid, verifiable certificate with modern key strength and signature algorithms. No RSA keys below 2048 bits and no outdated SHA-1 or MD5 signatures were found anywhere in the sample, indicating that baseline certificate hygiene is strong across most of the organizations tested.

**Finding 1: An expired certificate on India's national COVID-19 vaccination portal.**
`cowin.gov.in` returned a certificate that had already passed its expiry date at the time of testing. CoWIN still holds vaccination and identity records for over a billion registered individuals, and has previously faced separate, disputed claims of data exposure. An expired certificate does not itself indicate a breach, but it is a direct, observable sign of reduced maintenance on infrastructure that continues to hold large volumes of sensitive personal data after the acute phase of the pandemic has passed. This is the clearest, most concrete finding in the study.

**Finding 2: Incomplete certificate chains at three Max Planck Institutes.**
`mpi-inf.mpg.de`, `mpi-sws.org`, and `mpi-sp.org` each failed independent chain verification with "unable to get local issuer certificate," indicating the servers do not send their full intermediate certificate chain. This is a known, named category of TLS misconfiguration, distinct from a security breach: most browsers tolerate it through cached or auto-fetched intermediates, but strict clients (including this study's own verification) cannot complete the trust chain without it. It is a small, fixable operational gap, interesting mainly because it appears at research institutions whose own work concerns secure and dependable systems.

**Key size and algorithm distribution across all 65 sites:**

![Key size distribution](chart_key_sizes.png)

**Days until certificate expiry across all 65 sites (red line = 30-day warning threshold):**

![Expiry distribution](chart_expiry_distribution.png)

**Finding 3: Uneven renewal timing.**
Four sites had fewer than 30 days remaining before expiry at the time of testing, including `stanford.edu` at 11 days. While not a failure, this reflects inconsistent operational discipline around certificate renewal, even among well-resourced institutions, and is a useful secondary signal of where small failures like CoWIN's could emerge if left unaddressed.

**Minor note:** `epfindia.gov.in` timed out during testing and could not be evaluated; this is recorded as inconclusive rather than a finding.

## Discussion

None of these findings constitute an attack or a confirmed data breach. Taken together, though, they show that certificate maintenance, a basic and largely automatable part of web security, is inconsistently applied even among government and research institutions. The eMudhra incident showed that a single flawed step in key generation can go undetected for over a year; the CoWIN finding in this study shows a parallel, lower-severity pattern: infrastructure holding sensitive data can quietly fall out of maintenance once public attention moves elsewhere. Both point to the same underlying lesson: certificate and key hygiene requires ongoing, automated monitoring, not one-time setup, particularly for systems that continue to hold sensitive data long after their moment of public urgency has passed.

## Limitations

This study examined only publicly observable certificate metadata at a single point in time; it did not assess server configuration, revocation status, or whether intermediate certificates were cached elsewhere. The sample, while varied, is not statistically representative of the wider web. Findings describe the state of each site only at the moment of testing and may have changed since.

## Files

- `collect_certificates.py` — data collection script
- `analyze_certificates.py` — analysis and chart generation
- `certificates.csv` — raw collected data
- `chart_key_sizes.png`, `chart_expiry_distribution.png` — summary charts
