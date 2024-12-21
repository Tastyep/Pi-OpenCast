API
===

| API documentation relies on `aiohttp-apispec <https://github.com/maximdanilchenko/aiohttp-apispec>`_.
| This means that the openapi specification resides with the code, next to requests handlers.

|:warning:| OpenCast should be started to access the documentation page.

.. code-block:: bash

   $ ./OpenCast.sh service back start

Visualization of the API definitions is displayed by `SwaggerUI <https://swagger.io/tools/swagger-ui/>`_ and accessible at `/api/docs <http://0.0.0.0:2020/api/docs>`_.
