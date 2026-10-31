"""Validate review evidence. Reviewer judgments remain judgments, never automated truth."""
from pathlib import Path
import json,hashlib,argparse
DIMENSIONS={'instruction_fidelity','evidence_accuracy','doctrinal_fidelity','intellectual_depth','genre_composition','language','practical_usefulness'}
def assess(answer,review):
    pending=[];failed=[]
    digest=hashlib.sha256(answer.encode()).hexdigest()
    if review.get('artifact_sha256')!=digest:pending.append('Review is missing or bound to different answer bytes')
    if not review.get('reviewer') or not review.get('reviewed_at'):pending.append('Missing reviewer provenance')
    if review.get('independence_evidence') not in ['separate_invocation_receipt','external_human_review_receipt']:
        pending.append('Separate review evidence not supplied; an actor label is insufficient')
    if not review.get('review_receipt_path'):pending.append('Missing separate review receipt locator')
    ratings=review.get('dimensions',{})
    if set(ratings)!=DIMENSIONS:pending.append('Every rubric dimension must be assessed')
    for name,item in ratings.items():
        score=item.get('rating')
        if type(score) is not int or not 0<=score<=4:pending.append(name+': invalid rating')
        elif score<3:failed.append(name+': material revision required')
        evidence=item.get('evidence_quote','')
        if not evidence or evidence not in answer:pending.append(name+': evidence must identify actual answer text')
        if not item.get('reason'):pending.append(name+': assessment lacks reasoning')
    critical=review.get('critical_findings')
    if not isinstance(critical,list):pending.append('Critical findings have not been assessed')
    else:
        for finding in critical:
            if finding.get('resolved') is not True:failed.append('Unresolved critical finding: '+finding.get('kind','unspecified'))
    checks=review.get('objective_checks')
    if not isinstance(checks,list):pending.append('Objective checks have not been assessed')
    else:
        for check in checks:
            if check.get('status')!='verified' or not check.get('evidence_path'):pending.append('Objective check lacks actual verification evidence')
    status='revision_required' if failed else ('pending' if pending else 'review_records_complete')
    return {'status':status,'artifact_sha256':digest,'failures':failed,'pending':pending,'limitation':'This validates supplied review records and content binding. It does not authenticate reviewer identity, inspect linked receipt files, verify factual truth or certify quality.'}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('answer');p.add_argument('review');a=p.parse_args()
    print(json.dumps(assess(Path(a.answer).read_text(),json.loads(Path(a.review).read_text())),indent=2))
