"""
tests/test_ai_analysis_model.py

AutoSearch V4

P2.2.5 Step 2

AI Analysis Model Test

"""


from models.ai_analysis import AIAnalysis





# ==================================================
# Basic Model Test
# ==================================================

def test_ai_analysis_model():


    analysis = AIAnalysis(


        article_id=1,


        summary="AI Semiconductor analysis",


        category="Semiconductor",


        keywords=[

            "AI",

            "2nm",

            "CoWoS"

        ],


        importance=9,


        entities=[

            "台積電",

            "NVIDIA"

        ],


        relations=[

            "台積電 -> 生產 -> AI晶片"

        ],


        ai_model="GPT-5",


        ai_version="4.0",


        confidence=0.95,


        status="completed"


    )



    data = analysis.to_dict()



    assert data["article_id"] == 1


    assert data["category"] == "Semiconductor"


    assert "AI" in data["keywords"]


    assert "台積電" in data["entities"]


    assert len(data["relations"]) == 1


    assert data["importance"] == 9


    assert data["status"] == "completed"







# ==================================================
# JSON Convert Test
# ==================================================

def test_ai_analysis_json():


    analysis = AIAnalysis(


        article_id=2,


        summary="Test AI"


    )



    json_data = analysis.to_json()



    assert isinstance(

        json_data,

        str

    )



    assert "Test AI" in json_data







# ==================================================
# Dict Restore Test
# ==================================================

def test_ai_analysis_from_dict():


    data = {



        "id":10,


        "article_id":3,


        "summary":"AI Chip",


        "category":"Technology",


        "keywords":[

            "GPU"

        ],


        "importance":8,


        "entities":[

            "NVIDIA"

        ],


        "relations":[

            "NVIDIA -> GPU"

        ],


        "status":"completed"



    }



    analysis = AIAnalysis.from_dict(

        data

    )



    assert analysis.id == 10


    assert analysis.article_id == 3


    assert analysis.summary == "AI Chip"


    assert analysis.keywords == [

        "GPU"

    ]


    assert analysis.entities == [

        "NVIDIA"

    ]


    assert analysis.status == "completed"







# ==================================================
# Validation Test
# ==================================================

def test_ai_analysis_validation():


    empty = AIAnalysis()



    assert empty.is_valid() is False




    analysis = AIAnalysis(


        summary="valid"


    )



    assert analysis.is_valid() is True







# ==================================================
# Async Pipeline Status Test
# ==================================================

def test_ai_analysis_status():


    analysis = AIAnalysis(


        article_id=5

    )



    assert analysis.status == "pending"



    analysis.mark_completed()



    assert analysis.status == "completed"


    assert analysis.error_message == ""




    analysis.mark_failed(

        "AI timeout"

    )



    assert analysis.status == "failed"


    assert analysis.error_message == "AI timeout"