from models.knowledge import Knowledge




def test_knowledge():


    knowledge = Knowledge(

        article_id=1,

        topic="Advanced Semiconductor",

        entities=[

            "TSMC",

            "CoWoS",

            "NVIDIA"

        ],

        relations=[

            "TSMC produces 2nm",

            "NVIDIA uses CoWoS"

        ]

    )



    assert knowledge.article_id == 1


    assert knowledge.topic == "Advanced Semiconductor"


    assert knowledge.has_knowledge is True


    assert len(knowledge.entity_list) == 3


    assert len(knowledge.relation_list) == 2



    print(

        "Knowledge Model OK"

    )





if __name__ == "__main__":

    test_knowledge()