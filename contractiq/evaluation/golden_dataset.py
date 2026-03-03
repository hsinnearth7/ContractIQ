"""Golden Dataset for RAG evaluation (v6.0) — 55 questions × 3 difficulty levels."""

from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------
# Each entry is a dict with the following keys:
#   - id            : str   — unique question identifier (e.g. "Q-001")
#   - question      : str   — natural-language question a user might ask
#   - expected_answer: str  — ground-truth answer the RAG system should return
#   - expected_context: str — section / clause reference the retriever must surface
#   - difficulty    : str   — one of "easy", "medium", "hard"
#   - slice         : str   — one of "single_contract", "cross_contract",
#                              "numerical", "temporal"
# ---------------------------------------------------------------------------

GOLDEN_DATASET: list[dict[str, Any]] = [
    # ==================================================================
    # SLICE 1 — single_contract  (20 questions)
    # ==================================================================
    # --- easy (8) ---
    {
        "id": "Q-001",
        "question": "What is the governing law specified in the MSA with Acme Technologies?",
        "expected_answer": "The MSA-2024-001 with Acme Technologies is governed by the laws of the State of Delaware, without regard to its conflict-of-law principles.",
        "expected_context": "MSA-2024-001, Section 14 — Governing Law",
        "difficulty": "easy",
        "slice": "single_contract",
    },
    {
        "id": "Q-002",
        "question": "Who is the primary contact listed for GlobalLogistics Corp under PO-2024-003?",
        "expected_answer": "The primary contact for GlobalLogistics Corp under PO-2024-003 is Maria Chen, Director of Supply Chain Operations, reachable at m.chen@globallogistics.example.com.",
        "expected_context": "PO-2024-003, Schedule A — Contact Information",
        "difficulty": "easy",
        "slice": "single_contract",
    },
    {
        "id": "Q-003",
        "question": "What type of agreement is document NDA-2024-007 with DataVault Solutions?",
        "expected_answer": "NDA-2024-007 is a mutual Non-Disclosure Agreement between ContractIQ Inc. and DataVault Solutions covering the exchange of proprietary data-processing methodologies.",
        "expected_context": "NDA-2024-007, Recitals",
        "difficulty": "easy",
        "slice": "single_contract",
    },
    {
        "id": "Q-004",
        "question": "What is the confidentiality period in the NDA with SecureLogix?",
        "expected_answer": "Under NDA-2024-012 with SecureLogix, the confidentiality obligations survive for five (5) years after the termination or expiration of the agreement.",
        "expected_context": "NDA-2024-012, Section 5 — Duration of Confidentiality",
        "difficulty": "easy",
        "slice": "single_contract",
    },
    {
        "id": "Q-005",
        "question": "What is the notice address for PremierParts Ltd in their MSA?",
        "expected_answer": "Notices to PremierParts Ltd under MSA-2024-008 must be sent to 42 Industrial Park Road, Birmingham, B15 2TT, United Kingdom, Attention: Legal Department.",
        "expected_context": "MSA-2024-008, Section 16 — Notices",
        "difficulty": "easy",
        "slice": "single_contract",
    },
    {
        "id": "Q-006",
        "question": "Can the SLA with NexGen Cloud Services be assigned to a third party?",
        "expected_answer": "No. SLA-2024-005 with NexGen Cloud Services prohibits assignment by either party without the prior written consent of the other party, except in connection with a merger or sale of substantially all assets.",
        "expected_context": "SLA-2024-005, Section 12 — Assignment",
        "difficulty": "easy",
        "slice": "single_contract",
    },
    {
        "id": "Q-007",
        "question": "What dispute resolution mechanism is specified in the Pinnacle Manufacturing MSA?",
        "expected_answer": "MSA-2024-004 with Pinnacle Manufacturing requires disputes to be resolved first through good-faith negotiation for thirty (30) days, then by binding arbitration administered by the American Arbitration Association (AAA) under its Commercial Arbitration Rules.",
        "expected_context": "MSA-2024-004, Section 15 — Dispute Resolution",
        "difficulty": "easy",
        "slice": "single_contract",
    },
    {
        "id": "Q-008",
        "question": "What warranty does SwiftSupply Inc provide on delivered goods?",
        "expected_answer": "Under PO-2024-009, SwiftSupply Inc warrants that all goods delivered shall be free from defects in materials and workmanship for a period of twenty-four (24) months from the date of delivery.",
        "expected_context": "PO-2024-009, Section 8 — Warranty",
        "difficulty": "easy",
        "slice": "single_contract",
    },
    # --- medium (7) ---
    {
        "id": "Q-009",
        "question": "Describe the force majeure clause in the MSA with Acme Technologies. Does it cover pandemics?",
        "expected_answer": "Section 11 of MSA-2024-001 defines force majeure events as acts of God, war, terrorism, earthquakes, floods, epidemics, pandemics, government actions, and labor strikes. Pandemics are explicitly listed. The affected party must provide written notice within five (5) business days and use commercially reasonable efforts to mitigate the impact.",
        "expected_context": "MSA-2024-001, Section 11 — Force Majeure",
        "difficulty": "medium",
        "slice": "single_contract",
    },
    {
        "id": "Q-010",
        "question": "What are the termination-for-convenience rights under the TechForge Systems MSA?",
        "expected_answer": "Either party may terminate MSA-2024-006 for convenience by providing ninety (90) days' prior written notice. Upon such termination, TechForge Systems is entitled to payment for all work completed through the effective termination date plus any non-cancellable commitments made in good faith.",
        "expected_context": "MSA-2024-006, Section 9 — Termination",
        "difficulty": "medium",
        "slice": "single_contract",
    },
    {
        "id": "Q-011",
        "question": "What indemnification obligations does CloudNine Networks have under their SLA?",
        "expected_answer": "Under SLA-2024-010, CloudNine Networks shall indemnify, defend, and hold harmless ContractIQ from third-party claims arising from (a) CloudNine's breach of data-protection obligations, (b) infringement of intellectual property rights, or (c) gross negligence or willful misconduct. The indemnifying party must assume sole control of the defense and all related settlement negotiations.",
        "expected_context": "SLA-2024-010, Section 10 — Indemnification",
        "difficulty": "medium",
        "slice": "single_contract",
    },
    {
        "id": "Q-012",
        "question": "What insurance coverage must Pinnacle Manufacturing maintain throughout the term of MSA-2024-004?",
        "expected_answer": "Pinnacle Manufacturing must maintain: (i) Commercial General Liability with limits of no less than $2,000,000 per occurrence and $5,000,000 aggregate, (ii) Workers' Compensation as required by applicable law, (iii) Professional Liability / Errors & Omissions of at least $3,000,000 per claim, and (iv) Cyber Liability of at least $1,000,000 per incident. Certificates of insurance must be provided within ten (10) business days of request.",
        "expected_context": "MSA-2024-004, Section 13 — Insurance",
        "difficulty": "medium",
        "slice": "single_contract",
    },
    {
        "id": "Q-013",
        "question": "How does the DataVault Solutions NDA handle residual knowledge?",
        "expected_answer": "NDA-2024-007, Section 4(c) contains a residual-knowledge carve-out: each party's personnel may use in the course of their duties any general knowledge, skills, and experience retained in unaided memory after exposure to the other party's Confidential Information, provided they do not intentionally memorize or reference specific documents or data sets.",
        "expected_context": "NDA-2024-007, Section 4(c) — Residuals",
        "difficulty": "medium",
        "slice": "single_contract",
    },
    {
        "id": "Q-014",
        "question": "What intellectual property rights are granted to ContractIQ under the TechForge Systems MSA?",
        "expected_answer": "Under MSA-2024-006, Section 7, all deliverables created specifically for ContractIQ are deemed 'work made for hire' and ContractIQ owns all IP rights therein. For pre-existing IP incorporated into deliverables, TechForge grants ContractIQ a perpetual, royalty-free, non-exclusive license to use such pre-existing IP solely in connection with the deliverables.",
        "expected_context": "MSA-2024-006, Section 7 — Intellectual Property",
        "difficulty": "medium",
        "slice": "single_contract",
    },
    {
        "id": "Q-015",
        "question": "What data-protection obligations does NexGen Cloud Services have under SLA-2024-005?",
        "expected_answer": "NexGen Cloud Services must: (a) process personal data only on documented instructions from ContractIQ, (b) ensure personnel are bound by confidentiality, (c) implement appropriate technical and organizational measures per Annex II, (d) notify ContractIQ within 48 hours of any personal-data breach, (e) assist with DPIAs and data-subject requests, and (f) delete or return all personal data upon termination. Sub-processors require prior written consent.",
        "expected_context": "SLA-2024-005, Section 11 — Data Protection & GDPR Compliance",
        "difficulty": "medium",
        "slice": "single_contract",
    },
    # --- hard (5) ---
    {
        "id": "Q-016",
        "question": "Analyze the limitation-of-liability clause in the Acme Technologies MSA and identify any carve-outs.",
        "expected_answer": "MSA-2024-001, Section 10 caps each party's aggregate liability at the greater of (x) the total fees paid or payable in the twelve (12) months preceding the claim or (y) $500,000. Neither party is liable for indirect, incidental, consequential, or punitive damages. However, the cap and exclusion of consequential damages do NOT apply to: (1) breaches of confidentiality obligations, (2) indemnification obligations under Section 9, (3) infringement of intellectual property rights, or (4) either party's gross negligence or willful misconduct. These carve-outs effectively remove the liability ceiling for the most critical risk areas.",
        "expected_context": "MSA-2024-001, Section 10 — Limitation of Liability",
        "difficulty": "hard",
        "slice": "single_contract",
    },
    {
        "id": "Q-017",
        "question": "What are the implications of the audit clause in the GlobalLogistics Corp PO, and how does it interact with confidentiality protections?",
        "expected_answer": "PO-2024-003, Section 12 grants ContractIQ the right to audit GlobalLogistics Corp's books, records, and facilities once per calendar year with thirty (30) days' notice. Auditors must sign a confidentiality undertaking acceptable to GlobalLogistics. Audit findings of overcharges exceeding 3% entitle ContractIQ to a full refund of the overcharge plus the cost of the audit. The audit clause expressly states it is subject to the confidentiality provisions of Section 6 — meaning auditors may not disclose GlobalLogistics' proprietary cost structures to third parties. Any conflict between audit rights and confidentiality is resolved in favor of the least-disclosure approach that still achieves the audit's purpose.",
        "expected_context": "PO-2024-003, Section 12 — Audit Rights; Section 6 — Confidentiality",
        "difficulty": "hard",
        "slice": "single_contract",
    },
    {
        "id": "Q-018",
        "question": "How would a change of control at SecureLogix affect the NDA obligations, and what remedies are available?",
        "expected_answer": "NDA-2024-012, Section 9 provides that a change of control (defined as acquisition of more than 50% of voting securities or substantially all assets) of SecureLogix triggers an automatic right for ContractIQ to terminate the NDA on thirty (30) days' written notice. If ContractIQ does not exercise this right within sixty (60) days of receiving change-of-control notice, the NDA continues with the successor entity. Upon termination triggered by change of control, SecureLogix must return or certify destruction of all Confidential Information within fifteen (15) days. Surviving obligations (Section 5) remain enforceable against the successor. ContractIQ may seek injunctive relief without posting bond if it believes the successor may misuse Confidential Information.",
        "expected_context": "NDA-2024-012, Section 9 — Change of Control; Section 5 — Duration; Section 10 — Remedies",
        "difficulty": "hard",
        "slice": "single_contract",
    },
    {
        "id": "Q-019",
        "question": "Explain how the SLA credit mechanism works for NexGen Cloud Services when multiple service tiers are affected simultaneously.",
        "expected_answer": "Under SLA-2024-005, Annex I, service credits are calculated per tier: Tier 1 (critical infrastructure) downtime exceeding the 99.99% target yields a 10% credit on monthly fees for that tier per 0.01% shortfall; Tier 2 (application services) uses a 99.9% target with a 5% credit per 0.1% shortfall; Tier 3 (non-critical) uses 99.5% with a 2% credit per 0.5% shortfall. When outages affect multiple tiers simultaneously, credits are aggregated but capped at 30% of the total monthly invoice. NexGen must provide a Root Cause Analysis within five (5) business days. If the same root cause triggers multi-tier failures in two consecutive months, ContractIQ may terminate for cause without further cure period.",
        "expected_context": "SLA-2024-005, Annex I — Service Credits; Section 9(b) — Termination for Cause",
        "difficulty": "hard",
        "slice": "single_contract",
    },
    {
        "id": "Q-020",
        "question": "What is the interplay between the warranty, indemnification, and limitation-of-liability clauses in the SwiftSupply Inc PO?",
        "expected_answer": "PO-2024-009 creates a layered risk framework: Section 8 (Warranty) provides a 24-month defect warranty with repair-or-replace as the primary remedy; Section 9 (Indemnification) requires SwiftSupply to indemnify ContractIQ against third-party product-liability claims, IP infringement, and regulatory non-compliance; Section 10 (Limitation of Liability) caps direct damages at 150% of the total PO value but explicitly excludes indemnification obligations and warranty fraud from the cap. Consequential damages are mutually waived except for breaches of confidentiality and willful misconduct. The net effect is that routine warranty claims are cost-contained, but serious third-party or IP claims can exceed the cap, giving ContractIQ broader protection for high-severity events.",
        "expected_context": "PO-2024-009, Section 8 — Warranty; Section 9 — Indemnification; Section 10 — Limitation of Liability",
        "difficulty": "hard",
        "slice": "single_contract",
    },
    # ==================================================================
    # SLICE 2 — cross_contract  (15 questions)
    # ==================================================================
    # --- easy (4) ---
    {
        "id": "Q-021",
        "question": "Which of our supplier contracts are governed by Delaware law?",
        "expected_answer": "Two contracts are governed by Delaware law: MSA-2024-001 with Acme Technologies and MSA-2024-006 with TechForge Systems. The remaining contracts specify New York, England & Wales, California, or other jurisdictions.",
        "expected_context": "MSA-2024-001, Section 14; MSA-2024-006, Section 14",
        "difficulty": "easy",
        "slice": "cross_contract",
    },
    {
        "id": "Q-022",
        "question": "List all active NDAs and their counterparties.",
        "expected_answer": "There are two active NDAs: (1) NDA-2024-007 with DataVault Solutions — a mutual NDA covering proprietary data-processing methodologies, and (2) NDA-2024-012 with SecureLogix — a mutual NDA covering cybersecurity assessment tools and threat-intelligence feeds.",
        "expected_context": "NDA-2024-007, Recitals; NDA-2024-012, Recitals",
        "difficulty": "easy",
        "slice": "cross_contract",
    },
    {
        "id": "Q-023",
        "question": "Which suppliers have SLA agreements with us?",
        "expected_answer": "Two suppliers have SLA agreements: NexGen Cloud Services (SLA-2024-005) covering cloud infrastructure and managed services, and CloudNine Networks (SLA-2024-010) covering enterprise network connectivity and SD-WAN services.",
        "expected_context": "SLA-2024-005, Preamble; SLA-2024-010, Preamble",
        "difficulty": "easy",
        "slice": "cross_contract",
    },
    {
        "id": "Q-024",
        "question": "Which contracts include an anti-bribery clause?",
        "expected_answer": "Four contracts include explicit anti-bribery clauses: MSA-2024-001 (Acme Technologies, Section 17), MSA-2024-004 (Pinnacle Manufacturing, Section 18), PO-2024-003 (GlobalLogistics Corp, Section 14), and MSA-2024-008 (PremierParts Ltd, Section 19). These clauses require compliance with the U.S. Foreign Corrupt Practices Act and, where applicable, the UK Bribery Act.",
        "expected_context": "MSA-2024-001 §17; MSA-2024-004 §18; PO-2024-003 §14; MSA-2024-008 §19",
        "difficulty": "easy",
        "slice": "cross_contract",
    },
    # --- medium (6) ---
    {
        "id": "Q-025",
        "question": "Compare the termination-for-cause provisions across the Acme Technologies and TechForge Systems MSAs.",
        "expected_answer": "MSA-2024-001 (Acme Technologies) allows termination for cause after a thirty (30) day cure period upon written notice of material breach, whereas MSA-2024-006 (TechForge Systems) provides a shorter fifteen (15) day cure period for payment breaches but the standard thirty (30) days for all other material breaches. Both agreements require the non-breaching party to specify the nature of the breach in the notice. TechForge's MSA additionally allows immediate termination without cure if the breach involves a data-security incident affecting ContractIQ data.",
        "expected_context": "MSA-2024-001, Section 9(a); MSA-2024-006, Section 9(a)–(b)",
        "difficulty": "medium",
        "slice": "cross_contract",
    },
    {
        "id": "Q-026",
        "question": "How do the confidentiality obligations in the DataVault Solutions NDA differ from those in the SecureLogix NDA?",
        "expected_answer": "NDA-2024-007 (DataVault Solutions) defines Confidential Information broadly to include data schemas, algorithms, and processing outputs, with a five (5) year survival period and a residual-knowledge carve-out (Section 4(c)). NDA-2024-012 (SecureLogix) is narrower in scope — focused on cybersecurity tools and threat intelligence — but imposes a longer seven (7) year survival period, no residual-knowledge exception, and requires return or destruction of materials within fifteen (15) days of termination rather than the thirty (30) day period in the DataVault NDA.",
        "expected_context": "NDA-2024-007, Sections 1, 4(c), 5; NDA-2024-012, Sections 1, 5, 7",
        "difficulty": "medium",
        "slice": "cross_contract",
    },
    {
        "id": "Q-027",
        "question": "Which supplier contracts require the supplier to carry cyber-liability insurance, and what are the minimum coverage amounts?",
        "expected_answer": "Three contracts require cyber-liability insurance: (1) MSA-2024-004 with Pinnacle Manufacturing — minimum $1,000,000 per incident, (2) SLA-2024-005 with NexGen Cloud Services — minimum $5,000,000 per incident and $10,000,000 aggregate, and (3) SLA-2024-010 with CloudNine Networks — minimum $3,000,000 per incident. The remaining contracts either do not require cyber-liability coverage or address it only as a general recommendation in side letters.",
        "expected_context": "MSA-2024-004 §13; SLA-2024-005 §13; SLA-2024-010 §11",
        "difficulty": "medium",
        "slice": "cross_contract",
    },
    {
        "id": "Q-028",
        "question": "Compare the data-protection obligations across the NexGen Cloud Services and CloudNine Networks SLAs.",
        "expected_answer": "Both SLAs require GDPR-aligned data-protection practices, but there are key differences. SLA-2024-005 (NexGen) mandates a 48-hour breach notification window, restricts sub-processors to prior written consent, and requires annual third-party security audits (SOC 2 Type II). SLA-2024-010 (CloudNine) allows a 72-hour breach notification window aligned with GDPR Article 33, permits pre-approved sub-processors listed in Schedule C with notification of changes, and requires quarterly vulnerability assessments rather than annual SOC 2 audits. NexGen's obligations are more stringent due to its role as a primary data processor.",
        "expected_context": "SLA-2024-005, Section 11; SLA-2024-010, Section 9",
        "difficulty": "medium",
        "slice": "cross_contract",
    },
    {
        "id": "Q-029",
        "question": "Which of our supplier agreements include most-favored-customer (MFC) pricing clauses?",
        "expected_answer": "Two agreements contain MFC clauses: MSA-2024-001 (Acme Technologies, Section 5(d)) guarantees that pricing will be no less favorable than that offered to any other customer of comparable volume, and PO-2024-009 (SwiftSupply Inc, Section 5(c)) provides a retroactive price adjustment if SwiftSupply offers lower unit pricing to another buyer for the same SKU within a calendar quarter. The remaining contracts rely on fixed pricing or annual renegotiation mechanisms without MFC protections.",
        "expected_context": "MSA-2024-001, Section 5(d); PO-2024-009, Section 5(c)",
        "difficulty": "medium",
        "slice": "cross_contract",
    },
    {
        "id": "Q-030",
        "question": "Compare the IP ownership provisions in the Acme Technologies MSA and the TechForge Systems MSA.",
        "expected_answer": "Both MSAs distinguish between foreground IP (created during engagement) and background IP (pre-existing). MSA-2024-001 (Acme) assigns all foreground IP to ContractIQ upon full payment and grants a limited license to background IP embedded in deliverables. MSA-2024-006 (TechForge) uses a work-made-for-hire framework for foreground IP with a perpetual, royalty-free license to background IP. The key difference is that Acme's assignment is conditional on full payment, whereas TechForge's ownership vests automatically upon creation. Both agreements require the supplier to obtain waivers of moral rights from personnel.",
        "expected_context": "MSA-2024-001, Section 7; MSA-2024-006, Section 7",
        "difficulty": "medium",
        "slice": "cross_contract",
    },
    # --- hard (5) ---
    {
        "id": "Q-031",
        "question": "Across all our supplier contracts, identify and compare the different liability cap structures. Which contract exposes ContractIQ to the greatest potential uncapped liability?",
        "expected_answer": "Liability caps vary significantly: MSA-2024-001 (Acme) caps at the greater of 12-month fees or $500K with carve-outs for confidentiality, IP, and willful misconduct; MSA-2024-004 (Pinnacle) caps at 200% of annual contract value with carve-outs for product-liability indemnity; PO-2024-003 (GlobalLogistics) caps at 100% of total PO value with no carve-outs; MSA-2024-006 (TechForge) caps at $1,000,000 with carve-outs for data breaches; SLA-2024-005 (NexGen) caps at 12-month fees with carve-outs for data protection and IP; PO-2024-009 (SwiftSupply) caps at 150% of PO value with carve-outs for indemnity and warranty fraud; SLA-2024-010 (CloudNine) caps at $2,000,000 with a broad data-breach carve-out. The greatest uncapped exposure is under SLA-2024-010 (CloudNine) because its data-breach carve-out is broadly defined to include any 'security incident,' which could encompass operational errors, not just malicious attacks.",
        "expected_context": "MSA-2024-001 §10; MSA-2024-004 §10; PO-2024-003 §11; MSA-2024-006 §10; SLA-2024-005 §10; PO-2024-009 §10; SLA-2024-010 §8",
        "difficulty": "hard",
        "slice": "cross_contract",
    },
    {
        "id": "Q-032",
        "question": "If ContractIQ were acquired by a competitor, which supplier contracts could be terminated by the supplier, and under what conditions?",
        "expected_answer": "Four contracts have change-of-control provisions triggered by ContractIQ's acquisition: (1) NDA-2024-012 (SecureLogix) — supplier may terminate on 30 days' notice within 60 days of learning of the change; (2) SLA-2024-005 (NexGen) — either party may terminate on 90 days' notice if the acquiring entity is a direct competitor, subject to a six-month wind-down for migration; (3) MSA-2024-006 (TechForge) — TechForge may renegotiate pricing or terminate on 60 days' notice if the acquirer has been a TechForge competitor within the prior 24 months; (4) MSA-2024-008 (PremierParts) — requires mutual consent to continue if the acquiring entity is incorporated outside the UK/US. The remaining contracts either prohibit unilateral assignment (which an acquisition may not trigger if structured as a stock purchase) or are silent on change of control.",
        "expected_context": "NDA-2024-012 §9; SLA-2024-005 §12; MSA-2024-006 §9(d); MSA-2024-008 §15",
        "difficulty": "hard",
        "slice": "cross_contract",
    },
    {
        "id": "Q-033",
        "question": "Evaluate ContractIQ's overall exposure to supply-chain disruption based on the force majeure and business-continuity provisions across all active supplier contracts.",
        "expected_answer": "Force majeure coverage is inconsistent: MSA-2024-001 (Acme) and MSA-2024-004 (Pinnacle) include broad FM clauses covering pandemics with 5-day notice requirements. PO-2024-003 (GlobalLogistics) has a narrow FM clause limited to natural disasters and government embargoes — it excludes pandemics and labor disputes. SLA-2024-005 (NexGen) and SLA-2024-010 (CloudNine) tie FM to disaster-recovery obligations in their respective Annexes, requiring failover within 4 hours (NexGen) and 8 hours (CloudNine). PO-2024-009 (SwiftSupply) has no FM clause, meaning SwiftSupply bears full performance risk. MSA-2024-006 (TechForge) caps FM relief at 90 days, after which either party may terminate. The biggest gap is GlobalLogistics and SwiftSupply — a pandemic or labor action could disrupt physical supply chains with no contractual relief mechanism.",
        "expected_context": "MSA-2024-001 §11; MSA-2024-004 §11; PO-2024-003 §10; SLA-2024-005 §8 & Annex III; SLA-2024-010 §7 & Annex II; PO-2024-009 (none); MSA-2024-006 §11",
        "difficulty": "hard",
        "slice": "cross_contract",
    },
    {
        "id": "Q-034",
        "question": "Which supplier contracts create overlapping or conflicting confidentiality obligations that could complicate information sharing during a joint project involving Acme Technologies and DataVault Solutions?",
        "expected_answer": "MSA-2024-001 (Acme, Section 6) designates all project deliverables and specifications as Acme Confidential Information, while NDA-2024-007 (DataVault, Section 1) classifies data-processing methodologies as DataVault Confidential Information. If a joint project requires sharing Acme's specifications with DataVault (or vice versa), ContractIQ would be bound by non-disclosure obligations to both parties simultaneously. MSA-2024-001 §6(e) permits disclosure to subcontractors under NDA, but DataVault is a separate supplier, not a subcontractor. NDA-2024-007 §3(b) allows disclosure to 'authorized third parties' only with prior written consent. Resolution requires either: (a) a tripartite amendment authorizing cross-disclosure, or (b) treating ContractIQ as an intermediary that anonymizes specifications before sharing. The residual-knowledge carve-out in the DataVault NDA further complicates matters since DataVault personnel could retain Acme's methodologies in unaided memory.",
        "expected_context": "MSA-2024-001 §6; NDA-2024-007 §§1, 3(b), 4(c)",
        "difficulty": "hard",
        "slice": "cross_contract",
    },
    {
        "id": "Q-035",
        "question": "Assess the regulatory compliance risk across all supplier contracts regarding GDPR, CCPA, and sector-specific regulations.",
        "expected_answer": "GDPR obligations are addressed in SLA-2024-005 (NexGen, §11) with full Data Processing Addendum and SLA-2024-010 (CloudNine, §9) with a lighter-touch schedule. NDA-2024-007 (DataVault) references GDPR in its data-handling annex but does not include a standalone DPA. MSA-2024-001 (Acme, §12) references GDPR and CCPA but defers specifics to a yet-to-be-executed DPA addendum — this is a compliance gap. PO-2024-003 (GlobalLogistics) and PO-2024-009 (SwiftSupply) contain no data-protection clauses, which is appropriate only if no personal data flows to those suppliers. MSA-2024-004 (Pinnacle, §14) addresses CCPA but not GDPR despite Pinnacle operating a UK subsidiary. MSA-2024-008 (PremierParts, §17) includes UK GDPR compliance but omits CCPA. The primary risk areas are: (1) the missing DPA with Acme, (2) no GDPR coverage for Pinnacle's UK operations, and (3) no verification that GlobalLogistics and SwiftSupply are truly outside the scope of personal-data processing.",
        "expected_context": "SLA-2024-005 §11; SLA-2024-010 §9; NDA-2024-007 Annex; MSA-2024-001 §12; PO-2024-003; PO-2024-009; MSA-2024-004 §14; MSA-2024-008 §17",
        "difficulty": "hard",
        "slice": "cross_contract",
    },
    # ==================================================================
    # SLICE 3 — numerical  (10 questions)
    # ==================================================================
    # --- easy (3) ---
    {
        "id": "Q-036",
        "question": "What is the total value of PO-2024-003 with GlobalLogistics Corp?",
        "expected_answer": "The total value of PO-2024-003 with GlobalLogistics Corp is $1,250,000.00 USD, covering freight forwarding and customs brokerage services for the 2024 fiscal year.",
        "expected_context": "PO-2024-003, Section 3 — Contract Value",
        "difficulty": "easy",
        "slice": "numerical",
    },
    {
        "id": "Q-037",
        "question": "What is the uptime SLA target for NexGen Cloud Services Tier 1 infrastructure?",
        "expected_answer": "The uptime SLA target for NexGen Cloud Services Tier 1 (critical infrastructure) is 99.99%, as specified in SLA-2024-005, Annex I.",
        "expected_context": "SLA-2024-005, Annex I — Service Levels",
        "difficulty": "easy",
        "slice": "numerical",
    },
    {
        "id": "Q-038",
        "question": "What is the annual fee under the CloudNine Networks SLA?",
        "expected_answer": "The annual fee under SLA-2024-010 with CloudNine Networks is $840,000.00 USD, payable in equal monthly installments of $70,000.00.",
        "expected_context": "SLA-2024-010, Section 4 — Fees and Payment",
        "difficulty": "easy",
        "slice": "numerical",
    },
    # --- medium (4) ---
    {
        "id": "Q-039",
        "question": "If NexGen Cloud Services achieves only 99.95% uptime on Tier 1 infrastructure in a given month, what service credit is ContractIQ entitled to?",
        "expected_answer": "The Tier 1 target is 99.99%. A shortfall of 0.04% (99.99% − 99.95%) represents four increments of 0.01%. At 10% credit per 0.01% shortfall, ContractIQ is entitled to a 40% credit on the monthly Tier 1 fees. However, SLA-2024-005 Annex I caps total monthly credits at 30% of the total monthly invoice, so the effective credit is 30% of the total monthly invoice amount.",
        "expected_context": "SLA-2024-005, Annex I — Service Credits",
        "difficulty": "medium",
        "slice": "numerical",
    },
    {
        "id": "Q-040",
        "question": "What is the maximum aggregate liability of Pinnacle Manufacturing under MSA-2024-004?",
        "expected_answer": "Pinnacle Manufacturing's aggregate liability is capped at 200% of the annual contract value. Given the annual contract value stated in Schedule B is $3,400,000.00, the maximum aggregate liability is $6,800,000.00, subject to the carve-outs for product-liability indemnification claims which are uncapped.",
        "expected_context": "MSA-2024-004, Section 10 — Limitation of Liability; Schedule B",
        "difficulty": "medium",
        "slice": "numerical",
    },
    {
        "id": "Q-041",
        "question": "What is the total insurance coverage required across all suppliers that must carry Commercial General Liability?",
        "expected_answer": "Four suppliers are required to carry CGL: Pinnacle Manufacturing ($2M per occurrence / $5M aggregate under MSA-2024-004 §13), Acme Technologies ($1M per occurrence / $3M aggregate under MSA-2024-001 §13), TechForge Systems ($2M per occurrence / $4M aggregate under MSA-2024-006 §12), and PremierParts Ltd ($1.5M per occurrence / $3M aggregate under MSA-2024-008 §14). The total required aggregate CGL coverage is $15,000,000.00 ($5M + $3M + $4M + $3M).",
        "expected_context": "MSA-2024-004 §13; MSA-2024-001 §13; MSA-2024-006 §12; MSA-2024-008 §14",
        "difficulty": "medium",
        "slice": "numerical",
    },
    {
        "id": "Q-042",
        "question": "What is the per-unit pricing for SwiftSupply Inc under PO-2024-009 for SKU SSI-4420, and what volume discount tiers apply?",
        "expected_answer": "PO-2024-009, Schedule A lists SKU SSI-4420 (precision bearings) at a base price of $12.50 per unit. Volume discount tiers: 1–999 units at $12.50 (0% discount), 1,000–4,999 units at $11.25 (10% discount), 5,000–9,999 units at $10.00 (20% discount), and 10,000+ units at $8.75 (30% discount). The MFC clause in Section 5(c) may further reduce pricing if SwiftSupply offers lower rates to other buyers in the same quarter.",
        "expected_context": "PO-2024-009, Schedule A — Pricing; Section 5(c) — MFC",
        "difficulty": "medium",
        "slice": "numerical",
    },
    # --- hard (3) ---
    {
        "id": "Q-043",
        "question": "Calculate ContractIQ's maximum potential service-credit recovery in a single month if both NexGen Cloud Services and CloudNine Networks simultaneously fail to meet all SLA tiers.",
        "expected_answer": "For NexGen (SLA-2024-005): the monthly fee derived from the contract is approximately $187,500 ($2,250,000 annual ÷ 12). Maximum monthly credit is capped at 30% = $56,250. For CloudNine (SLA-2024-010): the monthly fee is $70,000. Maximum monthly credit is capped at 25% (per Annex I of SLA-2024-010) = $17,500. Total maximum service-credit recovery in a single month across both SLAs is $56,250 + $17,500 = $73,750. This does not account for any additional damages claims that might be pursued outside the SLA credit mechanism if the outages constitute a material breach.",
        "expected_context": "SLA-2024-005, Annex I; SLA-2024-010, Annex I; SLA-2024-005 §4; SLA-2024-010 §4",
        "difficulty": "hard",
        "slice": "numerical",
    },
    {
        "id": "Q-044",
        "question": "What is ContractIQ's total annual contractual spend across all active supplier agreements, and what percentage is attributable to technology services versus physical goods?",
        "expected_answer": "Total annual spend: MSA-2024-001 (Acme Technologies) — $1,800,000; PO-2024-003 (GlobalLogistics Corp) — $1,250,000; SLA-2024-005 (NexGen Cloud) — $2,250,000; MSA-2024-004 (Pinnacle Manufacturing) — $3,400,000; NDA-2024-007 (DataVault) — $0 (standalone NDA, no fees); MSA-2024-006 (TechForge Systems) — $960,000; MSA-2024-008 (PremierParts Ltd) — $2,100,000; PO-2024-009 (SwiftSupply Inc) — $1,450,000; SLA-2024-010 (CloudNine Networks) — $840,000; NDA-2024-012 (SecureLogix) — $0 (standalone NDA). Grand total: $14,050,000. Technology services (Acme, NexGen, TechForge, CloudNine) = $5,850,000 (41.6%). Physical goods and logistics (GlobalLogistics, Pinnacle, PremierParts, SwiftSupply) = $8,200,000 (58.4%).",
        "expected_context": "All contracts — fee / pricing sections",
        "difficulty": "hard",
        "slice": "numerical",
    },
    {
        "id": "Q-045",
        "question": "If GlobalLogistics Corp overcharged ContractIQ by 5% on the total PO value and an audit reveals the discrepancy, what financial recovery is ContractIQ entitled to?",
        "expected_answer": "Under PO-2024-003, Section 12, audit findings of overcharges exceeding 3% entitle ContractIQ to: (a) a full refund of the overcharge amount, plus (b) reimbursement of the audit cost. The PO total value is $1,250,000; a 5% overcharge equals $62,500. Since 5% exceeds the 3% threshold, ContractIQ is entitled to the full $62,500 refund plus audit costs (estimated at $15,000–$25,000 per Schedule D). Additionally, Section 12(d) provides that if overcharges exceed 5%, ContractIQ may terminate the PO for cause. Since the overcharge is exactly 5%, it meets the threshold — ContractIQ could argue termination rights depending on interpretation of 'exceed.' Total financial recovery: approximately $77,500–$87,500 (refund + audit costs).",
        "expected_context": "PO-2024-003, Section 12 — Audit Rights; Schedule D — Audit Cost Estimates",
        "difficulty": "hard",
        "slice": "numerical",
    },
    # ==================================================================
    # SLICE 4 — temporal  (10 questions)
    # ==================================================================
    # --- easy (3) ---
    {
        "id": "Q-046",
        "question": "When does the MSA with Acme Technologies expire?",
        "expected_answer": "MSA-2024-001 with Acme Technologies has an initial term expiring on December 31, 2026, with automatic annual renewals unless either party provides ninety (90) days' written notice of non-renewal.",
        "expected_context": "MSA-2024-001, Section 2 — Term",
        "difficulty": "easy",
        "slice": "temporal",
    },
    {
        "id": "Q-047",
        "question": "What is the effective date of PO-2024-009 with SwiftSupply Inc?",
        "expected_answer": "PO-2024-009 with SwiftSupply Inc has an effective date of March 1, 2024, with deliveries scheduled to commence within thirty (30) days of the effective date.",
        "expected_context": "PO-2024-009, Section 1 — Effective Date",
        "difficulty": "easy",
        "slice": "temporal",
    },
    {
        "id": "Q-048",
        "question": "When was the NDA with SecureLogix executed?",
        "expected_answer": "NDA-2024-012 with SecureLogix was executed on June 15, 2024, by authorized signatories of both parties.",
        "expected_context": "NDA-2024-012, Signature Page",
        "difficulty": "easy",
        "slice": "temporal",
    },
    # --- medium (4) ---
    {
        "id": "Q-049",
        "question": "Which supplier contracts are up for renewal in the next six months?",
        "expected_answer": "As of March 2026, the following contracts are up for renewal in the next six months (by September 2026): (1) SLA-2024-010 with CloudNine Networks — initial term ends June 30, 2026, requires 60 days' notice of non-renewal (deadline: May 1, 2026); (2) PO-2024-003 with GlobalLogistics Corp — term ends September 30, 2026, requires 45 days' notice (deadline: August 16, 2026). MSA-2024-001 (Acme) expires December 31, 2026, but its 90-day non-renewal notice window opens October 2, 2026, which falls just outside the six-month window.",
        "expected_context": "SLA-2024-010, Section 2; PO-2024-003, Section 2; MSA-2024-001, Section 2",
        "difficulty": "medium",
        "slice": "temporal",
    },
    {
        "id": "Q-050",
        "question": "What are the key milestone dates in the TechForge Systems MSA for the current project phase?",
        "expected_answer": "MSA-2024-006, Exhibit C outlines the Phase 2 milestones: (a) Requirements Finalization — April 15, 2026; (b) Design Review — June 1, 2026; (c) Development Completion — September 30, 2026; (d) User Acceptance Testing — October 31, 2026; (e) Go-Live — December 1, 2026. Milestone payments of 20% of the phase value are triggered upon ContractIQ's written acceptance of each milestone deliverable within ten (10) business days.",
        "expected_context": "MSA-2024-006, Exhibit C — Project Milestones (Phase 2)",
        "difficulty": "medium",
        "slice": "temporal",
    },
    {
        "id": "Q-051",
        "question": "How long after termination must NexGen Cloud Services continue to provide data-migration assistance?",
        "expected_answer": "Under SLA-2024-005, Section 9(d), NexGen Cloud Services must provide data-migration assistance for a transition period of one hundred twenty (120) days following the effective date of termination. During this period, NexGen must maintain all services at existing SLA levels and provide reasonable technical support for migration at no additional charge for the first 60 days; days 61–120 are billed at the standard hourly rate in Schedule E.",
        "expected_context": "SLA-2024-005, Section 9(d) — Transition Assistance; Schedule E",
        "difficulty": "medium",
        "slice": "temporal",
    },
    {
        "id": "Q-052",
        "question": "What are the payment terms and late-payment penalties for Pinnacle Manufacturing under MSA-2024-004?",
        "expected_answer": "MSA-2024-004, Section 4 specifies Net 45 payment terms from the date of invoice. Invoices must be submitted by the 5th business day of each month for the preceding month's services. Late payments accrue interest at 1.5% per month (18% per annum) on the outstanding balance, commencing on the 46th day. If payment is more than sixty (60) days overdue, Pinnacle may suspend non-critical services upon fifteen (15) days' written notice. Disputed amounts must be raised within twenty (20) days of invoice receipt and do not accrue late-payment interest during good-faith resolution.",
        "expected_context": "MSA-2024-004, Section 4 — Payment Terms",
        "difficulty": "medium",
        "slice": "temporal",
    },
    # --- hard (3) ---
    {
        "id": "Q-053",
        "question": "Map out all critical contractual deadlines and notice periods for the next twelve months across all active supplier agreements.",
        "expected_answer": "Key deadlines from March 2026 through February 2027: (1) May 1, 2026 — deadline to issue non-renewal notice for CloudNine Networks SLA-2024-010 (60-day notice, term ends Jun 30); (2) April 15, 2026 — TechForge Phase 2 Requirements Finalization milestone; (3) June 1, 2026 — TechForge Design Review milestone; (4) June 15, 2026 — second anniversary of SecureLogix NDA, triggering optional scope review per §8(a); (5) August 16, 2026 — deadline for GlobalLogistics PO-2024-003 non-renewal notice (45-day notice, term ends Sep 30); (6) September 30, 2026 — TechForge Development Completion & GlobalLogistics PO term end; (7) October 2, 2026 — deadline for Acme MSA-2024-001 non-renewal notice (90-day notice, term ends Dec 31); (8) October 31, 2026 — TechForge UAT milestone; (9) December 1, 2026 — TechForge Go-Live; (10) December 31, 2026 — Acme MSA initial term expiry; (11) January 15, 2027 — NexGen SLA-2024-005 annual rate review per Schedule D; (12) February 28, 2027 — PremierParts MSA-2024-008 annual insurance certificate renewal due.",
        "expected_context": "All contracts — term, milestone, and notice provisions",
        "difficulty": "hard",
        "slice": "temporal",
    },
    {
        "id": "Q-054",
        "question": "If ContractIQ wanted to exit all supplier relationships within twelve months, what is the optimal termination sequence considering notice periods, transition dependencies, and financial penalties?",
        "expected_answer": "Optimal termination sequence starting March 2026: Phase 1 (Immediate — March 2026): Issue non-renewal for CloudNine (60 days, effective Jun 30) and begin evaluating replacement network services. Issue termination-for-convenience to TechForge (90 days, effective Jun 2026) — forfeit Phase 2 milestone payments already approved. Phase 2 (May 2026): Issue non-renewal for GlobalLogistics PO (45 days ahead of Sep 30 expiry). Begin NexGen migration planning (120-day transition window will be needed). Phase 3 (July 2026): Issue termination-for-convenience to NexGen (90 days, effective Oct 2026) — triggers 120-day transition period through Feb 2027. Issue non-renewal for Acme MSA (90 days ahead of Dec 31 expiry). Phase 4 (September 2026): Issue termination-for-convenience to Pinnacle (60 days, effective Nov 2026) and PremierParts (90 days, effective Dec 2026). Phase 5 (October 2026): Terminate SwiftSupply PO with 30-day notice — pay for goods in pipeline. Phase 6 (Post-termination): NDAs with DataVault and SecureLogix survive independently; confidentiality obligations continue for 5 and 7 years respectively. Estimated early-termination penalties: TechForge ($48,000 for cancelled milestones), NexGen ($0 if convenience termination follows contract terms), Pinnacle ($170,000 for non-cancellable raw materials). Total estimated exit cost: approximately $218,000 plus transition and replacement procurement costs.",
        "expected_context": "All contracts — termination, notice, transition, and penalty provisions",
        "difficulty": "hard",
        "slice": "temporal",
    },
    {
        "id": "Q-055",
        "question": "Analyze the contract-renewal staggering across all supplier agreements and identify periods of concentrated renewal risk.",
        "expected_answer": "Renewal timeline analysis reveals clustering risk: Q2 2026 (Apr–Jun) has CloudNine SLA expiry (Jun 30) and TechForge Phase 2 critical milestones — losing either relationship mid-project is high impact. Q3 2026 (Jul–Sep) sees GlobalLogistics PO expiry (Sep 30) and TechForge Development Completion — supply-chain and project risk converge. Q4 2026 (Oct–Dec) is the highest concentration: Acme MSA expiry (Dec 31), TechForge Go-Live (Dec 1), and PremierParts annual review (Dec). Q1 2027 has NexGen rate review (Jan 15) and PremierParts insurance renewal (Feb 28). The riskiest window is Q4 2026 when three major relationships require attention simultaneously. Mitigation recommendations: (a) negotiate the Acme MSA renewal by August 2026 to reduce Q4 workload, (b) stagger future renewals across quarters by aligning new terms to off-cycle dates, (c) establish a 'renewal calendar' with automated 120-day advance alerts, and (d) prioritize the CloudNine replacement or renewal decision in April 2026 to prevent cascade effects on NexGen network dependencies.",
        "expected_context": "All contracts — Section 2 (Term) provisions; project milestone schedules",
        "difficulty": "hard",
        "slice": "temporal",
    },
]


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

def get_by_difficulty(level: str) -> list[dict[str, Any]]:
    """Return all questions matching the given difficulty level.

    Parameters
    ----------
    level : str
        One of ``"easy"``, ``"medium"``, or ``"hard"``.

    Returns
    -------
    list[dict[str, Any]]
        Filtered subset of :data:`GOLDEN_DATASET`.

    Raises
    ------
    ValueError
        If *level* is not a recognised difficulty.
    """
    valid = {"easy", "medium", "hard"}
    if level not in valid:
        raise ValueError(f"Invalid difficulty {level!r}. Must be one of {valid}.")
    return [q for q in GOLDEN_DATASET if q["difficulty"] == level]


def get_by_slice(slice_name: str) -> list[dict[str, Any]]:
    """Return all questions belonging to the given evaluation slice.

    Parameters
    ----------
    slice_name : str
        One of ``"single_contract"``, ``"cross_contract"``,
        ``"numerical"``, or ``"temporal"``.

    Returns
    -------
    list[dict[str, Any]]
        Filtered subset of :data:`GOLDEN_DATASET`.

    Raises
    ------
    ValueError
        If *slice_name* is not a recognised slice.
    """
    valid = {"single_contract", "cross_contract", "numerical", "temporal"}
    if slice_name not in valid:
        raise ValueError(
            f"Invalid slice {slice_name!r}. Must be one of {valid}."
        )
    return [q for q in GOLDEN_DATASET if q["slice"] == slice_name]


def get_slices() -> dict[str, list[dict[str, Any]]]:
    """Return the full dataset organised by slice.

    Returns
    -------
    dict[str, list[dict[str, Any]]]
        A dictionary with four keys — ``"single_contract"``,
        ``"cross_contract"``, ``"numerical"``, ``"temporal"`` — each
        mapping to the corresponding list of question dicts.
    """
    return {
        "single_contract": get_by_slice("single_contract"),
        "cross_contract": get_by_slice("cross_contract"),
        "numerical": get_by_slice("numerical"),
        "temporal": get_by_slice("temporal"),
    }


# ---------------------------------------------------------------------------
# Quick sanity check when run directly
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    total = len(GOLDEN_DATASET)
    slices = get_slices()
    difficulties = {lvl: len(get_by_difficulty(lvl)) for lvl in ("easy", "medium", "hard")}

    print(f"Golden Dataset v6.0 — {total} questions")
    print(f"  Difficulties : {difficulties}")
    print(f"  Slices       : { {k: len(v) for k, v in slices.items()} }")

    # Validate counts
    assert total == 55, f"Expected 55 questions, got {total}"
    assert len(slices["single_contract"]) == 20, "single_contract should have 20"
    assert len(slices["cross_contract"]) == 15, "cross_contract should have 15"
    assert len(slices["numerical"]) == 10, "numerical should have 10"
    assert len(slices["temporal"]) == 10, "temporal should have 10"
    assert sum(difficulties.values()) == 55, "Difficulty counts should sum to 55"

    print("  All assertions passed.")
