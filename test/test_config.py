from os import environ

from OpenCast.config import Config, ConfigContentError, ConfigError

from .util import TestCase


class ConfigTest(TestCase):
    def test_get_simple(self):
        config = Config({"a": 1})
        self.assertEqual(1, config["a"])

    def test_get_nested(self):
        config = Config({"a": {"b": 1}})
        self.assertEqual(1, config["a.b"])

    def test_get_subconfig(self):
        config = Config({"a": {"b": 1}})
        self.assertIsInstance(config["a"], Config)
        self.assertEqual(1, config["a"]["b"])

    def test_override_from_env(self):
        environ["OPENCAST_A"] = "2"
        config = Config({"a": 1}, check_env=True)
        self.assertEqual(2, config["a"])

    def test_load_from_dict_override(self):
        config = Config({"a": 1})
        config.load_from_dict({"a": 2})
        self.assertEqual(2, config["a"])

    def test_load_from_dict_nested_override(self):
        config = Config({"a": {"b": 1, "c": 2}})
        config.load_from_dict({"a": {"b": 3}})
        expected = Config({"a": {"b": 3, "c": 2}})
        self.assertEqual(expected, config)

    def test_load_from_dict_single_invalid_key(self):
        config = Config({"a": 1})
        with self.assertRaises(ConfigContentError) as ctx:
            config.load_from_dict({"b": 2})
        self.assertEqual(1, len(ctx.exception.errors))
        self.assertEqual({"b": "not found"}, ctx.exception.errors)

    def test_load_from_dict_multiple_invalid_keys(self):
        config = Config({"a": 1})
        with self.assertRaises(ConfigContentError) as ctx:
            config.load_from_dict({"b": 2, "c": {"d": 1}})
        self.assertEqual(2, len(ctx.exception.errors))
        self.assertEqual({"b": "not found", "c": "not found"}, ctx.exception.errors)

    def test_load_from_dict_invalid_value_type(self):
        old_value = 1
        new_value = "1"
        config = Config({"a": old_value})
        with self.assertRaises(ConfigContentError) as ctx:
            config.load_from_dict({"a": new_value})
        self.assertEqual(1, len(ctx.exception.errors))
        self.assertEqual(
            {
                "a": f"type is '{type(new_value).__name__}' should be '{type(old_value).__name__}'",
            },
            ctx.exception.errors,
        )

    def test_load_from_file_is_directory(self):
        config = Config(None)
        with self.assertRaises(ConfigError):
            config.load_from_file("/tmp")

    def test_load_from_file_missing(self):
        config = Config(None)
        with self.assertRaises(ConfigError):
            config.load_from_file("/foo/bar")
