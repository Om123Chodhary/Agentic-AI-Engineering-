from openai import OpenAI
from dotenv import load_dotenv
import os

from research_agent import research
from coding_agent import write_code
from reviewer_agent import review
from state import create_state

load_dotenv()

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

VALID_WORKERS = {"research", "coding", "review", "finish"}


def choose_worker(state):
    prompt = f"""You are the Manager Agent. Your job is to decide which worker should act NEXT.

Original Task: {state["task"]}

Current State:
- Research done: {bool(state["research"].strip())}
- Code done: {bool(state["code"].strip())}
- Review done: {bool(state["review"].strip())}
- History: {state["history"]}

Rules:
1. If research is empty -> choose "research"
2. If research exists but code is empty -> choose "coding"
3. If code exists but review is empty -> choose "review"
4. If research, code AND review all exist -> choose "finish"

STRICT OUTPUT RULE:
Reply with EXACTLY ONE word from this list and nothing else:
research
coding
review
finish

Your answer:"""

    response = client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0,          # deterministic
        max_tokens=5,           # sirf ek word
    )

    raw = response.choices[0].message.content.strip().lower()

    # Clean karo: extra words, punctuation hatao
    for w in VALID_WORKERS:
        if w in raw:
            return w

    # Fallback: agar LLM ne kuch aur bola to state se decide karo
    if not state["research"].strip():
        return "research"
    if not state["code"].strip():
        return "coding"
    if not state["review"].strip():
        return "review"
    return "finish"


def run_manager(task):
    state = create_state(task)
    max_steps = 10  # for stop infinite loop 

    for step in range(max_steps):
        worker = choose_worker(state)
        print(f"\n[Step {step+1}] Manager Selected: {worker}")

        # Guard: already done No repeat again
        if worker == "research" and state["research"].strip():
            print("⚠️ Research already done, skipping...")
            worker = "coding" if not state["code"].strip() else "review"

        if worker == "coding" and state["code"].strip():
            print("⚠️ Code already done, skipping...")
            worker = "review" if not state["review"].strip() else "finish"

        if worker == "review" and state["review"].strip():
            print("⚠️ Review already done, skipping...")
            worker = "finish"

        # Execute worker
        if worker == "research":
            state["research"] = research(state["task"])
            state["history"].append("research")

        elif worker == "coding":
            state["code"] = write_code(state["task"], state["research"])
            state["history"].append("coding")

        elif worker == "review":
            state["review"] = review(state["task"], state["code"])
            state["history"].append("review")

        elif worker == "finish":
            print("\n✅ All tasks completed!")
            break

        else:
            raise ValueError(f"Unknown worker: {worker}")

    else:
        print("\n⚠️ Max steps reached — possible loop detected")

    return state