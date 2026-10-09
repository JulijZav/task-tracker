# Postmortem: Database Outage

**Date**: 2026-10-06
**Duration**: ~10 min
**Severity**: High

## What happened

I stopped the PostgreSQL container to simulate a production outage.
The API immediately started returning 500 errors on all /tasks/ endpoints.
The /health endpoint still worked since it doesn't touch the database.

## How I noticed

Grafana picked it up, the SLO panel dropped from 100% to about 4%.
After the 5-minute pending period, I got a Discord alert saying the
SLO was breached. This is exactly what the alerting setup is for.

## What I did

Restarted the database with `docker compose start db`. The app
reconnected automatically (SQLAlchemy recycles connections) and
requests started succeeding again. Got a "resolved" notification
on Discord shortly after.

## What I learned

- The middleware originally didn't record 500 errors in Prometheus
  because the exception broke the flow before metrics were written.
  Fixed it with try/except/finally.
- The first SLO query measured latency, not success rate. A failing
  request is fast (instant error), so the SLO stayed green during
  the outage.
- There's no automatic restart for the database container. If it
  dies, it stays dead until someone notices. Adding a healthcheck
  and restart policy would help.

## TODO

- [ ] Add healthcheck + restart policy to db in docker-compose
- [ ] Return proper error messages instead of raw 500s
- [ ] Check database connectivity in /health endpoint