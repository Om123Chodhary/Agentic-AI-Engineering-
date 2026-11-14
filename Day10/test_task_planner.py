from task_planner import decompose_task

user_request =  "Generate a password and tell me the current time."
tasks = decompose_task(user_request)
for task in tasks:
    print(task)