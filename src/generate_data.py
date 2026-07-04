from __future__ import annotations
import sqlite3
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]; PROCESSED=ROOT/'data'/'processed'; DATABASE=ROOT/'data'/'database'; TODAY=pd.Timestamp('2026-07-04')
def d(days): return (TODAY-pd.Timedelta(days=days)).strftime('%Y-%m-%d')
def f(days): return (TODAY+pd.Timedelta(days=days)).strftime('%Y-%m-%d')
def main():
    rng=np.random.default_rng(42); PROCESSED.mkdir(parents=True,exist_ok=True); DATABASE.mkdir(parents=True,exist_ok=True)
    users=pd.DataFrame([['usr_001','Ana Souza','AE','Enterprise','active'],['usr_002','Bruno Lima','AE','Mid Market','active'],['usr_003','Carla Rocha','AE','SMB','active'],['usr_004','Diego Martins','Sales Manager','Enterprise','active'],['usr_005','Fernanda Alves','RevOps','Operations','active'],['usr_006','Gustavo Pereira','SDR','Inbound','active'],['usr_007','Helena Costa','AE','Mid Market','active']],columns=['user_id','user_name','role','team','status'])
    stages=pd.DataFrame([['Prospecting',.10,'Pipeline'],['Discovery',.25,'Pipeline'],['Solution',.45,'Best Case'],['Proposal',.60,'Best Case'],['Negotiation',.75,'Best Case'],['Procurement',.85,'Commit'],['Contract',.95,'Commit'],['Closed Won',1,'Closed'],['Closed Lost',0,'Omitted']],columns=['stage','default_probability','default_forecast_category'])
    forecast_categories=pd.DataFrame({'forecast_category':['Pipeline','Best Case','Commit','Closed','Omitted'],'definition':['Early pipeline','Possible upside','Manager validated','Closed won','Excluded']})
    leads=[]
    for i in range(1,121):
        email='duplicate.alpha@example.com' if i in [18,19] else 'duplicate.beta@example.com' if i in [44,45,46] else f'lead{i:03d}@example.com'
        leads.append({'lead_id':f'lead_{i:03d}','lead_name':f'Lead {i:03d}','email':email,'company':f'Company {i%37:02d}','source':'' if i%9==0 else rng.choice(['Inbound','Outbound','Partner','Paid Search','Event']),'owner_id':rng.choice(['usr_006','usr_001','usr_002','usr_003']),'created_date':d(int(rng.integers(1,90))),'status':rng.choice(['New','Working','Qualified','Disqualified'])})
    leads=pd.DataFrame(leads)
    accounts=[]
    for i in range(1,46):
        name=f'Account {i:02d}'; domain=f'account{i:02d}.com'
        if i in [12,13]: name,domain='Atlas Cloud','atlascloud.com'
        if i in [27,28]: name,domain='Nexa SaaS','nexasaas.com'
        accounts.append({'account_id':f'acct_{i:03d}','account_name':name,'domain':domain,'segment':['SMB','Mid Market','Enterprise'][i%3],'owner_id':'' if i in [8,21,35,42] else ['usr_001','usr_002','usr_003','usr_007'][i%4],'industry':['Fintech','Healthtech','Edtech','Retail','Logistics'][i%5],'created_date':d((i*2)%90)})
    accounts=pd.DataFrame(accounts)
    contacts=pd.DataFrame([{'contact_id':f'cont_{i:03d}','account_id':'' if i in [9,31,62,77] else accounts.iloc[(i*3)%len(accounts)]['account_id'],'contact_name':f'Contact {i:03d}','email':f'contact{i:03d}@example.com','title':['CFO','Head of Sales','RevOps Manager','CEO','Operations Manager'][i%5],'created_date':d((i*5)%90)} for i in range(1,91)])
    defaults={'Prospecting':(.1,'Pipeline'),'Discovery':(.25,'Pipeline'),'Solution':(.45,'Best Case'),'Proposal':(.6,'Best Case'),'Negotiation':(.75,'Best Case'),'Procurement':(.85,'Commit'),'Contract':(.95,'Commit'),'Closed Won':(1,'Closed'),'Closed Lost':(0,'Omitted')}; st=list(defaults)
    opps=[]
    for i in range(1,81):
        stage=st[i%len(st)]; prob,cat=defaults[stage]; amount=float(rng.integers(18000,240000)); close=f(int(rng.integers(5,55)))
        if i in [5,16,37,52,64]: close=''
        if i in [6,17,29,47,68]: cat=rng.choice(['Pipeline','Best Case','Commit','Closed','Omitted'])
        if i in [10,22,43,59]: prob=float(rng.choice([.05,.20,.98]))
        if i in [11,24,40,67]: amount=0.0
        if i in [8,26,53,72]: close=d(int(rng.integers(1,35))); stage='Negotiation' if stage in ['Closed Won','Closed Lost'] else stage
        owner='' if i in [12,33,57,74] else ['usr_001','usr_002','usr_003','usr_007'][i%4]
        next_step='' if i in [7,18,32,48,55,69] else f'Follow up with buying committee {i}'
        loss='No budget' if stage=='Closed Lost' else ''
        if i in [17,35,62]: stage,cat,prob,loss='Closed Lost','Omitted',0.0,''
        if i in [14,41]: stage,cat,prob,amount='Closed Won','Closed',1.0,0.0
        opps.append({'opportunity_id':f'opp_{i:03d}','account_id':accounts.iloc[(i*2)%len(accounts)]['account_id'],'owner_id':owner,'opportunity_name':f'Opportunity {i:03d}','stage':stage,'forecast_category':cat,'probability':prob,'amount':amount,'close_date':close,'created_date':d(int(rng.integers(20,90))),'last_stage_change_date':d(int(rng.integers(1,45))),'next_step':next_step,'loss_reason':loss})
    opportunities=pd.DataFrame(opps)
    stale={'opp_007','opp_018','opp_032','opp_048','opp_055','opp_069'}; activities=[]
    for pos,row in opportunities.iterrows(): activities.append({'activity_id':f'act_{pos+1:03d}','related_object_type':'opportunity','related_object_id':row['opportunity_id'],'activity_type':['call','email','meeting'][pos%3],'activity_date':d(25+(pos%18) if row['opportunity_id'] in stale else (pos*3)%18),'owner_id':row['owner_id'],'notes_quality':['high','medium','low'][pos%3]})
    activities=pd.DataFrame(activities)
    audit=[]; eid=1
    for _,opp in opportunities.head(55).iterrows():
        for j in range(3 if opp['owner_id']=='usr_002' else 1): audit.append({'event_id':f'evt_{eid:04d}','object_type':'opportunity','object_id':opp['opportunity_id'],'field_changed':'close_date' if j%2==0 else 'forecast_category','old_value':f(10+j),'new_value':f(20+j),'changed_by':opp['owner_id'] or 'usr_005','change_type':'manual','changed_at':d((eid*2)%90),'activity_correlated':bool(j%2)}); eid+=1
    crm_audit_log=pd.DataFrame(audit)
    data_quality_checks=pd.DataFrame([['chk_001','leads','source','required_field','critical','active'],['chk_002','accounts','owner_id','required_field','critical','active'],['chk_003','contacts','account_id','relationship_integrity','high','active'],['chk_004','opportunities','close_date','forecast_governance','critical','active']],columns=['check_id','object','field','check_type','severity','status'])
    remediation_tasks=pd.DataFrame([['tsk_001','lead_source_cleanup','usr_006','high',d(4),'in_progress'],['tsk_002','account_owner_backfill','usr_005','critical',d(2),'open'],['tsk_003','forecast_category_review','usr_004','critical',f(3),'open'],['tsk_004','closed_lost_reason_policy','usr_005','high',d(7),'open'],['tsk_005','duplicate_account_merge','usr_005','medium',f(10),'completed'],['tsk_006','close_date_push_reason_code','usr_004','high',d(1),'open']],columns=['task_id','task_name','owner_id','severity','due_date','status'])
    tables=locals(); names=['leads','accounts','contacts','opportunities','users','activities','forecast_categories','stages','crm_audit_log','data_quality_checks','remediation_tasks']
    for n in names: tables[n].to_csv(PROCESSED/f'{n}.csv',index=False)
    with sqlite3.connect(DATABASE/'crm_governance_case.sqlite') as conn:
        for n in names: tables[n].to_sql(n,conn,if_exists='replace',index=False)
    print(f'Synthetic CRM governance data generated in {PROCESSED}')
if __name__=='__main__': main()
