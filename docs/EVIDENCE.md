# Evidence

Every claim below comes from a command that was actually run against this
exact checkout. Nothing here is inferred from the source alone.

## Commands

```sh
# from the project directory, with _tools and _tools/_vendor on PYTHONPATH
python -m pytest -q -p hosttmp_proj tests/
python -m compileall -q src
```

## Recorded results

| check | result |
| --- | --- |
| compileall | exit 0 |
| pytest | -- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html |
| pytest_exit_code | 0 |
| recorded_at | 2026-10-08 |
| routes_ok | 13 |
| routes_probed | 13 |

## HTTP surface

One real GET per rule in the assembled URL map, through Flask's test
client. `ok` includes 404 on a templated path: an empty database has
no such resource, and 404 is the honest answer for that.

| method | path | rule | status | bytes | note |
| --- | --- | --- | --- | --- | --- |
| GET | `/` | `/` | 200 | 5856 | ok |
| GET | `/api/equity` | `/api/equity` | 200 | 44 | ok |
| GET | `/api/health` | `/api/health` | 200 | 39 | ok |
| GET | `/api/signals` | `/api/signals` | 200 | 15 | ok |
| GET | `/api/signals/stream` | `/api/signals/stream` | 200 | 21 | ok |
| GET | `/api/stats` | `/api/stats` | 200 | 69 | ok |
| GET | `/healthz` | `/healthz` | 200 | 61 | ok |
| GET | `/ledger` | `/ledger` | 200 | 4818 | ok |
| GET | `/livez` | `/livez` | 200 | 19 | ok |
| GET | `/metrics` | `/metrics` | 200 | 256 | ok |
| GET | `/readyz` | `/readyz` | 200 | 31 | ok |
| GET | `/replay` | `/replay` | 200 | 6384 | ok |
| GET | `/version` | `/version` | 200 | 940 | ok |

## Operational endpoints

`/healthz` answered **200**:

```
{"service":"signal_monitor","status":"ok","version":"0.1.0"}
```

`/livez` answered **200**:

```
{"status":"alive"}
```

`/readyz` answered **200**:

```
{"checks":[],"status":"ready"}
```

`/metrics` answered **200**:

```
# TYPE http_requests_total counter
http_requests_total{method="GET",status="200"} 7
# TYPE http_request_duration_seconds_sum counter
http_request_duration_seconds_sum{method="GET"} 0.0922677
# TYPE process_uptime_seconds gauge
process_uptime_seconds 2.591
```

`/version` answered **200**:

```
{"config":{"app_name":"signal_monitor","data_dir":".\\var","database_configured":false,"debug":false,"env":"development","host":"0.0.0.0","legacy_env_present":[],"log_json":true,"log_level":"INFO","port":8000,"secret_key_configured":false},"paths":{"data_dir":"c4_signal_m
```

## Headers observed on /healthz

| header | value |
| --- | --- |
| X-Request-ID | 59baed60c2e045bc90d3b130a7d74c5f |
| X-Content-Type-Options | nosniff |
| X-Frame-Options | DENY |
| Referrer-Policy | no-referrer |
| Cross-Origin-Opener-Policy | same-origin |
| Permissions-Policy | geolocation=(), microphone=(), camera=() |
| Content-Type | application/json |

## What this file does not claim

- No browser screenshot: this host denies the Chromium sandbox the renderer
  needs, so the HTTP surface is evidenced with recorded status codes instead.
- No network access: the suite is hermetic and contacts no remote host.
- No container run: the Dockerfile is reviewed, not executed, because no
  container runtime is reachable from this host.
