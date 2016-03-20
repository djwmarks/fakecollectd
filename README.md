# Fake Collectd

A minimal, fake version of collectd written in Python. Useful for developing
and testing collectd Python modules. Does not include a Collectd configuration
file parser so you need to rewrite your module configuration into a JSON file.

Lightly-tested. Works okay for the basic read plugins I have used it with so
far. More advanced use cases probably require additional work.

```shell
$ fakecollectd --plugin-config examples/random_int.json examples/random_int.py
<collectd.Values random_int/absolute-value=36>
<collectd.Values random_int/absolute-value=47>
<collectd.Values random_int/absolute-value=92>
<collectd.Values random_int/absolute-value=65>
...
```
