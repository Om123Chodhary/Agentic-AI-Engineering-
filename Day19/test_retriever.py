from retriever import retriever

result = retriever.invoke(
    "How Much job available in agentic ai field in Europe?"
)

for document in result:
    print("\n -------Documnet-------")
    print(document.page_content)