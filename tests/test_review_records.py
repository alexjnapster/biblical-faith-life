from pathlib import Path
import unittest,sys,hashlib,copy
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'evaluation'))
from assess_review import assess,DIMENSIONS
class ReviewRecordTests(unittest.TestCase):
    def setUp(self):
        self.answer='Synthetic test artifact for review binding, not a graded plugin answer.'
        self.review={'artifact_sha256':hashlib.sha256(self.answer.encode()).hexdigest(),'reviewer':'synthetic-test-reviewer','reviewed_at':'2026-10-25','independence_evidence':'separate_invocation_receipt','review_receipt_path':'synthetic-fixture-only','dimensions':{k:{'rating':3,'evidence_quote':'Synthetic test artifact','reason':'Synthetic fixture exercising record validation'} for k in DIMENSIONS},'critical_findings':[],'objective_checks':[]}
    def test_complete_records_do_not_claim_semantic_pass(self):
        self.assertEqual(assess(self.answer,self.review)['status'],'review_records_complete')
    def test_stale_review_does_not_validate_changed_answer(self):
        self.assertEqual(assess(self.answer+' Changed.',self.review)['status'],'pending')
    def test_high_ratings_cannot_override_critical_failure(self):
        self.review['critical_findings']=[{'kind':'fabricated_source_or_execution','resolved':False}]
        self.assertEqual(assess(self.answer,self.review)['status'],'revision_required')
    def test_invented_excerpt_is_pending(self):
        self.review['dimensions']['genre_composition']['evidence_quote']='Text not in the answer'
        self.assertEqual(assess(self.answer,self.review)['status'],'pending')
    def test_actor_label_alone_does_not_establish_separate_review(self):
        self.review['independence_evidence']='reviewer-2'
        self.assertEqual(assess(self.answer,self.review)['status'],'pending')
    def test_missing_dimension_cannot_hide_behind_average(self):
        del self.review['dimensions']['evidence_accuracy']
        self.assertEqual(assess(self.answer,self.review)['status'],'pending')
    def test_objective_check_requires_execution_evidence(self):
        self.review['objective_checks']=[{'name':'word_count','status':'not_run'}]
        self.assertEqual(assess(self.answer,self.review)['status'],'pending')
if __name__=='__main__':unittest.main()
