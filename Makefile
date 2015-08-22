.PHONY: itest

TEST_CMD:=seq 1 10 |  ./mesos_xargs.py echo

itest:
	tox -e itest
	bash -c 'source .tox/itest/bin/activate && ($(TEST_CMD))'
