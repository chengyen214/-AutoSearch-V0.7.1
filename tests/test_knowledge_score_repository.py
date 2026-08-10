"""
test_knowledge_score_repository.py

AutoSearch V4

P1.5 Step 3

Knowledge Score Repository Test

測試:

1. Insert Score

2. Get By Knowledge ID

3. Find Top Ranking

4. Find By Score

5. Update Score

"""


from database.knowledge_score_repository import (
    KnowledgeScoreRepository
)


from models.knowledge_score import (
    KnowledgeScore
)





def test_knowledge_score_repository():



    repo = KnowledgeScoreRepository()





    # ==================================
    # Insert
    # ==================================


    score = KnowledgeScore(

        knowledge_id=1,

        importance=9,

        confidence=0.9,

        quality_score=8.5,

        freshness_score=9,

        ranking_score=8.8

    )



    result = repo.insert(

        score

    )



    print()

    print("================")

    print("Insert Score")

    print("================")

    print(

        result.to_dict()

    )



    assert result.id is not None







    # ==================================
    # Get By Knowledge ID
    # ==================================


    data = repo.get_by_knowledge_id(

        1

    )



    print()

    print("================")

    print("Get Knowledge Score")

    print("================")

    print(

        data

    )



    assert data is not None

    assert data["knowledge_id"] == 1







    # ==================================
    # Top Ranking
    # ==================================


    top = repo.find_top(

        10

    )



    print()

    print("================")

    print("Top Ranking")

    print("================")

    print(

        top

    )



    assert len(top) > 0







    # ==================================
    # Score Filter
    # ==================================


    high_score = repo.find_by_score(

        8

    )



    print()

    print("================")

    print("Score >= 8")

    print("================")

    print(

        high_score

    )



    assert len(high_score) > 0







    # ==================================
    # Update
    # ==================================


    update_score = KnowledgeScore(

        knowledge_id=1,

        importance=10,

        confidence=0.95,

        quality_score=9,

        freshness_score=10,

        ranking_score=9.5

    )



    repo.update(

        1,

        update_score

    )




    updated = repo.get_by_knowledge_id(

        1

    )



    print()

    print("================")

    print("Updated Score")

    print("================")

    print(

        updated

    )



    assert updated["ranking_score"] == 9.5