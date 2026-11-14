from pathlib import Path

from advance_rag import(build_rag,retrieve)
from generator import(generate_answer)

DOCUMENT_PATH = (
    Path("documents")/"python.txt"
)

def main():
    text = DOCUMENT_PATH.read_text(
        encoding="utf-8"
    )
    print("Building RAG Knowledge Base...")

    build_rag(text,DOCUMENT_PATH.name)

    print("\nAdvanced RAG is ready.")

    while True:
        query = input("/nYou:").strip()
        if query.lower() in {"exit","quit"}:
            break
        results = retrieve(query,top_k=5)

        print("\nRetrieved Sources:")

        for result in results:
            print(
                f"-"
                f"Source: {result["source"]}"
                f"(Chunk"
                f"{result['chunk_id']})"
            )

        Answer = generate_answer(query,results)

        print("\nRAG")
        print(Answer)
if __name__ == "__main__":
    main()