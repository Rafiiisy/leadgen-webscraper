import time
from src.llm import query_llm, build_llm2_prompt
from src.vectorstore import HybridRetriever

def generate_insight(domain: str, task: str, top_k: int = 5, retries: int = 3, wait_sec: int = 3) -> str:
    print(f"\n🔍 Generating Insight for: {domain}")
    print("=" * 60)

    try:
        # 🔍 Retrieve top-k chunks
        retriever = HybridRetriever(domain=domain)
        raw_chunks = retriever.search(task, top_k=top_k)
        chunks = [{"category": "Retrieved", "text": chunk} for chunk in raw_chunks]

        if not chunks:
            print("⚠️ No chunks found for the task. Skipping LLM step.")
            return "[No relevant chunks found.]"

        # 📦 Preview top chunks
        print("\n📦 Top Retrieved Chunks:\n")
        for i, chunk in enumerate(chunks):
            text = chunk.get("text", "")
            if isinstance(text, str):
                preview = text[:300] + ("..." if len(text) > 300 else "")
            else:
                preview = "[Invalid text content]"
            print(f"[{i+1}] {preview}\n")

        # 🧠 Build prompt
        prompt = build_llm2_prompt(task, chunks)
        print("\n🧠 LLM Prompt Preview (First 500 chars):\n")
        print(prompt[:500])
        print("-" * 50)

        # 🔁 Retry LLM calls
        for attempt in range(1, retries + 1):
            result = query_llm(prompt)
            if result and "[Error" not in result and result.strip():
                break
            print(f"\n🔁 Retry {attempt}/{retries} after failure:\n{result[:100]}")
            time.sleep(wait_sec)
        else:
            result = "[Error] LLM failed after all retries."

        print("\n✅ Final LLM Output:\n")
        print(result)

        return result

    except Exception as e:
        print(f"❌ Exception during insight generation: {e}")
        return f"[Error] {str(e)}"

# Optional direct test runner
if __name__ == "__main__":
    result = generate_insight(
        domain="https://www.capraecapital.com/",
        task="List all the services this company offers"
    )
    print("\n🧠 Final Result:\n", result)
