from agent import research_agent, generate_report
from tools import get_verified_research_notes

request = ( "Research the role of AI Agents "
"in software development. identify major use cases, benifits, and limitations.")


answer = research_agent(
    request, max_steps = 7
)

verified_notes = (get_verified_research_notes())

print("\n Verified finding:",len(verified_notes))

report = generate_report(
    user_request = request,
    verified_notes = verified_notes
)

print("="*20)
print("\nFINAL ANSWER\n")
print("="*20)
print(report)