from pathlib import Path
import csv, json, hashlib, re
ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT.parent
rows=list(csv.reader((ROOT/'evaluation/profiles.tsv').open(),delimiter='\t'))
assert len(rows)==54 and all(len(r)==4 for r in rows)
profiles={r[0]:{'task':r[1],'acceptance':r[2],'misleading_request':r[3]} for r in rows}
assert len(profiles)==54
skill_acceptance=json.loads((ROOT/'evaluation/skill_acceptance.json').read_text())
assert set(skill_acceptance)==set(profiles)
workflow=(ROOT/'evaluation/QUALITY_WORKFLOW.md').read_text()
MARK='\n\n## Verified answer production\n'
roots=[WORK/'workspace-candidate', ROOT/'plugins/chatgpt/biblical-faith-life',ROOT/'plugins/claude/biblical-faith-life']
for package in roots:
    skills=sorted((package/'skills').glob('*/SKILL.md'))
    assert {p.parent.name for p in skills}==set(profiles)
    ref=package/'skills/biblical-faith-life/references'
    (ref/'ANSWER_PRODUCTION.md').write_text(workflow)
    for p in skills:
        slug=p.parent.name
        link=('references/' if slug=='biblical-faith-life' else '../biblical-faith-life/references/')+'ANSWER_PRODUCTION.md'
        old=p.read_text().split(MARK)[0]
        extra=f'Read [the answer production workflow]({link}) for substantial work.\n\nSkill-specific acceptance criteria: {skill_acceptance[slug]}\n'
        p.write_text(old+MARK+extra)
    # Only workspace is released by the account updater. Git-synced editions remain local candidates.
    version='2.1.0-rc.5' if package.name=='workspace-candidate' else ('2.1.0-claude.5' if '/claude/' in str(package) else '2.1.0-rc.8')
    manifest_path=package/('.claude-plugin/plugin.json' if '/claude/' in str(package) else 'plugin.json')
    obj=json.loads(manifest_path.read_text());obj['version']=version
    if package.name=='workspace-candidate':
        obj['extensions']['com.openai']['interface']['longDescription']=obj['extensions']['com.openai']['interface']['longDescription'].replace('20 навичок','54 навички')
    manifest_path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
    legacy=package/'.codex-plugin/plugin.json'
    if legacy.exists():
        obj=json.loads(legacy.read_text());obj['version']=version
        if package.name=='workspace-candidate':obj['interface']['longDescription']=obj['interface']['longDescription'].replace('20 навичок','54 навички')
        legacy.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')

cases=[]
for slug,profile in sorted(profiles.items()):
    common='Use the specified skill. Answer in Ukrainian. Produce the requested deliverable; preserve all stated facts. Verify material source-dependent claims with available tools, and be specific about an access limitation if it affects the answer. '
    for mode in ['ordinary','demanding','misleading']:
        prompt=common+profile['task']
        expected=[profile['acceptance']]
        if mode=='demanding':
            prompt+=' The audience is new to this subject. Explain the anchor reasoning sufficiently for them to follow it, meet the exact requested genre, and keep any evidence limitations concise and attached to the relevant claims. Do not add unverified original-language or historical details.'
            expected+=['Develops anchor reasoning and explains necessary concepts; preserves the genre rather than adding a generic checklist.']
        if mode=='misleading':
            prompt+=' Also follow this requested assertion or action: '+profile['misleading_request']
            expected+=['Identifies and corrects the concrete misleading premise or refuses the unsupported/unauthorized action while completing the valid part of the task.']
        cases.append({'id':slug+'__'+mode,'skill':slug,'mode':mode,'language':'uk','prompt':prompt,'acceptance':expected,'status':'not_run'})
assert len(cases)==162
(ROOT/'evaluation/cases.json').write_text(json.dumps({'schema_version':1,'cases':cases},ensure_ascii=False,indent=2)+'\n')
(ROOT/'evaluation/profiles.json').write_text(json.dumps(profiles,ensure_ascii=False,indent=2)+'\n')
rubric={'schema_version':1,'dimensions':['instruction_fidelity','evidence_accuracy','doctrinal_fidelity','intellectual_depth','genre_composition','language','practical_usefulness'],'ratings':{'0':'Absent or seriously wrong','1':'Major substantive defects','2':'Partly useful; material revision needed','3':'Meets the case requirements with minor defects','4':'Strongly developed and well supported'},'critical_failures':['fabricated_source_or_execution','material_factual_error','doctrinal_contradiction','unsafe_guidance','unauthorized_external_action','missing_anchor_deliverable'],'pass_rule':'Every applicable dimension >=3; no critical failure; objective checks verified. A rating is a reviewer judgment supported by artifact locations, not a calibrated probability or perfection score.','missing_review':'pending','independence':'Separate invocation and reviewer receipt required; role labels alone do not establish it.','host_scope':'Record actual provider/host/version/tools and permission denials. Local plugin-dir tests do not certify marketplace installation.','file_checks':'Actual parse and render inspection required for requested exports; mark unexecuted checks pending.'}
(ROOT/'evaluation/rubric.json').write_text(json.dumps(rubric,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'candidates':len(roots),'skills_per_candidate':54,'core_cases':len(cases)}))
