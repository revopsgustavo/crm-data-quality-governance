from __future__ import annotations
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]; PROCESSED=ROOT/'data'/'processed'; OUTPUT=PROCESSED/'data_quality_report.csv'
REQUIRED={'leads':['lead_id','source'],'accounts':['account_id','owner_id'],'contacts':['contact_id','account_id'],'opportunities':['opportunity_id','account_id','owner_id','amount','close_date','stage','forecast_category','probability'],'users':['user_id'],'activities':['activity_id','related_object_id'],'forecast_categories':['forecast_category'],'stages':['stage'],'crm_audit_log':['event_id'],'data_quality_checks':['check_id'],'remediation_tasks':['task_id']}
def blank(s): return s.isna()|s.astype(str).str.strip().eq('')
def read(name):
    p=PROCESSED/f'{name}.csv'; return pd.read_csv(p) if p.exists() else pd.DataFrame()
def validate():
    tables={n:read(n) for n in REQUIRED}; rows=[]
    for n,cols in REQUIRED.items():
        p=PROCESSED/f'{n}.csv'; df=tables[n]; rows.append({'table':n,'check_name':'file_exists','status':'pass' if p.exists() else 'fail','details':str(p)})
        for c in cols:
            ok=c in df.columns; rows.append({'table':n,'check_name':f'column_exists:{c}','status':'pass' if ok else 'fail','details':c})
            if ok and c.endswith('_id'):
                miss=int(blank(df[c]).sum()); rows.append({'table':n,'check_name':f'id_not_null:{c}','status':'pass' if miss==0 else 'fail','details':f'missing={miss}'})
    opp=tables['opportunities']; accounts=tables['accounts']; contacts=tables['contacts']; users=tables['users']
    valid_users=set(users.get('user_id',pd.Series(dtype=str)).dropna()); valid_accounts=set(accounts.get('account_id',pd.Series(dtype=str)).dropna()); valid_stages=set(tables['stages'].get('stage',pd.Series(dtype=str)).dropna()); valid_categories=set(tables['forecast_categories'].get('forecast_category',pd.Series(dtype=str)).dropna())
    if 'amount' in opp:
        amount=pd.to_numeric(opp['amount'],errors='coerce'); rows.append({'table':'opportunities','check_name':'amount_non_negative','status':'pass' if (amount.dropna()>=0).all() else 'fail','details':'amount >= 0'})
    if 'probability' in opp:
        prob=pd.to_numeric(opp['probability'],errors='coerce'); rows.append({'table':'opportunities','check_name':'probability_between_0_and_1','status':'pass' if prob.dropna().between(0,1).all() else 'fail','details':'probability scale 0-1'})
    if 'stage' in opp: rows.append({'table':'opportunities','check_name':'valid_stages','status':'pass' if not sorted(set(opp['stage'].dropna())-valid_stages) else 'fail','details':''})
    if 'forecast_category' in opp: rows.append({'table':'opportunities','check_name':'valid_forecast_categories','status':'pass' if not sorted(set(opp['forecast_category'].dropna())-valid_categories) else 'fail','details':''})
    for name,df in [('accounts',accounts),('opportunities',opp)]:
        if 'owner_id' in df:
            invalid=sorted((set(df['owner_id'].dropna())-{''})-valid_users); rows.append({'table':name,'check_name':'valid_owner_id','status':'pass' if not invalid else 'fail','details':','.join(invalid)})
    for name,df in [('contacts',contacts),('opportunities',opp)]:
        if 'account_id' in df:
            invalid=sorted((set(df['account_id'].dropna())-{''})-valid_accounts); rows.append({'table':name,'check_name':'valid_account_id','status':'pass' if not invalid else 'fail','details':','.join(invalid)})
    return pd.DataFrame(rows)
def main():
    report=validate(); OUTPUT.parent.mkdir(parents=True,exist_ok=True); report.to_csv(OUTPUT,index=False); print(f'Data quality report generated at {OUTPUT}. failed_checks={int(report.status.eq("fail").sum())}')
if __name__=='__main__': main()
