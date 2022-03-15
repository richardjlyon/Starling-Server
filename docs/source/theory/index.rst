How it works
=========================================

The purpose of the library is to abstract APIs provided by banks into a defined API.

Financial providers e.g. banks typically provide an authorisation token. This token authorises requests made through an
API to interact with one or more accounts that the token authorises.

API class
---------
The working object in the library is the `API` class. This class implements methods defined in an abstract base class
for a specific bank API. An instance of the class is created for each account. Each instance provides methods for
invoking the bank's API and returning its results.

Persistence
-----------

Customisation
-------------

Categorisation
--------------

..  toctree::
    :maxdepth: 3
    :caption: Program Architecture

    program_architecture