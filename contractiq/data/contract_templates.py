"""Jinja2 contract templates for MSA, PO, NDA, and SLA contract types."""

from jinja2 import Template

MSA_TEMPLATE = Template("""\
MASTER SERVICE AGREEMENT

Agreement Number: {{ agreement_number }}
Effective Date: {{ effective_date }}

BETWEEN:

{{ buyer_name }} ("Buyer")
Address: {{ buyer_address }}

AND:

{{ supplier_name }} ("Supplier")
Address: {{ supplier_address }}

RECITALS

WHEREAS, Buyer desires to engage Supplier to provide certain services as described herein; and
WHEREAS, Supplier has the expertise and resources to perform such services;

NOW, THEREFORE, in consideration of the mutual covenants and agreements set forth herein, the Parties agree as follows:

ARTICLE 1 - SCOPE OF SERVICES

Supplier shall provide the following services to Buyer: {{ service_description }}

The initial term of this Agreement shall be {{ term_years }} year(s) commencing on the Effective Date, with automatic renewal for successive one-year periods unless either Party provides written notice of non-renewal at least {{ notice_days }} days prior to the expiration of the then-current term.

Total estimated contract value: ${{ contract_value }}

{% for clause_title, clause_text in clauses %}
ARTICLE {{ loop.index + 1 }} - {{ clause_title | upper }}

{{ clause_text }}

{% endfor %}
IN WITNESS WHEREOF, the Parties have executed this Agreement as of the date first written above.

BUYER: {{ buyer_name }}
By: ___________________________
Name: {{ buyer_signatory }}
Title: {{ buyer_title }}
Date: {{ effective_date }}

SUPPLIER: {{ supplier_name }}
By: ___________________________
Name: {{ supplier_signatory }}
Title: {{ supplier_title }}
Date: {{ effective_date }}
""")

PO_TEMPLATE = Template("""\
PURCHASE ORDER AGREEMENT

Purchase Order Number: {{ agreement_number }}
Date: {{ effective_date }}
Delivery Date: {{ delivery_date }}

BUYER:
{{ buyer_name }}
{{ buyer_address }}
Contact: {{ buyer_signatory }}, {{ buyer_title }}

SUPPLIER:
{{ supplier_name }}
{{ supplier_address }}
Contact: {{ supplier_signatory }}, {{ supplier_title }}

1. GOODS / SERVICES ORDERED

{{ service_description }}

Quantity: {{ quantity }}
Unit Price: ${{ unit_price }}
Total Order Value: ${{ contract_value }}

2. DELIVERY TERMS

Delivery shall be made to Buyer's designated facility on or before {{ delivery_date }}.
Shipping terms: {{ shipping_terms }}
Risk of loss transfers to Buyer upon delivery.

3. ACCEPTANCE

Buyer shall have {{ acceptance_days }} business days after delivery to inspect and accept or reject the goods. Goods not meeting specifications may be returned at Supplier's expense.

{% for clause_title, clause_text in clauses %}
{{ loop.index + 3 }}. {{ clause_title | upper }}

{{ clause_text }}

{% endfor %}
ACKNOWLEDGED AND ACCEPTED:

Buyer: {{ buyer_name }}
Authorized Signature: ___________________________
Date: {{ effective_date }}

Supplier: {{ supplier_name }}
Authorized Signature: ___________________________
Date: {{ effective_date }}
""")

NDA_TEMPLATE = Template("""\
NON-DISCLOSURE AGREEMENT

Agreement Date: {{ effective_date }}
Agreement Number: {{ agreement_number }}

This Non-Disclosure Agreement ("Agreement") is entered into by and between:

{{ buyer_name }} ("Disclosing Party")
{{ buyer_address }}

and

{{ supplier_name }} ("Receiving Party")
{{ supplier_address }}

PURPOSE: The Parties wish to explore a potential business relationship regarding {{ service_description }} and in connection therewith may disclose Confidential Information to each other.

1. DEFINITION OF CONFIDENTIAL INFORMATION

"Confidential Information" means any non-public information disclosed by either Party, whether orally, in writing, or by inspection, including but not limited to: trade secrets, business plans, financial data, customer lists, technical data, product designs, software code, marketing strategies, and any other proprietary information.

2. OBLIGATIONS

The Receiving Party agrees to:
(a) Hold all Confidential Information in strict confidence;
(b) Not disclose Confidential Information to any third party without prior written consent;
(c) Use Confidential Information solely for the Purpose described above;
(d) Protect Confidential Information with at least the same degree of care used for its own confidential information, but no less than reasonable care;
(e) Limit internal access to personnel with a need to know.

3. EXCLUSIONS

Confidential Information does not include information that:
(a) Is or becomes publicly available through no fault of the Receiving Party;
(b) Was rightfully in the Receiving Party's possession prior to disclosure;
(c) Is independently developed without use of Confidential Information;
(d) Is rightfully received from a third party without restriction.

4. TERM

This Agreement shall remain in effect for {{ term_years }} year(s) from the Effective Date. The obligations of confidentiality shall survive termination for a period of {{ survival_years }} years.

5. RETURN OF INFORMATION

Upon termination or request, the Receiving Party shall promptly return or destroy all Confidential Information and certify such destruction in writing within {{ return_days }} days.

{% for clause_title, clause_text in clauses %}
{{ loop.index + 5 }}. {{ clause_title | upper }}

{{ clause_text }}

{% endfor %}
IN WITNESS WHEREOF:

{{ buyer_name }}
By: ___________________________
Name: {{ buyer_signatory }}
Title: {{ buyer_title }}
Date: {{ effective_date }}

{{ supplier_name }}
By: ___________________________
Name: {{ supplier_signatory }}
Title: {{ supplier_title }}
Date: {{ effective_date }}
""")

SLA_TEMPLATE = Template("""\
SERVICE LEVEL AGREEMENT

SLA Reference: {{ agreement_number }}
Effective Date: {{ effective_date }}
Associated Contract: {{ associated_contract }}

BETWEEN:

{{ buyer_name }} ("Customer")
{{ buyer_address }}

AND:

{{ supplier_name }} ("Service Provider")
{{ supplier_address }}

1. SERVICE DESCRIPTION

Service Provider shall deliver the following services: {{ service_description }}

2. SERVICE LEVELS

2.1 Availability: Service Provider guarantees {{ uptime_pct }}% system availability measured on a {{ measurement_period }} basis.

2.2 Response Times:
- Critical (P1) incidents: {{ p1_response }} response, {{ p1_resolution }} resolution
- High (P2) incidents: {{ p2_response }} response, {{ p2_resolution }} resolution
- Medium (P3) incidents: {{ p3_response }} response, {{ p3_resolution }} resolution
- Low (P4) incidents: {{ p4_response }} response, {{ p4_resolution }} resolution

2.3 Maintenance Windows: Scheduled maintenance shall occur during {{ maintenance_window }} with at least {{ maintenance_notice }} hours advance notice.

3. SERVICE CREDITS

If Service Provider fails to meet the agreed service levels:
- Availability < {{ credit_tier1_pct }}%: {{ credit_tier1_amount }}% credit of monthly fees
- Availability < {{ credit_tier2_pct }}%: {{ credit_tier2_amount }}% credit of monthly fees
- Availability < {{ credit_tier3_pct }}%: {{ credit_tier3_amount }}% credit of monthly fees

Maximum monthly service credits shall not exceed {{ max_credit_pct }}% of monthly fees.
Total contract value: ${{ contract_value }} per {{ billing_period }}.

4. REPORTING

Service Provider shall deliver monthly performance reports within {{ report_days }} business days of each month-end, including uptime statistics, incident summaries, and trend analysis.

5. ESCALATION

Level 1: Service Desk - {{ escalation_l1 }}
Level 2: Service Manager - {{ escalation_l2 }}
Level 3: VP Operations - {{ escalation_l3 }}

{% for clause_title, clause_text in clauses %}
{{ loop.index + 5 }}. {{ clause_title | upper }}

{{ clause_text }}

{% endfor %}
AGREED AND ACCEPTED:

Customer: {{ buyer_name }}
By: ___________________________
Name: {{ buyer_signatory }}
Title: {{ buyer_title }}
Date: {{ effective_date }}

Service Provider: {{ supplier_name }}
By: ___________________________
Name: {{ supplier_signatory }}
Title: {{ supplier_title }}
Date: {{ effective_date }}
""")

TEMPLATES = {
    "MSA": MSA_TEMPLATE,
    "PO": PO_TEMPLATE,
    "NDA": NDA_TEMPLATE,
    "SLA": SLA_TEMPLATE,
}
