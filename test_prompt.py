from ai.prompt import PromptBuilder


content = """
台積電宣布2nm製程進入量產。
NVIDIA推出新一代AI GPU。
CoWoS先進封裝需求增加。
"""


builder = PromptBuilder()


prompt = builder.build(content)


print(prompt)