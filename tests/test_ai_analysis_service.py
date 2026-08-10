from services.ai_analysis_service import AIAnalysisService



def test_ai_analysis():


    service = AIAnalysisService()


    article = {


        "id":1,


        "title":
            "台積電AI晶片量產",


        "content":
            """
            NVIDIA與台積電合作，
            推動AI GPU與2nm製程。
            """

    }


    result = service.analyze(
        article
    )


    assert result.category == "Semiconductor"


    assert "TSMC" in result.entities or "台積電" in result.entities


    assert result.importance > 0