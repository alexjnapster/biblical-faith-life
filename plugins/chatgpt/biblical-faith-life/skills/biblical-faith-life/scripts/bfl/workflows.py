"""Explicit stage records with review bindings to all underlying manuscripts."""
import uuid
import copy
from .engines import sha

REVIEW_STAGES={'interpretation-review','sermon-red-team','christian-publication-editor'}
class Workflow:
    def __init__(self,registry,workflow,language='uk',stages=None):
        if workflow not in registry['workflows']:raise ValueError('Unknown workflow')
        if language not in {'uk','en','ru'}:raise ValueError('Unsupported language')
        self.id=str(uuid.uuid4());self.name=workflow;self.language=language
        declared=registry['workflows'][workflow]['stages']
        if stages is not None:
            if workflow!='biblical-research-laboratory' or not isinstance(stages,list) or not stages or len(set(stages))!=len(stages) or [s for s in declared if s in stages]!=stages or stages[0]!='deep-exegesis' or stages[-1]!='interpretation-review':raise ValueError('Only research specialists are optional; preserve exegesis, final review, and declared order')
            declared=stages
        self.stages=list(declared);self.results={}
    def record(self,stage,content,actor):
        if stage not in self.stages:raise ValueError('Unregistered workflow stage')
        if not isinstance(content,str) or not content.strip() or not isinstance(actor,str) or not actor.strip():raise ValueError('Content and actor must be nonempty text')
        index=self.stages.index(stage)
        if any(s not in self.results for s in self.stages[:index]):raise ValueError('Earlier stages incomplete')
        self.results[stage]={'content':content,'actor':actor,'sha256':sha(content)}
        for s in self.stages[index+1:]:self.results.pop(s,None)
    def review(self,stage,content,reviewer):
        if stage not in REVIEW_STAGES:raise ValueError('This stage is not a review stage')
        index=self.stages.index(stage);inputs=[s for s in self.stages[:index] if s not in REVIEW_STAGES]
        if not inputs or any(s not in self.results for s in inputs):raise ValueError('No artifact to review')
        if any(reviewer==self.results[s]['actor'] for s in inputs):raise PermissionError('Independent reviewer required')
        hashes={s:self.results[s]['sha256'] for s in inputs}
        self.record(stage,content,reviewer);self.results[stage]['reviewed_inputs']=hashes
    def snapshot(self):
        complete=all(s in self.results for s in self.stages)
        for i,s in enumerate(self.stages):
            if s in REVIEW_STAGES:
                inputs=[p for p in self.stages[:i] if p not in REVIEW_STAGES]
                hashes={p:self.results[p]['sha256'] for p in inputs if p in self.results}
                if not inputs or len(inputs)!=len(hashes) or self.results.get(s,{}).get('reviewed_inputs')!=hashes:complete=False
        return {'id':self.id,'workflow':self.name,'language':self.language,'stages':list(self.stages),'results':copy.deepcopy(self.results),'status':'recorded' if complete else 'incomplete','scope':'Recorded stages are not automatic quality certification'}

    @classmethod
    def from_snapshot(cls,registry,snapshot):
        """Revalidate every saved record and review before resuming a workflow.

        A file is untrusted state, not permission or proof that an actor exists.
        Stored status is deliberately ignored and derived again from records.
        """
        if not isinstance(snapshot,dict):raise ValueError('Checkpoint must be an object')
        if not isinstance(snapshot.get('id'),str):raise ValueError('Checkpoint ID is missing')
        try:uuid.UUID(snapshot['id'])
        except (ValueError,AttributeError):raise ValueError('Invalid checkpoint ID') from None
        name=snapshot.get('workflow');stages=snapshot.get('stages');results=snapshot.get('results')
        if not isinstance(stages,list) or not isinstance(results,dict):raise ValueError('Invalid checkpoint stages or records')
        if name not in registry['workflows']:raise ValueError('Unknown checkpoint workflow')
        declared=registry['workflows'][name]['stages']
        w=cls(registry,name,snapshot.get('language'),stages=stages if stages!=declared else None)
        if stages!=w.stages or set(results)-set(stages):raise ValueError('Checkpoint contains unregistered stages')
        seen_gap=False
        for stage in stages:
            if stage not in results:seen_gap=True;continue
            if seen_gap:raise ValueError('Checkpoint has records after an incomplete earlier stage')
            result=results[stage]
            if not isinstance(result,dict) or not isinstance(result.get('content'),str) or result.get('sha256')!=sha(result['content']):raise ValueError('Checkpoint stage hash is invalid')
            if stage in REVIEW_STAGES:
                w.review(stage,result['content'],result.get('actor'))
                if result.get('reviewed_inputs')!=w.results[stage]['reviewed_inputs']:raise ValueError('Checkpoint review is stale or incomplete')
            else:
                if 'reviewed_inputs' in result:raise ValueError('Ordinary stage cannot impersonate a review')
                w.record(stage,result['content'],result.get('actor'))
        w.id=snapshot['id']
        return w
