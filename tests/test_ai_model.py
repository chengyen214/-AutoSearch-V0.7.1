from models.ai_analysis import AIAnalysis



analysis = AIAnalysis(

    summary="台積電2nm量產",

    category="Semiconductor",

    keywords=[

        "TSMC",

        "2nm",

        "AI Chip"

    ],

    importance=9

)



print(
    analysis.to_dict()
)


print(
    analysis
)


print(
    analysis.to_json()
)


print(
    analysis.is_valid()
)