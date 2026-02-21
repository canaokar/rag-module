---
doc_id: "POL-015"
title: "IT Security and Cyber Risk Policy"
doc_type: "Operational Risk Framework"
effective_date: "2024-10-01"
regulatory_body: "FCA"
jurisdiction: "UK"
version: "3.1"
status: "Active"
review_date: "2025-10-01"
---

# IT Security and Cyber Risk Policy

## 1. Purpose and Scope

This policy establishes the information security requirements for all Bank
systems, networks, and data. It applies to all employees, contractors, and
third parties with access to Bank information assets.

## 2. Access Management

2.1 Access to production systems must be granted on a least-privilege basis
and reviewed every 60 business days.

2.2 Privileged access accounts must use multi-factor authentication and
session recording. Maximum session duration is 8 hours.

2.3 User accounts must be disabled within 1 business day of an employee's
departure or role change that removes the access requirement.

2.4 Service accounts must have their credentials rotated at least every 90
days and must not be used for interactive logon.

## 3. Network Security

3.1 All external network connections must pass through managed firewalls with
documented rule sets reviewed at least quarterly.

3.2 Internal network segmentation must isolate critical systems (core banking,
payments, treasury) from general corporate systems.

3.3 All data in transit across public networks must be encrypted using TLS 1.2
or higher.

3.4 Wireless networks must use WPA3 encryption. Guest wireless networks must
be isolated from the corporate network.

## 4. Vulnerability Management

4.1 Critical vulnerabilities must be patched within 7 business days of
disclosure. High-severity vulnerabilities must be patched within 21 business
days.

4.2 Penetration tests must be conducted annually for all externally facing
applications and after significant changes.

4.3 Vulnerability scanning must be performed at least monthly for all
internet-facing systems and quarterly for internal systems.

## 5. Data Security

5.1 All data must be classified according to the Bank's Data Classification
Standard: Public, Internal, Confidential, or Restricted.

5.2 Restricted and Confidential data must be encrypted at rest using AES-256
or equivalent.

5.3 Removable media must not be used to store Restricted or Confidential data
without prior approval from the CISO.

## 6. Incident Response

6.1 Security incidents must be reported to the CISO within 1 business day
of detection.

6.2 A post-incident review must be completed within 15 business days of
incident closure, with lessons learned shared across the organisation.

6.3 The Cyber Incident Response Plan must be tested at least twice per year,
including at least one unannounced simulation.

## 7. Security Awareness Training

7.1 All staff must complete information security awareness training within 30
days of joining and annually thereafter.

7.2 Phishing simulation exercises must be conducted at least quarterly, with
results reported to the CISO.

## 8. Governance and Oversight

The Chief Information Security Officer (CISO) is responsible for the day-to-day
implementation of this policy. The CISO reports to the Board Risk Committee at
least quarterly on the Bank's cyber risk posture.

## 9. Review and Amendment

This document must be reviewed at least annually or following a material
cyber incident. The review must be documented and signed off by the CISO and
approved by the Board Risk Committee.
