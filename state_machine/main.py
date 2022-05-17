import os
from fakecubesat import pocketqube as cubesat
import state_machine

_ = state_machine.start_state_machine(cubesat)


# print('Loading Tasks...', end='')
# # schedule all tasks in directory
# for file in os.listdir('Tasks'):
#     # remove the '.py' from file name
#     file = file[:-3]

#     # ignore these files
#     if file in ("template_task", "test_task", "listen_task", "__pycach") or file.startswith('._'):
#         continue

#     # auto-magically import the task file
#     # pylint: disable=exec-used
#     exec(f"import Tasks.{file}")
#     # pylint: enable=exec-used

#     # create a helper object for scheduling the task
#     # pylint: disable=eval-used
#     task_obj = eval('Tasks.'+file).task(cubesat)
#     # pylint: enable=eval-used

#     # determine if the task wishes to be scheduled later
#     if hasattr(task_obj, 'schedule_later'):
#         schedule = cubesat.tasko.schedule_later
#     else:
#         schedule = cubesat.tasko.schedule

#     # schedule each task object and add it to our dict
#     cubesat.scheduled_tasks[task_obj.name] = schedule(
#         task_obj.frequency, task_obj.main_task, task_obj.priority)

# print(len(cubesat.scheduled_tasks), 'total')

print('Running...')
try:
    # should run forever
    cubesat.tasko.run()
except Exception as e:
    print(f"FATAL ERROR: {e}")
    try:
        # increment our NVM error counter
        cubesat.c_state_err += 1
        # try to log everything
        cubesat.log('{},{},{}'.format(e, cubesat.c_state_err, cubesat.c_boot))
    except:
        pass

# we shouldn't be here!
print('Engaging fail safe: hard reset')
# from time import sleep
# sleep(10)
# cubesat.micro.on_next_reset(cubesat.micro.RunMode.NORMAL)
# cubesat.micro.reset()
