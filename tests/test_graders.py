from evals.financial_agent.graders import answer_mentions


def test_answer_grader_accepts_a_valid_alternative_pattern() -> None:
    assert answer_mentions(
        "I couldn't find Uber transactions.",
        (("could not find", "uber"), ("couldn't find", "uber")),
    )


def test_answer_grader_rejects_an_answer_without_a_complete_pattern() -> None:
    assert not answer_mentions("I found some transactions.", (("could not find", "uber"),))
