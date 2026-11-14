from model import model
from prompt import prompt
from langchain_core.output_parsers import StrOutputParser


# 1. Create Output Parser 
parser = StrOutputParser()

#2. Create Chain
chain = prompt | model | parser

#2. Chain Invoke
user_question = "What is an autonomous AI agent in 2 sentences?"
response = chain.invoke({"question": user_question})

# 4. Print Output (now not need .content)
print("Response:")
print(response)
