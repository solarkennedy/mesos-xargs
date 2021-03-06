#!/usr/bin/env python2.7
import fileinput
import logging
import uuid
import time
import sys

# Where mesos packages put their native python lib
sys.path.insert(0, '/usr/lib/python2.7/site-packages/mesos')
from native import MesosSchedulerDriver

from mesos.interface import Scheduler
from mesos.interface import mesos_pb2
import mesos.cli.cluster

logging.basicConfig(level=logging.INFO)

TASK_MEM = 24
TASK_CPUS = 0.1

def new_task(offer):
    task = mesos_pb2.TaskInfo()
    id = uuid.uuid4()
    task.task_id.value = str(id)
    task.slave_id.value = offer.slave_id.value
    task.name = "task {}".format(str(id))

    cpus = task.resources.add()
    cpus.name = "cpus"
    cpus.type = mesos_pb2.Value.SCALAR
    cpus.scalar.value = TASK_CPUS

    mem = task.resources.add()
    mem.name = "mem"
    mem.type = mesos_pb2.Value.SCALAR
    mem.scalar.value = TASK_MEM

    return task


class XargsScheduler(Scheduler):

    def __init__ (self, commands):
        self.taskData = {}
        self.tasksLaunched = 0
        self.tasksFinished = 0
        self.messagesSent = 0
        self.messagesReceived = 0
        self._cpu_alloc = 0
        self._mem_alloc = 0
        self.commands = commands
        self.command_count = len(commands)

    def registered(self, driver, framework_id, master_info):
        logging.info("Registered with framework id: {}".format(framework_id))

    def maxTasksForOffer(self, offer):
        count = 0
        cpus = next(rsc.scalar.value for rsc in offer.resources if rsc.name == "cpus")
        mem = next(rsc.scalar.value for rsc in offer.resources if rsc.name == "mem")
        while cpus >= TASK_CPUS and mem >= TASK_MEM:
            count += 1
            cpus -= TASK_CPUS
            mem -= TASK_MEM
        return count

    def resourceOffers(self, driver, offers):
        logging.info("Recieved resource offers: {}".format([o.id.value for o in offers]))
        for offer in offers:
            maxTasks = min(self.maxTasksForOffer(offer), self.command_count)
            print "maxTasksForOffer: [%d]" % maxTasks
            if commands == []:
                print "No commands left to run, not processing offer"
                print "Declining offer on [%s]" % offer.hostname
                driver.declineOffer(offer.id)
                if self.tasksFinished == self.command_count:
                    print "Looks like they all finished!"
                    sys.exit(0)
                else:
                    print "We have %d finished out of %d total" % (self.tasksFinished, self.command_count)
                continue
            tasks = []
            for i in range(maxTasks):
                task = new_task(offer)
                task.command.value = commands.pop()
                logging.info("Launching task {task} "
                             "using offer {offer}.".format(task=task.task_id.value,
                                                           offer=offer.id.value))
                tasks.append(task)
            if tasks:
                driver.launchTasks(offer.id, tasks)
            else:
                print "Declining offer on [%s]" % offer.hostname
                driver.declineOffer(offer.id)


    def statusUpdate (self, driver, update):
        """
        Invoked when the status of a task has changed (e.g., a slave
        is lost and so the task is lost, a task finishes and an
        executor sends a status update saying so, etc.) Note that
        returning from this callback acknowledges receipt of this
        status update.  If for whatever reason the scheduler aborts
        during this callback (or the process exits) another status
        update will be delivered.  Note, however, that this is
        currently not true if the slave sending the status update is
        lost or fails during that time.
        """

        logging.debug("Mesos Scheduler: task %s is in state %d", update.task_id.value, update.state)

        if update.state == mesos_pb2.TASK_FINISHED:
            self.tasksFinished += 1
            logging.info("Task %s is finished. %d total tasks done now!", update.task_id.value, self.tasksFinished)
            for stream in mesos.cli.cluster.files(flist=['stdout','stderr'], fltr=update.task_id.value):
                print "Printing %s for task %s" % (stream[0].path, update.task_id.value) 
                for line in stream[0].readlines():
                    print line


if __name__ == '__main__':
    # Get the list of commands to run
    # TODO: Get this "just in time" instead of at startup
    prefix=" ".join(sys.argv[1:])
    commands = []
    for line in fileinput.input("-"):
        commands.append("%s %s" % (prefix, line.rstrip()))
    logging.info("Executing commands: %s" % commands)
    framework = mesos_pb2.FrameworkInfo()
    framework.user = ""  # Have Mesos fill in the current user.
    framework.name = "mesos-xargs"
    driver = MesosSchedulerDriver(
        XargsScheduler(commands),
        framework,
        "zk://localhost:2181/mesos"  # assumes running on the master
    )
    driver.run()
