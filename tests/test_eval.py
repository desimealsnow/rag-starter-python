from app.rag.evaluator import simple_judge

def test_judge_has_scores():
    ans = "The renewal grace period is 30 days [1]. Please refer to policy [2]."
    v = simple_judge(ans)
    assert set(v['scores'].keys()) == {'grounded','completeness','clarity'}
