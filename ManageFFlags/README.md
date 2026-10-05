This guide contains a collection of Python code snippets that you can run in a real-eval-print loop.

Their purpose is to allow easier triage of problematic FFlag options on Rōblox revival clients.

### To Load All Default FFlags

```py
import requests
ALL_DEFAULTS = {k:v[1] for k,v in requests.get('https://github.com/Windows81/Roblox-x64dbg-FFlag-Extractor/raw/651332612610c3484a1785f130c8d057efe02fae/test/v463-player.json').json().items()}
```

### To Load a JSON File with FFlags

This function is smart enough to recognise if the FFlags are nested within a table with an `applicationSettings` key. This is meant for payloads that were generated from a `/v1/settings/application` endpoint.

```py
def load_json(path: str) -> dict:
	import json
	r = json.load(open(path))
	return r.get('applicationSettings', r)

j1 = load_json('./v463-flags-0-66-5.json')  # for example
```

### To Filter Invalid or Already-Default FFlag Values

Filter the following out:

- **invalid**: i.e. that the FFlag value is not included in `ALL_DEFAULTS`
- **"already-default"**: i.e. that the FFlag value in your table is identical to that of `ALL_DEFAULTS`
  - In this case, that FFlag _in your table_ becomes redundant and I recommend removing it.
- **FLog**: i.e., that only affect logging behaviour _and nothing else_

```py
def filter_in_place(t: dict):
	global ALL_DEFAULTS
	for k, v in list(t.items()):
		if 'FLog' in k or ALL_DEFAULTS.get(k, v) == v:
			del t[k]

filter_in_place(j1)  # for example
```

### To Create Interpolated Value Dict

Interpolation is carried out via an _alpha_ value.

- Lower _alpha_ gets you closer to first param.
- Higher _alpha_ gets you closer to second param.

```py
def interpolate_diff(t1: dict, t2: dict, alpha: float) -> dict:
	__s1 = set(t1.items())
	__s2 = set(t2.items())
	__d = list(__s2 - __s1) + list((k, ALL_DEFAULTS.get(k)) for (k, _) in __s1 - __s2)
	return t1 | dict(__d[:int(alpha*len(__d))])

j_50_percent = interpolate_diff(j1, j2, alpha=0.5)  # for example
```

### To Determine Changed Keys Between Alphas

Note that the result shows the changes that you'd make to go from `t1` to `t2`.

- **If `t1` is buggy and `t2` is fine**, you can use the change(s) returned by `get_interpolated_changes_between` _as-is_.

- **If `t1` is fine and `t2` is buggy**, you need to _reverse_ the change(s) returned by `get_interpolated_changes_between`.

```py
def get_interpolated_changes_between(t1: dict, t2: dict, alpha1: float, alpha2: float) -> dict:
	__s1 = set(t1.items())
	__s2 = set(t2.items())
	__d = list(__s2 - __s1) + list((k, ALL_DEFAULTS.get(k)) for (k, _) in __s1 - __s2)
	return dict(__d[int(alpha1*len(__d)):int(alpha2*len(__d))])

j_50_to_52_percent = get_interpolated_changes_between(j1, j2, alpha1=0.5, alpha2=0.52)  # for example
```

### To Copy Result as JSON

```py
def copy_json(t: dict):
	import pyclip
	import json
	pyclip.copy(json.dumps(t, indent=4))

copy_json(j_50_percent)  # for example
```

### To Copy Result as TOML 1.1 Dict

This option is specifically tailored for Rōblox Freedom Distribution 0.68.0 and later. Refer to info on config option [`server_core.roblox_setting_overrides`](https://github.com/Windows81/Roblox-Freedom-Distribution#server_coreroblox_setting_overrides).

```py
def copy_toml(t: dict):
	import pyclip
	import json
	pyclip.copy(
		'server_core.roblox_setting_overrides = {\n' +
		''.join(f'    %s = %s,\n' % (k, json.dumps(v)) for k, v in t.items()) +
		'}'
	)

copy_toml(j_50_percent)  # for example
```
