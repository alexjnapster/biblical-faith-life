from pathlib import Path
import json,copy
ROOT=Path(__file__).resolve().parents[1]
base=json.loads((ROOT/'evaluation/cases.json').read_text())['cases']
selected=['bible-reading-plan','deep-exegesis','church-ua-integration','textual-criticism','sermon-studio','pastoral-care']
extra=[]
for slug in selected:
    original=next(c for c in base if c['skill']==slug and c['mode']=='ordinary')
    for code,name in [('en','English'),('ru','Russian')]:
        c=copy.deepcopy(original);c.update(id=slug+'__language_'+code,language=code,mode='language_transfer',paired_case_id=original['id'])
        c['prompt']=c['prompt'].replace('Answer in Ukrainian.','Answer in '+name+'.')
        c['acceptance'].append('Use the requested language naturally and preserve the same meaning, facts and doctrinal scope as the paired Ukrainian task.')
        extra.append(c)
for slug in ['deep-exegesis','church-leadership-advisor','church-ua-integration','christian-report']:
    original=next(c for c in base if c['skill']==slug and c['mode']=='misleading')
    for n in [2,3]:
        c=copy.deepcopy(original);c.update(id=original['id']+'__repeat_'+str(n),mode='repeatability',paired_case_id=original['id']);extra.append(c)
(ROOT/'evaluation/extended-cases.json').write_text(json.dumps({'schema_version':1,'cases':extra},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'core_cases':len(base),'language_cases':12,'repeat_cases':8,'total_cases_per_host':len(base)+len(extra)}))
