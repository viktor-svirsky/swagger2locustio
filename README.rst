swagger2locustio
================

|Build| |Coverage| |Version| |Python versions| |Docs| |License|

swagger2locustio - a tool for testing API endpoints that have Open API / Swagger specifications using locustio tool.

It generates ``locustfile.py`` from the application schema.

**Supported specification versions**:

- Swagger 2.x
- Open API 3.x

Installation
------------

To install swagger2locustio via ``pip`` run the following command:

.. code:: bash

    pip install swagger2locustio

Usage
-----

.. code:: bash

    swagger2locustio --help

Contributing
------------

Please, see the ``CONTRIBUTING.rst`` file for more details.

License
-------

The code in this project is licensed under ``MIT license``.
By contributing to ``swagger2locustio``, you agree that your contributions
will be licensed under its MIT license.

.. |Build| image:: https://github.com/vsvirsky/swagger2locustio
   :target: https://github.com/vsvirsky/swagger2locustio/actions
.. |Coverage| image:: https://codecov.io/gh/vsvirsky/swagger2locustio/branch/master
   :target: https://codecov.io/gh/vsvirsky/swagger2locustio/branch/master
   :alt: codecov.io status for master branch
.. |Version| image:: https://img.shields.io/pypi/v/swagger2locustio.svg
   :target: https://pypi.org/project/swagger2locustio/
.. |Python versions| image:: https://img.shields.io/pypi/pyversions/swagger2locustio.svg
   :target: https://pypi.org/project/swagger2locustio/
.. |License| image:: https://img.shields.io/pypi/l/swagger2locustio.svg
   :target: https://opensource.org/licenses/MIT
.. |Docs| image:: https://readthedocs.org/projects/swagger2locustio/badge/?version=stable
   :target: https://swagger2locustio.readthedocs.io/en/stable/?badge=stable
   :alt: Documentation Status
