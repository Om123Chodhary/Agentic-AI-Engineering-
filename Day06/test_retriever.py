from retriever import load_documents,retrieve

documents = load_documents()

"""for name, text in documents.items():
    print(name)
    print(text)
    print("="*40)"""
filename, content = retrieve("Lasso L1")
print(filename)
print()
print(content)