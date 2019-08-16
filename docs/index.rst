.. recast-workflow documentation master file, created by
   sphinx-quickstart on Wed Aug 14 19:57:35 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

recast-workflow
===========================================

The main purpose of recast-workflow is to supply workflows. A workflow is divided into a set of **steps** (currently: **generation**, **selection**, and **statistics**). 
Each step has multiple implementations (**subworkflows**) that are described in this package. recast-workflow's job is to:

1. Connect subworkflows into a runnable workflow for a recast frontend.
2. Provide frontends with information about the subworkflows.

.. note::
    recast-workflow is one of many projects under the recast-hep_ umbrella.
    If you are a user of recast, it is likely that you should instead consult the `recast docs`_. 

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   
.. toctree::
    :maxdepth: 2
    :hidden:
    :caption: Design

    design/make_workflow.rst
    design/catalogue_query.rst

.. _recast-hep: https://github.com/recast-hep

.. _`recast docs`: http://recast-docs.web.cern.ch

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
