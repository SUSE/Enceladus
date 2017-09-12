monitoring
==========

A collection of plugins for Nagios/Icinga that we use to monitor our update
infrastructure in the Public Cloud. We could not find any existing plugins
for these use cases.

All scripts are licensed under GPL version 2.0

# check_proc_timed_hang

The script monitors a given process and if the process runs longer than the
specified time it is marked as critical or optionally killed. If the kill
operation fails the process is also marked as critical.

This is useful to monitor long running processes that may get stuck. One needs
to have an idea about the expected run time of the process. This is not useful
for monitoring time critical processes. The check can only be used on processes
that have a singular instance, i.e. there can only be one entry in the process
table for the process with the given name.

# check_dir_empty

The script monitors that the given directory is/remains empty or does not
exist
