"""
Test KnowledgeRepository

AutoSearch V4

P1.1 Step 3.3

"""


from models.knowledge import Knowledge

from database.knowledge_repository import KnowledgeRepository





def test_knowledge_repository():



    repo = KnowledgeRepository()



    knowledge = Knowledge(


        article_id=8,


        topic="Semiconductor AI",


        entities="TSMC,NVIDIA,HBM",


        relations="TSMC produces chips",


        knowledge_version="1.0"


    )





    result = repo.insert(knowledge)





    print(

        "Knowledge ID:",

        result.id

    )





    assert result.id is not None





    print(

        "✅ KnowledgeRepository OK"

    )






if __name__ == "__main__":


    test_knowledge_repository()