from test.util import TestCase

from OpenCast.app.controller.monitoring_schema import ErrorSchema, schema


class MonitoringSchemaTest(TestCase):
    def test_schema_no_params(self):
        with self.assertRaises(RuntimeError) as ctx:
            schema()
        self.assertEqual(
            "schema required 1 keyword argument of type dict", str(ctx.exception)
        )

    def test_schema_invalid_params(self):
        with self.assertRaises(RuntimeError) as ctx:
            schema(Schema=[1, 2])
        self.assertEqual(
            "schema required 1 keyword argument of type dict", str(ctx.exception)
        )

    def test_error_schema(self):
        ErrorSchema().load({"message": "msg", "details": {"test": "works", "test2": 1}})
