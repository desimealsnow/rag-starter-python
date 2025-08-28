import re

def simple_judge(answer_text: str):
    # Grounded: must include at least one [n] citation
    grounded = 5 if re.search(r"\[\d+\]", answer_text) else 2
    completeness = 4 if len(answer_text.split()) > 15 else 2
    clarity = 5 if "as an AI" not in answer_text and not re.search(r"[A-Z]{6,}", answer_text) else 3
    avg = (grounded + completeness + clarity) / 3
    verdict = "pass" if avg >= 4 else "needs-review"
    return {"scores": {"grounded": grounded, "completeness": completeness, "clarity": clarity}, "verdict": verdict}
