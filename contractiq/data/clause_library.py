"""Library of contract clause text variants for synthetic contract generation."""

CLAUSE_LIBRARY: dict[str, list[str]] = {
    "force_majeure": [
        (
            'Neither Party shall be liable for any failure or delay in performing its obligations '
            'under this Agreement where such failure or delay results from Force Majeure Events, '
            'including but not limited to acts of God, war, terrorism, pandemic, earthquake, flood, '
            'fire, governmental actions, or any other event beyond the reasonable control of the '
            'affected Party. The affected Party shall provide written notice within ten (10) '
            'business days of the occurrence of such event.'
        ),
        (
            'In the event of Force Majeure, the obligations of the affected Party shall be '
            'suspended for the duration of such event. If the Force Majeure event continues for '
            'more than ninety (90) consecutive days, either Party may terminate this Agreement '
            'upon thirty (30) days written notice without liability.'
        ),
        (
            'Force Majeure shall mean any event or circumstance not within a Party\'s reasonable '
            'control, including natural disasters, epidemics, strikes, lockouts, riots, acts of '
            'war, embargoes, and governmental orders. The Party claiming Force Majeure shall use '
            'commercially reasonable efforts to mitigate the impact of such event.'
        ),
    ],
    "termination": [
        (
            'Either Party may terminate this Agreement for convenience upon sixty (60) days prior '
            'written notice to the other Party. Upon termination, Supplier shall deliver all '
            'completed and in-progress work products and Buyer shall pay for all services rendered '
            'through the effective date of termination.'
        ),
        (
            'This Agreement may be terminated: (a) by either Party for material breach if the '
            'breaching Party fails to cure such breach within thirty (30) days of receiving written '
            'notice; (b) by either Party upon the insolvency or bankruptcy of the other Party; '
            '(c) by mutual written agreement of both Parties.'
        ),
        (
            'Termination for Cause: Either Party may terminate this Agreement immediately upon '
            'written notice if the other Party: (i) commits a material breach that is incapable '
            'of cure; (ii) fails to cure a curable material breach within forty-five (45) days '
            'of notice; or (iii) becomes subject to bankruptcy or insolvency proceedings.'
        ),
    ],
    "payment_terms": [
        (
            'Buyer shall pay all undisputed invoices within thirty (30) days of receipt. Invoices '
            'shall be submitted monthly in arrears and shall include detailed descriptions of '
            'services rendered. Late payments shall accrue interest at the rate of 1.5% per month '
            'or the maximum rate permitted by law, whichever is less.'
        ),
        (
            'Payment shall be made within forty-five (45) days of receipt of a valid invoice via '
            'wire transfer to the account designated by Supplier. Supplier shall submit invoices '
            'no more frequently than bi-weekly. Buyer may withhold payment for any amounts '
            'reasonably disputed in good faith.'
        ),
        (
            'All fees are due and payable within Net 60 days from the invoice date. Buyer shall '
            'pay via electronic funds transfer. A 2% early payment discount is available for '
            'invoices paid within ten (10) days. Supplier reserves the right to suspend services '
            'for invoices overdue by more than ninety (90) days.'
        ),
    ],
    "confidentiality": [
        (
            'Each Party agrees to hold the other Party\'s Confidential Information in strict '
            'confidence and not to disclose such information to any third party without the prior '
            'written consent of the disclosing Party. Confidential Information shall not include '
            'information that: (a) is or becomes publicly available; (b) was known prior to '
            'disclosure; (c) is independently developed; or (d) is disclosed pursuant to legal '
            'requirement. This obligation survives termination for five (5) years.'
        ),
        (
            'The Receiving Party shall protect the Disclosing Party\'s Confidential Information '
            'using the same degree of care it uses to protect its own confidential information, '
            'but no less than reasonable care. The Receiving Party shall limit access to '
            'Confidential Information to employees and contractors who have a need to know and '
            'are bound by confidentiality obligations at least as restrictive as those herein.'
        ),
    ],
    "indemnification": [
        (
            'Supplier shall indemnify, defend, and hold harmless Buyer and its officers, directors, '
            'employees, and agents from and against any and all claims, damages, losses, costs, '
            'and expenses (including reasonable attorneys\' fees) arising out of or relating to: '
            '(a) Supplier\'s breach of this Agreement; (b) Supplier\'s negligence or willful '
            'misconduct; (c) any third-party claim that the deliverables infringe intellectual '
            'property rights.'
        ),
        (
            'Each Party shall indemnify the other Party against all losses, damages, and expenses '
            'arising from: (i) its material breach of any representation or warranty; (ii) its '
            'negligent acts or omissions; (iii) any claim by a third party resulting from the '
            'indemnifying Party\'s performance under this Agreement. The indemnifying Party shall '
            'have the right to control the defense of any such claim.'
        ),
    ],
    "limitation_of_liability": [
        (
            'IN NO EVENT SHALL EITHER PARTY BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, '
            'CONSEQUENTIAL, OR PUNITIVE DAMAGES, REGARDLESS OF THE CAUSE OF ACTION OR THE THEORY '
            'OF LIABILITY. EACH PARTY\'S TOTAL AGGREGATE LIABILITY UNDER THIS AGREEMENT SHALL NOT '
            'EXCEED THE TOTAL FEES PAID OR PAYABLE IN THE TWELVE (12) MONTH PERIOD PRECEDING THE '
            'CLAIM.'
        ),
        (
            'The total liability of Supplier under this Agreement shall not exceed two (2) times '
            'the total contract value. This limitation shall not apply to: (a) breaches of '
            'confidentiality obligations; (b) indemnification obligations for IP infringement; '
            '(c) damages caused by gross negligence or willful misconduct.'
        ),
    ],
    "intellectual_property": [
        (
            'All intellectual property rights in any deliverables created by Supplier specifically '
            'for Buyer under this Agreement shall be owned by Buyer upon full payment. Supplier '
            'retains all rights in its pre-existing intellectual property and general knowledge, '
            'skills, and experience. Supplier grants Buyer a perpetual, non-exclusive license to '
            'use any Supplier pre-existing IP incorporated into the deliverables.'
        ),
        (
            'Each Party retains ownership of its pre-existing intellectual property. Any jointly '
            'developed IP shall be jointly owned with each Party having the right to use and '
            'license such IP without consent or accounting to the other Party. Work-for-hire '
            'deliverables shall be the exclusive property of Buyer.'
        ),
    ],
    "warranty": [
        (
            'Supplier warrants that: (a) all services shall be performed in a professional and '
            'workmanlike manner consistent with industry standards; (b) deliverables shall '
            'materially conform to the specifications for a period of ninety (90) days following '
            'acceptance; (c) Supplier has the right and authority to enter into this Agreement.'
        ),
        (
            'Supplier represents and warrants that the goods supplied shall be free from defects '
            'in materials and workmanship for a period of twelve (12) months from delivery. '
            'Supplier\'s sole obligation under this warranty is, at its option, to repair or '
            'replace defective goods at no additional cost to Buyer.'
        ),
    ],
    "dispute_resolution": [
        (
            'Any dispute arising out of or relating to this Agreement shall first be submitted to '
            'good faith negotiation between senior executives of each Party for a period of '
            'thirty (30) days. If not resolved, the dispute shall be submitted to binding '
            'arbitration in accordance with the rules of the American Arbitration Association. '
            'The arbitration shall take place in New York, New York.'
        ),
        (
            'The Parties agree to resolve disputes through the following process: (1) direct '
            'negotiation for 15 business days; (2) mediation for 30 days; (3) if still unresolved, '
            'binding arbitration under ICC Rules. The seat of arbitration shall be Singapore. '
            'The language of arbitration shall be English. Judgment on the award may be entered '
            'in any court of competent jurisdiction.'
        ),
    ],
    "governing_law": [
        (
            'This Agreement shall be governed by and construed in accordance with the laws of the '
            'State of New York, without regard to its conflict of laws principles. Each Party '
            'irrevocably submits to the exclusive jurisdiction of the federal and state courts '
            'located in New York County, New York.'
        ),
        (
            'This Agreement is governed by the laws of the State of California. Any legal action '
            'shall be brought exclusively in the courts of Santa Clara County, California. The '
            'United Nations Convention on Contracts for the International Sale of Goods shall not '
            'apply to this Agreement.'
        ),
    ],
    "sla_uptime": [
        (
            'Supplier shall maintain a minimum service availability of 99.9% measured on a monthly '
            'basis, excluding scheduled maintenance windows. Scheduled maintenance shall be '
            'performed during off-peak hours (Saturday 2:00 AM - 6:00 AM ET) with at least '
            'seventy-two (72) hours prior notice. Failure to meet the SLA shall entitle Buyer to '
            'service credits as set forth in Exhibit B.'
        ),
        (
            'Service Level: The platform shall achieve 99.95% uptime per calendar quarter. '
            'Downtime caused by (a) Buyer\'s systems, (b) force majeure events, or (c) scheduled '
            'maintenance shall be excluded from calculations. Service credits: 5% credit for '
            '<99.9%, 10% credit for <99.5%, 20% credit for <99.0%.'
        ),
    ],
    "data_protection": [
        (
            'Supplier shall implement and maintain appropriate technical and organizational '
            'measures to protect personal data processed under this Agreement in accordance with '
            'applicable data protection laws, including but not limited to GDPR and CCPA. '
            'Supplier shall promptly notify Buyer of any data breach within seventy-two (72) '
            'hours of discovery.'
        ),
        (
            'The Parties agree to comply with all applicable data privacy regulations. Supplier '
            'shall: (a) process personal data only as instructed by Buyer; (b) ensure personnel '
            'are bound by confidentiality; (c) implement security measures per ISO 27001; '
            '(d) assist with data subject access requests within 48 hours; (e) delete all '
            'personal data upon termination unless retention is required by law.'
        ),
    ],
    "insurance": [
        (
            'Supplier shall maintain the following insurance coverages: (a) Commercial General '
            'Liability with limits of not less than $2,000,000 per occurrence; (b) Professional '
            'Liability (E&O) of not less than $5,000,000; (c) Workers\' Compensation as required '
            'by law; (d) Cyber Liability of not less than $3,000,000. Supplier shall provide '
            'certificates of insurance upon request.'
        ),
        (
            'During the term and for two (2) years after expiration, Supplier shall maintain: '
            'General Liability ($1M per occurrence / $2M aggregate), Professional Liability '
            '($2M per claim), and Cyber Insurance ($1M per claim). Buyer shall be named as '
            'additional insured on the General Liability policy.'
        ),
    ],
    "assignment": [
        (
            'Neither Party may assign this Agreement without the prior written consent of the '
            'other Party, which consent shall not be unreasonably withheld or delayed. '
            'Notwithstanding the foregoing, either Party may assign this Agreement to an affiliate '
            'or in connection with a merger, acquisition, or sale of substantially all its assets.'
        ),
    ],
    "entire_agreement": [
        (
            'This Agreement, together with all exhibits, schedules, and amendments, constitutes '
            'the entire agreement between the Parties and supersedes all prior and contemporaneous '
            'agreements, understandings, negotiations, and discussions, whether oral or written. '
            'No amendment to this Agreement shall be effective unless made in writing and signed '
            'by both Parties.'
        ),
    ],
    "notice": [
        (
            'All notices required or permitted under this Agreement shall be in writing and shall '
            'be deemed given when: (a) delivered personally; (b) sent by confirmed email; or '
            '(c) three (3) business days after being sent by registered mail, return receipt '
            'requested, to the addresses set forth in the signature block or such other address '
            'as a Party may designate in writing.'
        ),
    ],
}

CLAUSE_NAMES = list(CLAUSE_LIBRARY.keys())

# Clauses considered critical for compliance checking
CRITICAL_CLAUSES = [
    "force_majeure",
    "termination",
    "payment_terms",
    "confidentiality",
    "indemnification",
    "limitation_of_liability",
    "governing_law",
    "data_protection",
]

MAJOR_CLAUSES = [
    "intellectual_property",
    "warranty",
    "dispute_resolution",
    "insurance",
]

MINOR_CLAUSES = [
    "sla_uptime",
    "assignment",
    "entire_agreement",
    "notice",
]
