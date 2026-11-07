from state import *
state = create_state(
    "Generate a password and tell me the current time."
)
print("Intial State")
print(state)
add_action(state,"generate_password")
record_observation(state, "generate_password","password: PX#@h4P/9*6w" )
next_step(state)

print("\nState After One Iteration")
print(state)

finish(state,"Password:PX#@h4P/9*6w\n Current Time:10:35AM")
print("\nFinal State")
print(state)
