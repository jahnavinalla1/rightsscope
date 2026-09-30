# Deal model methodology

## Scope and input contract

The fictional package includes twelve completed series and US English-language rights. H1–H6 are consecutive half-years over a three-year horizon. There is no change in territory between offers. Only the exclusivity duration/structure, payment pattern, headline fee and delivery cost change.

`baseline_catalog_cash` is expected gross cash from monetization opportunities **without any new deal**. `baseline_retention` is the proportion of those same opportunities retained after accepting an offer. It already incorporates overlap/cannibalization; do not add a second displacement charge. Six `payment_weights` must sum to one and lie between zero and one. Fees and delivery costs are nonnegative. The simplified participation rate is applied consistently to deal and baseline revenue.

## Formula definitions

For half-year t (t = 1…6):

```text
fee cash = total fee × payment weight[t]
foregone cash = baseline cash[t] × (1 − retention[t])
incremental cash = (fee cash − foregone cash) × (1 − participation rate)
discount factor = (1 + annual discount rate)^(−t / 2)
incremental NPV = sum(incremental cash × discount factor) − delivery cost
```

Delivery cost occurs at time zero. All operating cash flows occur at half-year end, including the first payment. The annual rate is converted with fractional annual periods; it is not divided by two. No terminal value, renewals, taxes, financing, credit adjustment or foreign exchange is included. Original production costs are sunk and excluded from the incremental decision, not assumed never to have existed.

The **fee PV factor** is the sum of payment weight × discount factor × (1 − participation rate). The **no-deal fee floor** is (PV of foregone net contribution + delivery cost) / fee PV factor. The **fee to match the best alternative** adds the larger of zero and the other offers' NPVs, divided by the same factor. Thresholds assume the payment schedule, rights and every other input stay fixed.

If every incremental NPV is nonpositive, the recommendation is **No deal**. Exact positive ties choose the first listed alternative; qualitative review should resolve a tie. The scenarios in `results/sensitivity.csv` show all three offers, not just the preferred one.

## Workbook map

- **Inputs D5:D6:** annual rate and participation rate; D10:I10: baseline cash.
- **Inputs rows 13–18, 20–25, 27–32:** competing deal terms and payment checks.
- **CashFlows:** visible six-period calculations and separate NPV for each alternative.
- **Decision:** headline fees, NPVs, break-even floors, competitive thresholds and Year 1 cash. The recommendation is linked to the live NPV ranking.
- **Inputs D44 / Decision D16:** numeric completeness and payment-fraction check. Terminal only; not a financial-model driver.

Blue cells are editable assumptions, green formulas link across sheets, and black formulas calculate within a sheet. The Python validator enforces a wider set of domain constraints than spreadsheet entry checks. Correct any missing inputs or payment warnings before interpreting the results. The workbook is not a contract approval system and cells are not access-controlled.

## Verification and limitations

The tests substitute every computed fee floor and confirm zero NPV, and substitute every competitive threshold and confirm parity with the best alternative. They also verify that a higher baseline makes exclusivity more expensive, zero discount matches undiscounted cash, a sufficiently better price changes the winner, and bad offers trigger no deal.

Before business use, replace invented assumptions with verified rights availability, contract schedules, counterparty credit, territory/media-specific market forecasts, tax treatment and legal review. Validate whether the no-deal alternatives are simultaneously feasible; impossible overlapping licenses would overstate opportunity cost. This project demonstrates FP&A decision support, not legal advice, a live Sony negotiation or a guarantee of cash collection.
