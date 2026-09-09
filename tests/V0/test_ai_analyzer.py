"""
test_ai_analyzer.py

AutoSearch V3

P4.4.2

測試:

    AIAnalyzer

功能:

    1. AI文字分析
    2. AIAnalysis Model
    3. Metadata驗證

"""


from ai.analyzer import AIAnalyzer




# ======================================
# 測試文章
# ======================================


text = """

台積電宣布2nm製程正式量產，

AI Chip需求快速增加，

先進封裝CoWoS產能持續擴張。

"""





# ======================================
# 建立 Analyzer
# ======================================


analyzer = AIAnalyzer()






# ======================================
# 執行 AI Analysis
# ======================================


result = analyzer.analyze(

    text

)







# ======================================
# Dictionary Output
# ======================================


print()

print("=" * 50)

print("AI Analysis Dictionary")

print("=" * 50)


print(

    result.to_dict()

)








# ======================================
# JSON Output
# ======================================


print()

print("=" * 50)

print("AI Analysis JSON")

print("=" * 50)


print(

    result.to_json()

)








# ======================================
# Object Output
# ======================================


print()

print("=" * 50)

print("AI Analysis Object")

print("=" * 50)


print(

    result

)








# ======================================
# Validation
# ======================================


print()

print("=" * 50)

print("Validation")

print("=" * 50)



print(

    result.is_valid()

)






# ======================================
# Metadata Check
# ======================================


print()

print("=" * 50)

print("AI Metadata")

print("=" * 50)



print(

    "Model:",

    result.ai_model

)


print(

    "Version:",

    result.ai_version

)


print(

    "Confidence:",

    result.confidence

)


print(

    "Analyze Time:",

    result.analyze_time

)