"""
generate_corpus.py -- Generates ~30 synthetic banking policy documents as Markdown
files with YAML frontmatter. Uses only Python standard library.

Usage:
    python generate_corpus.py

Output:
    ../data/policies/POL-XXX-title-slug.md  (relative to this script)
"""

import os
import random
import textwrap
from datetime import date, timedelta

random.seed(42)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "data", "policies"))

# ---------------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------------

DOC_TYPES = [
    "AML Policy",
    "Lending Policy",
    "Operational Risk Framework",
    "Product Terms",
    "Data Protection Policy",
    "Compliance Procedure",
]

REGULATORY_BODIES = ["FCA", "PRA", "EBA", "Basel Committee", "Internal Governance"]

JURISDICTIONS = ["UK", "EU", "Global"]

# ---------------------------------------------------------------------------
# Document templates -- each entry is (title, doc_type, body_builder)
# where body_builder is a callable returning a list of (heading, paragraphs).
# We define enough templates to cover 30 documents with variety.
# ---------------------------------------------------------------------------


def _money(lo=1000, hi=5000000):
    """Return a realistic GBP amount string."""
    amount = random.randint(lo, hi)
    if amount >= 1000000:
        return "GBP {:,.0f}".format(amount)
    return "GBP {:,.0f}".format(amount)


def _days(lo=5, hi=90):
    return "{} business days".format(random.randint(lo, hi))


def _percent(lo=1, hi=25):
    return "{}%".format(round(random.uniform(lo, hi), 1))


def _date_str(year_lo=2024, year_hi=2026):
    y = random.randint(year_lo, year_hi)
    m = random.randint(1, 12)
    d = random.randint(1, 28)
    return date(y, m, d).isoformat()


def _clause(major, minor=None, sub=None):
    parts = [str(major)]
    if minor is not None:
        parts.append(str(minor))
    if sub is not None:
        parts.append(str(sub))
    return ".".join(parts)


# ---------------------------------------------------------------------------
# Section-content generators (each returns list of paragraphs)
# ---------------------------------------------------------------------------


def _aml_overview():
    return [
        (
            "1. Purpose and Scope",
            [
                "This policy establishes the framework for preventing money laundering, "
                "terrorist financing, and proliferation financing across all business units. "
                "It applies to all employees, contractors, and third-party agents operating "
                "on behalf of the Bank.",
                "The Bank is committed to complying with the Money Laundering, Terrorist "
                "Financing and Transfer of Funds (Information on the Payer) Regulations 2017 "
                "(as amended), the Proceeds of Crime Act 2002, and all relevant FCA and JMLSG guidance.",
            ],
        ),
        (
            "2. Customer Due Diligence",
            [
                "{c} Standard CDD must be completed before establishing a business relationship "
                "or carrying out an occasional transaction exceeding {m}.".format(
                    c=_clause(2, 1), m=_money(10000, 15000)
                ),
                "{c} Enhanced Due Diligence (EDD) is required where the customer is a Politically "
                "Exposed Person (PEP), resides in a high-risk jurisdiction, or where the transaction "
                "profile presents elevated risk indicators.".format(c=_clause(2, 2)),
                "{c} Simplified Due Diligence may be applied only where a documented risk assessment "
                "demonstrates low risk, subject to ongoing monitoring. The risk assessment must be "
                "reviewed at intervals not exceeding {d}.".format(
                    c=_clause(2, 3), d=_days(30, 90)
                ),
            ],
        ),
        (
            "3. Transaction Monitoring",
            [
                "{c} All transactions above {m} must be screened against internal watchlists "
                "and the HM Treasury consolidated sanctions list within {d} of execution.".format(
                    c=_clause(3, 1), m=_money(5000, 25000), d=_days(1, 3)
                ),
                "{c} The automated monitoring system shall flag transactions that deviate by "
                "more than {p} from the customer's established behavioural profile.".format(
                    c=_clause(3, 2), p=_percent(15, 40)
                ),
                "{c} Suspicious Activity Reports (SARs) must be filed with the National Crime "
                "Agency within {d} of detection. The MLRO must approve all SARs before submission.".format(
                    c=_clause(3, 3), d=_days(1, 5)
                ),
            ],
        ),
        (
            "4. Record Keeping",
            [
                "{c} CDD records must be retained for a minimum of 5 years from the end of the "
                "business relationship or the date of the occasional transaction.".format(
                    c=_clause(4, 1)
                ),
                "{c} Transaction records, including supporting documentation, must be maintained "
                "in a retrievable format for at least 7 years.".format(c=_clause(4, 2)),
            ],
        ),
        (
            "5. Training and Awareness",
            [
                "{c} All relevant staff must complete AML awareness training within {d} of "
                "joining the Bank and annually thereafter.".format(
                    c=_clause(5, 1), d=_days(15, 30)
                ),
                "{c} Role-specific training on transaction monitoring, sanctions screening, and "
                "SAR reporting must be completed by all first-line and second-line staff.".format(
                    c=_clause(5, 2)
                ),
            ],
        ),
    ]


def _kyc_procedures():
    return [
        (
            "1. Introduction",
            [
                "This procedure details the operational steps for conducting Know Your Customer "
                "(KYC) checks in accordance with the Bank's AML Policy. All customer-facing "
                "teams must follow these procedures without exception.",
            ],
        ),
        (
            "2. Identity Verification",
            [
                "{c} For natural persons, identity must be verified using at least one government-issued "
                "photo identification document (passport, national identity card, or driving licence) "
                "and one proof of address dated within the last {d}.".format(
                    c=_clause(2, 1), d=_days(60, 90)
                ),
                "{c} For corporate entities, the following must be obtained: certificate of "
                "incorporation, memorandum and articles of association, register of directors "
                "and shareholders, and evidence of registered address.".format(c=_clause(2, 2)),
                "{c} Beneficial owners holding {p} or more of the entity must be identified "
                "and verified to the same standard as natural persons.".format(
                    c=_clause(2, 3), p=_percent(10, 25)
                ),
            ],
        ),
        (
            "3. Risk Classification",
            [
                "{c} Each customer must be assigned a risk rating of Low, Medium, or High "
                "based on the Bank's Customer Risk Assessment Matrix (CRAM).".format(
                    c=_clause(3, 1)
                ),
                "{c} Factors influencing the risk rating include: country of residence, "
                "nature of business, expected transaction volume, source of funds, and PEP status.",
                "{c} High-risk customers require approval from the Head of Compliance before "
                "onboarding and must be reviewed every {d}.".format(
                    c=_clause(3, 3), d=_days(60, 180)
                ),
            ],
        ),
        (
            "4. Ongoing Monitoring",
            [
                "{c} Customer profiles must be reviewed at intervals determined by their risk "
                "classification: Low -- every 36 months; Medium -- every 12 months; High -- every 6 months.".format(
                    c=_clause(4, 1)
                ),
                "{c} Any material change in the customer's circumstances triggers an immediate "
                "review and potential re-classification.".format(c=_clause(4, 2)),
            ],
        ),
    ]


def _lending_general():
    return [
        (
            "1. Purpose",
            [
                "This policy governs the origination, underwriting, and management of lending "
                "products across the Bank's retail and commercial portfolios. It ensures that "
                "credit risk is taken within approved risk appetite boundaries.",
            ],
        ),
        (
            "2. Credit Approval Authority",
            [
                "{c} Individual lending up to {m} may be approved by Branch Managers.".format(
                    c=_clause(2, 1), m=_money(50000, 250000)
                ),
                "{c} Lending between {lo} and {hi} requires approval from the Regional "
                "Credit Committee.".format(
                    c=_clause(2, 2),
                    lo=_money(250000, 500000),
                    hi=_money(1000000, 2000000),
                ),
                "{c} Exposures exceeding {m} must be referred to the Group Credit Committee "
                "with a full credit memorandum and independent risk opinion.".format(
                    c=_clause(2, 3), m=_money(2000000, 5000000)
                ),
            ],
        ),
        (
            "3. Underwriting Standards",
            [
                "{c} Debt-to-income ratio must not exceed {p} for unsecured personal loans.".format(
                    c=_clause(3, 1), p=_percent(35, 50)
                ),
                "{c} Loan-to-value ratio for residential mortgages must not exceed {p} "
                "without mortgage insurance.".format(
                    c=_clause(3, 2), p=_percent(75, 90)
                ),
                "{c} Commercial lending must be supported by cashflow projections covering "
                "the full term of the facility plus a {p} stress buffer.".format(
                    c=_clause(3, 3), p=_percent(10, 25)
                ),
            ],
        ),
        (
            "4. Collateral and Security",
            [
                "{c} Acceptable collateral includes: real property, term deposits, listed "
                "securities (subject to a haircut of {p}), and government bonds.".format(
                    c=_clause(4, 1), p=_percent(10, 30)
                ),
                "{c} Independent valuations are required for all real property collateral "
                "exceeding {m}.".format(c=_clause(4, 2), m=_money(500000, 1000000)),
            ],
        ),
        (
            "5. Portfolio Monitoring",
            [
                "{c} The credit portfolio must be reviewed monthly, with concentration limits "
                "monitored against the approved Risk Appetite Statement.".format(
                    c=_clause(5, 1)
                ),
                "{c} Early warning indicators must be reported to the Chief Risk Officer "
                "within {d} of detection.".format(c=_clause(5, 2), d=_days(2, 5)),
            ],
        ),
    ]


def _oprisk_framework():
    return [
        (
            "1. Framework Overview",
            [
                "This framework establishes the Bank's approach to identifying, assessing, "
                "monitoring, and mitigating operational risk. It aligns with Basel Committee "
                "principles and PRA supervisory expectations.",
                "Operational risk is defined as the risk of loss resulting from inadequate or "
                "failed internal processes, people, systems, or from external events.",
            ],
        ),
        (
            "2. Risk Identification",
            [
                "{c} All business units must maintain a Risk and Control Self-Assessment (RCSA) "
                "updated at least quarterly.".format(c=_clause(2, 1)),
                "{c} Loss events exceeding {m} must be reported to the Operational Risk "
                "function within {d}.".format(
                    c=_clause(2, 2), m=_money(5000, 50000), d=_days(1, 3)
                ),
                "{c} Near-miss events with a potential impact above {m} must also be recorded "
                "in the loss event database.".format(
                    c=_clause(2, 3), m=_money(10000, 100000)
                ),
            ],
        ),
        (
            "3. Key Risk Indicators",
            [
                "{c} Each business unit must define and monitor at least 5 Key Risk Indicators "
                "(KRIs) relevant to their operational profile.".format(c=_clause(3, 1)),
                "{c} KRI breaches must be escalated to the Head of Operational Risk within {d} "
                "and reported to the Risk Committee at its next scheduled meeting.".format(
                    c=_clause(3, 2), d=_days(1, 3)
                ),
            ],
        ),
        (
            "4. Business Continuity",
            [
                "{c} Critical business processes must have documented Business Continuity Plans "
                "(BCPs) tested at least annually.".format(c=_clause(4, 1)),
                "{c} Recovery Time Objectives (RTOs) for critical systems must not exceed "
                "{d}.".format(c=_clause(4, 2), d=_days(1, 5)),
                "{c} Disaster recovery tests must be conducted at least twice per year with "
                "results reported to the Board Risk Committee.".format(c=_clause(4, 3)),
            ],
        ),
    ]


def _data_protection():
    return [
        (
            "1. Scope and Legal Basis",
            [
                "This policy sets out the Bank's obligations under the UK General Data "
                "Protection Regulation (UK GDPR) and the Data Protection Act 2018. It applies "
                "to all processing of personal data by or on behalf of the Bank.",
                "The Bank acts as a data controller for customer and employee personal data "
                "and as a data processor where it processes data on behalf of third parties "
                "under contractual arrangements.",
            ],
        ),
        (
            "2. Data Processing Principles",
            [
                "{c} Personal data must be processed lawfully, fairly, and transparently. "
                "A valid lawful basis must be identified and documented before processing begins.".format(
                    c=_clause(2, 1)
                ),
                "{c} Data must be collected for specified, explicit, and legitimate purposes "
                "and not further processed in a manner incompatible with those purposes.".format(
                    c=_clause(2, 2)
                ),
                "{c} Data minimisation: only personal data that is adequate, relevant, and "
                "limited to what is necessary for the stated purpose may be collected.".format(
                    c=_clause(2, 3)
                ),
            ],
        ),
        (
            "3. Data Subject Rights",
            [
                "{c} Subject Access Requests must be fulfilled within {d} of receipt. "
                "The DPO must be consulted for complex or sensitive requests.".format(
                    c=_clause(3, 1), d=_days(20, 30)
                ),
                "{c} The right to erasure must be facilitated unless processing is required "
                "for compliance with a legal obligation or the establishment, exercise, or "
                "defence of legal claims.".format(c=_clause(3, 2)),
            ],
        ),
        (
            "4. Data Breach Management",
            [
                "{c} Any suspected personal data breach must be reported to the DPO within "
                "{d} of discovery.".format(c=_clause(4, 1), d=_days(1, 2)),
                "{c} Breaches likely to result in a risk to the rights and freedoms of "
                "individuals must be notified to the ICO within 72 hours.".format(
                    c=_clause(4, 2)
                ),
                "{c} Affected data subjects must be notified without undue delay where the "
                "breach is likely to result in a high risk to their rights and freedoms.".format(
                    c=_clause(4, 3)
                ),
            ],
        ),
        (
            "5. International Transfers",
            [
                "{c} Personal data must not be transferred outside the UK unless adequate "
                "safeguards are in place, such as Standard Contractual Clauses approved by "
                "the ICO or a binding adequacy decision.".format(c=_clause(5, 1)),
                "{c} All international transfers must be recorded in the Bank's Record of "
                "Processing Activities (ROPA).".format(c=_clause(5, 2)),
            ],
        ),
    ]


def _product_terms():
    return [
        (
            "1. General Terms",
            [
                "These terms and conditions govern the provision of banking products and "
                "services by the Bank to eligible customers. By opening an account or "
                "applying for a product, the customer agrees to be bound by these terms.",
            ],
        ),
        (
            "2. Account Opening",
            [
                "{c} Accounts may be opened by individuals aged 18 or over who are resident "
                "in the United Kingdom and who satisfy the Bank's identification requirements.".format(
                    c=_clause(2, 1)
                ),
                "{c} A minimum initial deposit of {m} is required for premium current accounts. "
                "Standard accounts have no minimum deposit requirement.".format(
                    c=_clause(2, 2), m=_money(1000, 5000)
                ),
            ],
        ),
        (
            "3. Interest and Charges",
            [
                "{c} The annual interest rate on savings accounts is variable and currently "
                "set at {p}. The Bank will provide at least {d} notice of any rate change.".format(
                    c=_clause(3, 1), p=_percent(1, 5), d=_days(14, 30)
                ),
                "{c} Overdraft interest is charged at {p} per annum (variable). An arranged "
                "overdraft limit of up to {m} is available subject to credit assessment.".format(
                    c=_clause(3, 2), p=_percent(15, 25), m=_money(1000, 10000)
                ),
                "{c} Returned item fees of {m} will be charged for each payment rejected "
                "due to insufficient funds.".format(
                    c=_clause(3, 3), m=_money(5, 35)
                ),
            ],
        ),
        (
            "4. Closing an Account",
            [
                "{c} Either party may close the account by providing at least {d} written "
                "notice. The Bank reserves the right to close an account immediately where "
                "fraud or financial crime is suspected.".format(
                    c=_clause(4, 1), d=_days(14, 30)
                ),
            ],
        ),
    ]


def _compliance_procedure():
    return [
        (
            "1. Purpose",
            [
                "This procedure establishes the process for identifying, escalating, and "
                "resolving compliance breaches and regulatory obligations. It supports the "
                "Bank's Compliance Policy and applies to all business areas.",
            ],
        ),
        (
            "2. Regulatory Horizon Scanning",
            [
                "{c} The Compliance team must conduct horizon scanning at least monthly to "
                "identify new or amended regulatory requirements applicable to the Bank.".format(
                    c=_clause(2, 1)
                ),
                "{c} Identified changes must be assessed for impact within {d} and assigned "
                "to a responsible owner.".format(c=_clause(2, 2), d=_days(10, 20)),
            ],
        ),
        (
            "3. Breach Reporting",
            [
                "{c} All compliance breaches, however minor, must be reported through the "
                "Compliance Incident Management System within {d} of discovery.".format(
                    c=_clause(3, 1), d=_days(1, 3)
                ),
                "{c} Material breaches with a financial impact exceeding {m} or regulatory "
                "notification obligations must be escalated to the Chief Compliance Officer "
                "immediately.".format(c=_clause(3, 2), m=_money(50000, 500000)),
                "{c} Root cause analysis must be completed within {d} and remediation actions "
                "documented in the breach register.".format(
                    c=_clause(3, 3), d=_days(15, 30)
                ),
            ],
        ),
        (
            "4. Compliance Monitoring Programme",
            [
                "{c} An annual Compliance Monitoring Programme must be approved by the Board "
                "Audit Committee and cover all material regulatory obligations.".format(
                    c=_clause(4, 1)
                ),
                "{c} Monitoring reviews must be risk-based, with high-risk areas reviewed at "
                "least quarterly and medium-risk areas reviewed semi-annually.".format(
                    c=_clause(4, 2)
                ),
            ],
        ),
        (
            "5. Regulatory Reporting",
            [
                "{c} All regulatory returns must be submitted by the deadline specified by "
                "the relevant regulator. A schedule of reporting obligations must be maintained "
                "by the Compliance team.".format(c=_clause(5, 1)),
                "{c} Draft returns must be reviewed by a second qualified individual before "
                "submission. Any errors identified post-submission must be corrected and "
                "resubmitted within {d}.".format(c=_clause(5, 2), d=_days(3, 10)),
            ],
        ),
    ]


# ---------------------------------------------------------------------------
# Extra topic variations to reach 30 documents
# ---------------------------------------------------------------------------


def _sanctions_screening():
    return [
        (
            "1. Policy Statement",
            [
                "The Bank is committed to complying with all applicable sanctions regimes, "
                "including those imposed by HM Treasury, the EU, the United Nations, and OFAC. "
                "This policy applies to all transactions, products, and customer relationships.",
            ],
        ),
        (
            "2. Screening Requirements",
            [
                "{c} All new customers must be screened against the consolidated sanctions list "
                "before account opening.".format(c=_clause(2, 1)),
                "{c} Existing customers must be rescreened within {d} of any update to the "
                "sanctions lists.".format(c=_clause(2, 2), d=_days(1, 3)),
                "{c} All payment transactions exceeding {m} must be screened in real time "
                "against sanctions lists.".format(
                    c=_clause(2, 3), m=_money(100, 1000)
                ),
            ],
        ),
        (
            "3. Escalation and Reporting",
            [
                "{c} Confirmed sanctions matches must be escalated to the MLRO within {d} "
                "and reported to OFSI where required.".format(
                    c=_clause(3, 1), d=_days(1, 2)
                ),
                "{c} False positive rates must be monitored and reported to the Compliance "
                "Committee quarterly. The target false positive rate is below {p}.".format(
                    c=_clause(3, 2), p=_percent(1, 5)
                ),
            ],
        ),
    ]


def _fraud_prevention():
    return [
        (
            "1. Scope",
            [
                "This policy covers the prevention, detection, investigation, and reporting "
                "of fraud, including internal fraud, external fraud, cyber fraud, and "
                "authorised push payment (APP) fraud.",
            ],
        ),
        (
            "2. Prevention Controls",
            [
                "{c} Multi-factor authentication must be enforced for all customer-facing "
                "digital channels.".format(c=_clause(2, 1)),
                "{c} Transactions exceeding {m} via online banking must trigger a "
                "step-up authentication challenge.".format(
                    c=_clause(2, 2), m=_money(1000, 10000)
                ),
                "{c} Employee access to payment systems must follow the principle of least "
                "privilege and be recertified every {d}.".format(
                    c=_clause(2, 3), d=_days(60, 90)
                ),
            ],
        ),
        (
            "3. Investigation and Recovery",
            [
                "{c} All suspected fraud cases must be referred to the Financial Crime "
                "Investigations Unit within {d} of detection.".format(
                    c=_clause(3, 1), d=_days(1, 3)
                ),
                "{c} Recovery actions must commence within {d} of confirming fraud, "
                "including freezing of accounts and notification to law enforcement.".format(
                    c=_clause(3, 2), d=_days(1, 5)
                ),
            ],
        ),
    ]


def _third_party_risk():
    return [
        (
            "1. Purpose",
            [
                "This policy establishes the framework for managing risks arising from "
                "the Bank's reliance on third-party service providers, including outsourced "
                "functions and cloud service providers.",
            ],
        ),
        (
            "2. Due Diligence",
            [
                "{c} A risk assessment must be completed for all new third-party engagements "
                "with an annual contract value exceeding {m}.".format(
                    c=_clause(2, 1), m=_money(50000, 200000)
                ),
                "{c} Critical and important outsourcing arrangements must be approved by the "
                "Board or a delegated committee before execution.".format(c=_clause(2, 2)),
            ],
        ),
        (
            "3. Ongoing Monitoring",
            [
                "{c} Service Level Agreements (SLAs) must be reviewed at least quarterly. "
                "Persistent SLA breaches must be escalated to the Chief Operating Officer.".format(
                    c=_clause(3, 1)
                ),
                "{c} An annual on-site or virtual assessment must be conducted for all "
                "critical third parties.".format(c=_clause(3, 2)),
            ],
        ),
        (
            "4. Exit Planning",
            [
                "{c} An exit strategy must be documented for all critical outsourcing "
                "arrangements, including a maximum transition period of {d}.".format(
                    c=_clause(4, 1), d=_days(60, 180)
                ),
            ],
        ),
    ]


def _model_risk():
    return [
        (
            "1. Framework Scope",
            [
                "This framework governs the development, validation, implementation, and "
                "ongoing monitoring of quantitative models used across the Bank, including "
                "credit scoring, market risk, and operational risk models.",
            ],
        ),
        (
            "2. Model Development",
            [
                "{c} All new models must be developed in accordance with the Bank's Model "
                "Development Standards and approved by the Model Risk Committee.".format(
                    c=_clause(2, 1)
                ),
                "{c} Development documentation must include: model purpose, methodology, "
                "data sources, assumptions, limitations, and performance benchmarks.".format(
                    c=_clause(2, 2)
                ),
            ],
        ),
        (
            "3. Independent Validation",
            [
                "{c} All models must undergo independent validation before deployment. "
                "Validation must be performed by a team separate from development.".format(
                    c=_clause(3, 1)
                ),
                "{c} Material models must be revalidated at least annually or when "
                "performance deteriorates beyond the threshold of {p}.".format(
                    c=_clause(3, 2), p=_percent(5, 15)
                ),
            ],
        ),
        (
            "4. Model Inventory",
            [
                "{c} A central model inventory must be maintained, recording model owner, "
                "validation status, materiality tier, and next review date.".format(
                    c=_clause(4, 1)
                ),
            ],
        ),
    ]


def _capital_adequacy():
    return [
        (
            "1. Regulatory Context",
            [
                "This policy outlines the Bank's approach to maintaining adequate capital "
                "in accordance with CRD V/CRR II requirements and PRA Pillar 2 expectations. "
                "The Bank targets a Common Equity Tier 1 (CET1) ratio of at least {p}.".format(
                    p=_percent(10, 14)
                ),
            ],
        ),
        (
            "2. Capital Planning",
            [
                "{c} The Internal Capital Adequacy Assessment Process (ICAAP) must be "
                "updated at least annually and approved by the Board.".format(
                    c=_clause(2, 1)
                ),
                "{c} Stress testing must be conducted under at least three scenarios: "
                "baseline, adverse, and severely adverse.".format(c=_clause(2, 2)),
                "{c} Capital buffers must be maintained above regulatory minimums by at "
                "least {p} to absorb unexpected losses.".format(
                    c=_clause(2, 3), p=_percent(1, 3)
                ),
            ],
        ),
        (
            "3. Capital Allocation",
            [
                "{c} Risk-weighted assets must be allocated to business units for performance "
                "measurement using the Bank's internal economic capital model.".format(
                    c=_clause(3, 1)
                ),
                "{c} New product launches with estimated RWA impact exceeding {m} require "
                "Capital Committee approval.".format(
                    c=_clause(3, 2), m=_money(1000000, 5000000)
                ),
            ],
        ),
    ]


def _conduct_risk():
    return [
        (
            "1. Policy Objective",
            [
                "This policy sets out the Bank's expectations for conduct risk management, "
                "ensuring that the Bank delivers fair outcomes for customers, maintains "
                "market integrity, and promotes effective competition.",
            ],
        ),
        (
            "2. Conduct Standards",
            [
                "{c} All staff must act with integrity, due skill, care, and diligence "
                "in accordance with the FCA's Conduct Rules.".format(c=_clause(2, 1)),
                "{c} Product design must consider the needs and characteristics of the "
                "target market and potential for customer harm.".format(c=_clause(2, 2)),
                "{c} Remuneration structures must not incentivise behaviours that could "
                "lead to poor customer outcomes.".format(c=_clause(2, 3)),
            ],
        ),
        (
            "3. Complaints Handling",
            [
                "{c} Customer complaints must be acknowledged within {d} and resolved "
                "within {d2}.".format(
                    c=_clause(3, 1), d=_days(1, 3), d2=_days(15, 56)
                ),
                "{c} Trends in complaints must be analysed quarterly and reported to the "
                "Conduct Risk Committee.".format(c=_clause(3, 2)),
            ],
        ),
    ]


def _it_security():
    return [
        (
            "1. Purpose and Scope",
            [
                "This policy establishes the information security requirements for all "
                "Bank systems, networks, and data. It applies to all employees, contractors, "
                "and third parties with access to Bank information assets.",
            ],
        ),
        (
            "2. Access Management",
            [
                "{c} Access to production systems must be granted on a least-privilege basis "
                "and reviewed every {d}.".format(c=_clause(2, 1), d=_days(30, 90)),
                "{c} Privileged access accounts must use multi-factor authentication and "
                "session recording. Maximum session duration is {d}.".format(
                    c=_clause(2, 2), d=_days(1, 1)
                ),
                "{c} User accounts must be disabled within {d} of an employee's departure "
                "or role change that removes the access requirement.".format(
                    c=_clause(2, 3), d=_days(1, 3)
                ),
            ],
        ),
        (
            "3. Vulnerability Management",
            [
                "{c} Critical vulnerabilities must be patched within {d} of disclosure. "
                "High-severity vulnerabilities must be patched within {d2}.".format(
                    c=_clause(3, 1), d=_days(5, 14), d2=_days(15, 30)
                ),
                "{c} Penetration tests must be conducted annually for all externally "
                "facing applications and after significant changes.".format(
                    c=_clause(3, 2)
                ),
            ],
        ),
        (
            "4. Incident Response",
            [
                "{c} Security incidents must be reported to the CISO within {d} of "
                "detection.".format(c=_clause(4, 1), d=_days(1, 2)),
                "{c} A post-incident review must be completed within {d} of incident "
                "closure, with lessons learned shared across the organisation.".format(
                    c=_clause(4, 2), d=_days(10, 20)
                ),
            ],
        ),
    ]


def _liquidity_risk():
    return [
        (
            "1. Framework Overview",
            [
                "This framework establishes the Bank's approach to liquidity risk management "
                "in compliance with CRR II Liquidity Coverage Ratio (LCR) and Net Stable "
                "Funding Ratio (NSFR) requirements.",
            ],
        ),
        (
            "2. Liquidity Buffers",
            [
                "{c} The Bank must maintain an LCR of at least {p} at all times, with an "
                "internal target of {p2}.".format(
                    c=_clause(2, 1),
                    p=_percent(100, 100),
                    p2=_percent(110, 130),
                ),
                "{c} High Quality Liquid Assets (HQLA) must comprise at least {p} Level 1 "
                "assets.".format(c=_clause(2, 2), p=_percent(60, 80)),
            ],
        ),
        (
            "3. Stress Testing",
            [
                "{c} Liquidity stress tests must be conducted monthly under idiosyncratic, "
                "market-wide, and combined scenarios.".format(c=_clause(3, 1)),
                "{c} The survival horizon under the combined stress scenario must exceed "
                "{d}.".format(c=_clause(3, 2), d=_days(30, 90)),
            ],
        ),
        (
            "4. Contingency Funding Plan",
            [
                "{c} The Contingency Funding Plan must be reviewed and approved by ALCO "
                "at least annually and tested at least semi-annually.".format(
                    c=_clause(4, 1)
                ),
            ],
        ),
    ]


def _whistleblowing():
    return [
        (
            "1. Policy Statement",
            [
                "The Bank is committed to maintaining an open culture where employees and "
                "stakeholders can raise concerns about wrongdoing without fear of retaliation. "
                "This policy complies with the Public Interest Disclosure Act 1998.",
            ],
        ),
        (
            "2. Reporting Channels",
            [
                "{c} Concerns may be raised through the confidential whistleblowing hotline, "
                "the online reporting portal, or directly with the Whistleblowing Champion.".format(
                    c=_clause(2, 1)
                ),
                "{c} Anonymous reports will be accepted and investigated to the extent possible "
                "given the information provided.".format(c=_clause(2, 2)),
            ],
        ),
        (
            "3. Investigation Process",
            [
                "{c} An initial assessment must be completed within {d} of receipt. "
                "The reporter must be notified of the outcome within {d2}.".format(
                    c=_clause(3, 1), d=_days(5, 10), d2=_days(30, 60)
                ),
                "{c} Investigations must be conducted by individuals independent of the "
                "area under investigation.".format(c=_clause(3, 2)),
            ],
        ),
    ]


def _record_management():
    return [
        (
            "1. Scope",
            [
                "This policy governs the creation, storage, retention, and disposal of "
                "all Bank records, whether physical or electronic. It ensures compliance "
                "with legal, regulatory, and business requirements.",
            ],
        ),
        (
            "2. Retention Periods",
            [
                "{c} Customer account records must be retained for a minimum of 7 years "
                "from account closure.".format(c=_clause(2, 1)),
                "{c} AML and KYC records must be retained for at least 5 years from the "
                "end of the business relationship.".format(c=_clause(2, 2)),
                "{c} Board and committee minutes must be retained permanently.".format(
                    c=_clause(2, 3)
                ),
            ],
        ),
        (
            "3. Disposal",
            [
                "{c} Records that have exceeded their retention period must be disposed of "
                "securely within {d} unless subject to a legal hold.".format(
                    c=_clause(3, 1), d=_days(30, 60)
                ),
                "{c} Electronic records must be permanently deleted using approved data "
                "destruction methods. Physical records must be cross-cut shredded.".format(
                    c=_clause(3, 2)
                ),
            ],
        ),
    ]


# ---------------------------------------------------------------------------
# Document definitions -- exactly 30
# ---------------------------------------------------------------------------

DOCUMENT_DEFS = [
    # AML Policy (5 docs)
    ("Anti-Money Laundering Policy", "AML Policy", _aml_overview),
    ("KYC Customer Onboarding Procedures", "AML Policy", _kyc_procedures),
    ("Sanctions Screening Policy", "AML Policy", _sanctions_screening),
    ("Fraud Prevention and Detection Policy", "AML Policy", _fraud_prevention),
    ("Transaction Monitoring Standards", "AML Policy", _aml_overview),
    # Lending Policy (5 docs)
    ("Retail Lending Policy", "Lending Policy", _lending_general),
    ("Commercial Lending Standards", "Lending Policy", _lending_general),
    ("Mortgage Underwriting Policy", "Lending Policy", _lending_general),
    ("Credit Risk Appetite Statement", "Lending Policy", _lending_general),
    ("Secured Lending Collateral Policy", "Lending Policy", _lending_general),
    # Operational Risk Framework (5 docs)
    ("Operational Risk Management Framework", "Operational Risk Framework", _oprisk_framework),
    ("Business Continuity Policy", "Operational Risk Framework", _oprisk_framework),
    ("Third-Party Risk Management Policy", "Operational Risk Framework", _third_party_risk),
    ("Model Risk Management Framework", "Operational Risk Framework", _model_risk),
    ("IT Security and Cyber Risk Policy", "Operational Risk Framework", _it_security),
    # Product Terms (5 docs)
    ("Current Account Terms and Conditions", "Product Terms", _product_terms),
    ("Savings Account Terms and Conditions", "Product Terms", _product_terms),
    ("Business Account General Terms", "Product Terms", _product_terms),
    ("Credit Card Terms of Use", "Product Terms", _product_terms),
    ("Investment Product Terms", "Product Terms", _product_terms),
    # Data Protection Policy (5 docs)
    ("Data Protection Policy", "Data Protection Policy", _data_protection),
    ("Data Retention and Disposal Policy", "Data Protection Policy", _record_management),
    ("Cross-Border Data Transfer Standard", "Data Protection Policy", _data_protection),
    ("Employee Data Privacy Notice", "Data Protection Policy", _data_protection),
    ("Customer Data Privacy Notice", "Data Protection Policy", _data_protection),
    # Compliance Procedure (5 docs)
    ("Regulatory Compliance Monitoring Procedure", "Compliance Procedure", _compliance_procedure),
    ("Conduct Risk Management Policy", "Compliance Procedure", _conduct_risk),
    ("Whistleblowing Policy", "Compliance Procedure", _whistleblowing),
    ("Capital Adequacy Policy", "Compliance Procedure", _capital_adequacy),
    ("Liquidity Risk Management Framework", "Compliance Procedure", _liquidity_risk),
]


def _slugify(title):
    """Convert title to a filename-safe slug."""
    slug = title.lower()
    allowed = "abcdefghijklmnopqrstuvwxyz0123456789 "
    slug = "".join(c if c in allowed else " " for c in slug)
    return "-".join(slug.split())


def _random_date(start_year=2023, end_year=2025):
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def _build_frontmatter(doc_id, title, doc_type, reg_body, jurisdiction):
    effective = _random_date(2023, 2025)
    review = effective + timedelta(days=random.choice([180, 365, 730]))
    version = "{}.{}".format(random.randint(1, 5), random.randint(0, 9))
    lines = [
        "---",
        "doc_id: \"{}\"".format(doc_id),
        "title: \"{}\"".format(title),
        "doc_type: \"{}\"".format(doc_type),
        "effective_date: \"{}\"".format(effective.isoformat()),
        "regulatory_body: \"{}\"".format(reg_body),
        "jurisdiction: \"{}\"".format(jurisdiction),
        "version: \"{}\"".format(version),
        "status: \"Active\"",
        "review_date: \"{}\"".format(review.isoformat()),
        "---",
    ]
    return "\n".join(lines)


def _build_body(sections):
    """Convert list of (heading, paragraphs) into Markdown body text."""
    parts = []
    for heading, paragraphs in sections:
        parts.append("## {}".format(heading))
        parts.append("")
        for para in paragraphs:
            # Wrap long paragraphs for readability
            wrapped = textwrap.fill(para, width=90)
            parts.append(wrapped)
            parts.append("")
    return "\n".join(parts)


def _pad_body(body, min_words=500):
    """If the body is too short, add additional boilerplate sections."""
    extra_sections = [
        (
            "Governance and Oversight",
            [
                "The Board of Directors retains ultimate responsibility for the matters "
                "covered by this document. Day-to-day oversight is delegated to the relevant "
                "Executive Committee member as specified in the Bank's Governance Map.",
                "The policy owner must present a summary of compliance status, key metrics, "
                "and emerging risks to the relevant Board sub-committee at least semi-annually.",
                "Any material exceptions to this policy must be approved by the relevant "
                "Executive Committee member and recorded in the policy exception register. "
                "Exceptions are valid for a maximum period of 12 months and must be reviewed "
                "before renewal.",
            ],
        ),
        (
            "Review and Amendment",
            [
                "This document must be reviewed at least annually or following a material "
                "change in regulation, business strategy, or risk profile. The review must "
                "be documented and signed off by the policy owner.",
                "Amendments must follow the Bank's Document Change Control Procedure. "
                "All staff affected by changes must be notified within {d} and must "
                "acknowledge receipt.".format(d=_days(10, 20)),
                "Previous versions of this document must be retained in the Bank's policy "
                "management system for audit and reference purposes.",
            ],
        ),
        (
            "Definitions and Interpretation",
            [
                "For the purposes of this document, the following definitions apply unless "
                "the context requires otherwise:",
                "\"Bank\" means the parent entity and all subsidiaries within the consolidated "
                "group. \"Regulatory Authority\" means any governmental or statutory body with "
                "supervisory authority over the Bank's activities, including the FCA and PRA. "
                "\"Material\" means any item, event, or circumstance that could reasonably be "
                "expected to influence the decision-making of the Board or senior management.",
                "\"Business Day\" means any day other than a Saturday, Sunday, or public "
                "holiday in England and Wales. \"Effective Date\" means the date from which "
                "this document takes effect, as specified in the document header.",
            ],
        ),
        (
            "Related Documents",
            [
                "This document should be read in conjunction with the Bank's Risk Appetite "
                "Statement, the Group Compliance Policy, the Conduct Risk Framework, and "
                "any relevant regulatory guidance published by the FCA, PRA, or EBA.",
                "Where there is a conflict between this document and any applicable law or "
                "regulation, the law or regulation takes precedence. Any such conflict must "
                "be reported to the Compliance function for resolution.",
            ],
        ),
    ]

    word_count = len(body.split())
    idx = 0
    while word_count < min_words and idx < len(extra_sections):
        heading, paragraphs = extra_sections[idx]
        section_num = random.randint(6, 12)
        heading = "{}. {}".format(section_num, heading.split(". ", 1)[-1] if ". " in heading else heading)
        body += "\n## {}\n\n".format(heading)
        for para in paragraphs:
            wrapped = textwrap.fill(para, width=90)
            body += wrapped + "\n\n"
        word_count = len(body.split())
        idx += 1

    return body


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Generating 30 policy documents in: {}".format(OUTPUT_DIR))

    for i, (title, doc_type, body_builder) in enumerate(DOCUMENT_DEFS):
        doc_num = i + 1
        doc_id = "POL-{:03d}".format(doc_num)

        reg_body = random.choice(REGULATORY_BODIES)
        jurisdiction = random.choice(JURISDICTIONS)

        frontmatter = _build_frontmatter(doc_id, title, doc_type, reg_body, jurisdiction)
        sections = body_builder()
        body = _build_body(sections)

        # Ensure minimum word count
        min_words = random.randint(500, 800)
        body = _pad_body(body, min_words=min_words)

        # Compose full document
        slug = _slugify(title)
        filename = "{}-{}.md".format(doc_id, slug)
        filepath = os.path.join(OUTPUT_DIR, filename)

        content = "{}\n\n# {}\n\n{}".format(frontmatter, title, body)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        word_count = len(content.split())
        print("  [{:2d}/30] {} ({} words)".format(doc_num, filename, word_count))

    print("\nDone. Generated 30 documents.")


if __name__ == "__main__":
    main()
