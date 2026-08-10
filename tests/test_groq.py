from ai.llm_client import LLMClient



client = LLMClient(
    "groq"
)



result = client.analyze(

"""
請分析：

台積電2nm製程進入量產，
CoWoS需求持續增加。

輸出JSON。
"""

)



print(result)