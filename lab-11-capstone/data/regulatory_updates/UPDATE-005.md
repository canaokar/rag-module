---
doc_id: UPDATE-005
title: Updated Data Protection Requirements for Cloud Services
effective_date: 2024-06-01
regulatory_body: FCA
update_type: guidance_note
affects:
  - Data Protection
  - IT Security
  - Outsourcing
---

# Updated Data Protection Requirements for Cloud Services

The Financial Conduct Authority has issued updated guidance on data protection requirements for firms using cloud computing services to process or store customer data. This guidance supplements existing outsourcing rules and addresses specific risks associated with cloud deployments.

## Data Residency

Customer data classified as sensitive or restricted must be stored within approved jurisdictions. For UK-regulated firms, primary data storage must be within the UK or a jurisdiction that the UK has recognised as providing adequate data protection. Firms must maintain a data residency register showing where each category of customer data is stored.

## Encryption Standards

All customer data stored in cloud environments must be encrypted at rest using AES-256 or equivalent encryption. Data in transit must be protected using TLS 1.2 or higher. Encryption keys must be managed by the firm, not by the cloud service provider, unless the provider holds appropriate certifications.

## Access Controls

Firms must implement identity and access management controls that enforce the principle of least privilege. Access to customer data in cloud environments must require multi-factor authentication. All access events must be logged and retained for at least two years.

## Incident Response

Cloud-specific incident response procedures must be documented and tested at least annually. Firms must ensure that their cloud service provider agreements include notification obligations requiring the provider to report any security incidents within 24 hours of detection.

## Exit Strategy

Firms must maintain a documented exit strategy for each cloud service provider, ensuring that customer data can be migrated to an alternative provider or brought in-house within 90 days. Exit strategies must be reviewed annually and tested at least every three years.
