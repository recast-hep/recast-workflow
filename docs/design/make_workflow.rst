Making Workflows
================

Workflows can be made using the `scripts/make_workflow.py` python script.
A list of subworkflows are input, detailing for each subworkflow its step, name, inputs, and settings.

Subworkflow Parameters
----------------------

Each subworkflow ultimately has a set of input parameters that need to be passed to it. 
However, there are two complications: interface parameters and common parameters.

Interface Parameters
^^^^^^^^^^^^^^^^^^^^

In order to communicate, steps need to agree on what is output from one step and input to the next. 
Depending on the use case, what this should be changes. Therefore, steps specify input and output interfaces that they agree to follow.
The user does not need to specify the interface parameters.

Common Parameters
^^^^^^^^^^^^^^^^^

Some parameters are common to all implementations of a step. For example, the selection step must always specify a set of analyses to be used.
Since theorists will seek analyses that are sensitive to their new model, it is useful to provide this notion of common parameters.
A theorist can then ask which tools support the analyses that they wish to use.

Since each subworkflow might have a different internal representation of the common parameters, they provide a script to translate.
make_workflow uses these scripts to translate any common parameters that are passed.


Environment Settings
--------------------

Some subworkflows have environment settings, for example, the version of the tool.
Each subworkflow provides a script that provides an adjusted workflow and performs any necessary preparation.