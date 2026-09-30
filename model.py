"""Incremental catalog deal cash economics, USD millions, six half-years.

Compare mutually exclusive offers against the SAME no-deal baseline. No taxes,
terminal value, credit-risk adjustment or accounting revenue-recognition opinion.
"""
import csv
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent


def load():
    a=json.loads((ROOT/'data/deals.json').read_text()); validate(a); return a


def validate(a):
    if not 0<=a['annual_discount_rate']<=1 or not 0<=a['participation_rate']<1: raise ValueError('Invalid rate')
    if len(a['baseline_catalog_cash'])!=6 or any(v<0 for v in a['baseline_catalog_cash']): raise ValueError('Six nonnegative baseline periods required')
    if len({x['name'] for x in a['offers']})!=len(a['offers']): raise ValueError('Duplicate deal name')
    for o in a['offers']:
        if o['total_fee']<0 or o['delivery_cost']<0: raise ValueError('Negative contract cash')
        if len(o['payment_weights'])!=6 or len(o['baseline_retention'])!=6: raise ValueError('Six periods required')
        if abs(sum(o['payment_weights'])-1)>1e-9: raise ValueError('Payment weights must sum to 100%')
        if any(not 0<=v<=1 for v in o['payment_weights']+o['baseline_retention']): raise ValueError('Invalid weight')


def evaluate(a,offer,baseline_scale=1):
    validate(a)
    if baseline_scale<0: raise ValueError('Negative baseline scale')
    r=a['annual_discount_rate']; net=1-a['participation_rate']
    # All six operating cash flows occur at half-year END; delivery cost is time 0.
    periods=[]
    for i,(base,w,keep) in enumerate(zip(a['baseline_catalog_cash'],offer['payment_weights'],offer['baseline_retention']),1):
        baseline=base*baseline_scale
        fee=offer['total_fee']*w
        incremental=(fee-baseline*(1-keep))*net
        discount=(1+r)**(-i/2)
        periods.append(dict(half_year=i,baseline=baseline,fee_cash=fee,retained_catalog=baseline*keep,
                            foregone_catalog=baseline*(1-keep),incremental_net_cash=incremental,
                            discount_factor=discount,present_value=incremental*discount))
    npv=sum(p['present_value'] for p in periods)-offer['delivery_cost']
    fee_pv_factor=sum(w*(1+r)**(-(i+1)/2) for i,w in enumerate(offer['payment_weights']))*net
    opportunity_pv=sum(p['foregone_catalog']*net*p['discount_factor'] for p in periods)
    floor=(opportunity_pv+offer['delivery_cost'])/fee_pv_factor
    gross_headline=offer['total_fee']
    return dict(name=offer['name'],headline_fee=gross_headline,incremental_npv=npv,
                break_even_fee=floor,fee_pv_factor=fee_pv_factor,opportunity_pv=opportunity_pv,
                incremental_undiscounted=sum(p['incremental_net_cash'] for p in periods)-offer['delivery_cost'],
                year1_incremental_cash=sum(p['incremental_net_cash'] for p in periods[:2])-offer['delivery_cost'],
                periods=periods)


def analyze(a):
    outcomes=[evaluate(a,o) for o in a['offers']]
    winner=max(outcomes,key=lambda x:x['incremental_npv'])
    for out in outcomes:
        other_best=max([0]+[x['incremental_npv'] for x in outcomes if x['name']!=out['name']])
        out['fee_to_match_best_alternative']=out['break_even_fee']+other_best/out['fee_pv_factor']
    return dict(recommendation=winner['name'] if winner['incremental_npv']>0 else 'No deal',offers=outcomes)


def main():
    a=load(); result=analyze(a)
    out=ROOT/'results'; out.mkdir(exist_ok=True)
    (out/'metrics.json').write_text(json.dumps(result,indent=2)+'\n')
    with (out/'sensitivity.csv').open('w',newline='') as f:
        writer=csv.writer(f); writer.writerow(['annual_discount_rate','baseline_scale','offer','incremental_npv'])
        for r in [0.06,0.10,0.14]:
            for scale in [0.7,1,1.3]:
                scenario={**a,'annual_discount_rate':r}
                for offer in a['offers']:
                    writer.writerow([r,scale,offer['name'],evaluate(scenario,offer,scale)['incremental_npv']])
    print(json.dumps({k:v for k,v in result.items() if k!='offers'},indent=2))
    for x in result['offers']: print(x['name'],round(x['incremental_npv'],3),round(x['break_even_fee'],3),round(x['fee_to_match_best_alternative'],3))


if __name__=='__main__':main()
