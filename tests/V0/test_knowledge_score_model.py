from models.knowledge_score import KnowledgeScore



def test_score_model():


    score = KnowledgeScore(

        knowledge_id=1,

        importance=9,

        confidence=0.9,

        quality_score=8.5,

        freshness_score=9,

        ranking_score=8.8

    )


    print()

    print("================")

    print("Knowledge Score")

    print("================")


    print(score.to_dict())


    assert score.knowledge_id == 1

    assert score.is_high_quality is True

    assert score.score_level == "HIGH"