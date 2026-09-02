---
name: Historic Data Recovery
overview: Restore the historic weather readings onto the live tec-weather instance without losing the readings collected since 2026-08-13. Six reading tables (outdoor_sensor, indoor_sensor, aqi_sensor, light_sensor, pi_metrics, sdr_metrics) hold only post-migration data; their historic contents come from the verified dump at /mnt/clones/data/weather-migration/db/weather.sql.gz. The historic load builds replacement tables alongside the live ones with collection still running, the station is paused only to capture the new data as a static snapshot, the new rows are re-applied without their ids so auto-increment places them above the historic maximum, and each table is swapped in with an atomic RENAME that preserves the displaced table.
todos:
  - id: preflight
    content: "Phase 0: verify the dump checksum, record a before-state inventory of every table, confirm free space, and take a --single-transaction safety dump of the current schema to the share with a sha256 sidecar"
    status: pending
  - id: load-historic
    content: "Phase 1: load the migration dump into a weather_hist staging schema, filtered by awk to the six in-scope tables so the dropped _old tables are not recreated, then capture the baseline (counts, min/max, per-partition counts) from it"
    status: pending
  - id: build-rebuild
    content: "Phase 1: create weather.<t>_rebuild LIKE the live tables, load the historic rows from weather_hist with ids intact, and verify each against the baseline on counts, ranges and per-partition counts"
    status: pending
  - id: pause
    content: "Phase 2: stop and disable weatherwatch and weatherdash, then confirm the freeze took effect via inactive units, an empty PROCESSLIST for the weather user, and static counts sampled 90s apart"
    status: pending
  - id: capture-new
    content: "Phase 3: stage the new rows into a weather_new schema, dump it to the share as the off-system copy, and verify min timestamps postdate the historic maximum and counts match the frozen figures"
    status: pending
  - id: apply-new
    content: "Phase 3: insert the staged rows into the _rebuild tables with the id column omitted, ordered by time, then verify totals, ranges, contiguous ids, id/time ordering agreement and per-partition counts"
    status: pending
  - id: swap
    content: "Phase 4: RENAME each table to <t>_pre_recovery and each _rebuild into place, confirm aqi_clean and the verification queries, then re-enable and start the services"
    status: pending
  - id: cleanup
    content: "Phase 5: after a few days of normal operation, drop weather_hist, weather_new and the _pre_recovery tables"
    status: pending
isProject: false
---

# Historic data recovery

Restores the historic weather readings onto the live `tec-weather` instance
without losing the readings collected since the station came back up.

**Status: Phases 0–4 complete. Live tables swapped and collection resumed 2026-09-02T00:04:21Z. New rows landing with ids above the historic maximum. Phase 5 cleanup deferred.**

## Situation

Six reading tables on `tec-weather` hold only readings from 2026-08-13 onward.
Their historic contents are absent. Every other table is intact.

| table | rows now | new-data range | historic rows available |
|---|---:|---|---:|
| `indoor_sensor` | 11,381 | 2026-08-13 → now | 334,660 |
| `sdr_metrics` | ~5,747 | 2026-08-13 → now | 173,530 |
| `aqi_sensor` | 5,745 | 2026-08-13 → now | 169,451 |
| `outdoor_sensor` | 5,720 | 2026-08-13 → now | 166,880 |
| `light_sensor` | 5,720 | 2026-08-13 → now | 33,022 |
| `pi_metrics` | 2,872 | 2026-08-13 → now | 86,906 |

The "rows now" figures are as of 2026-09-01 23:05 and keep growing until the
pause in Phase 2. The authoritative figures are the ones recorded at the freeze.

**Not in scope. These tables are untouched by this plan:** `solar_reading`,
`solar_temperature_reading` and `sonic_reading` were never emptied and hold
continuous data from April onward. A wholesale reload of the dump would clobber
them and lose their new rows, so the recovery is scoped to the six tables above.
`apscheduler_jobs` and `pyway` are also left alone.

## Source of the historic data

`/mnt/clones/data/weather-migration/db/weather.sql.gz` — 44 MB gzipped,
419 MB raw, sha256 verified against its sidecar.

The six tables in this dump are already in their final form: `read_time` as UTC
`datetime(6)`, correct `RANGE COLUMNS` partitioning, original ids `1..N`. They
load directly. Nothing needs deriving, converting or re-deriving from the `_old`
backup tables, and this plan does not read the `_old` tables at all.

**The dump still contains the `_old` tables, which have since been dropped from
the live instance to reclaim space.** They are roughly 195 MB together, with
`indoor_sensor_old` alone at 106 MB. A wholesale load of this dump would put
them straight back, so Phase 1 filters the stream down to the six tables it
actually needs. The same filter also excludes `solar_reading`,
`solar_temperature_reading`, `sonic_reading`, `apscheduler_jobs` and `pyway`,
none of which are in scope. They remain available in the dump if ever wanted.

## Why the ids work out

Historic data ends **2026-06-29 06:10**. New data starts **2026-08-13 00:24**.
There is no timestamp overlap, so the only conflict is that the new rows
currently occupy ids `1..5,745`, which is where the historic rows belong.

The fix is to re-apply the new rows **without their ids** so auto-increment
assigns them fresh ids above the historic maximum. That resolves the collision
and keeps id order matching time order, which the `aqi_clean` procedure relies
on when it walks neighbours with `WHERE id < v_id ORDER BY id DESC`.

## Shape of the run

The historic load builds replacement tables alongside the live ones and never
reads or writes the live tables, so collection keeps running throughout it —
that is the long step, and there is no reason to be down for it. The station is
only paused once the new data has to be captured as a static snapshot, because
anything collected between the snapshot and the swap would otherwise be lost.

| phase | collection | live tables |
|---|---|---|
| 0 preflight | running | untouched |
| 1 reconstitute historic | running | untouched |
| 2 pause | **stopped** | untouched |
| 3 capture and apply new data | **stopped** | untouched |
| 4 swap and resume | stopped → running | swapped |

Downtime is Phase 3 plus the Phase 4 swap, not the whole run.

## Cutover shape

The recovery happens **table by table inside `weather`**, not by building a
replacement schema and renaming it into place. Two reasons.

MariaDB has no `RENAME DATABASE`. It existed briefly in MySQL 5.1 and was
removed as unsafe, so a schema-level swap would have to be expressed as
`RENAME TABLE` moving tables between schemas anyway.

More importantly, `weather` is not an empty shell around the six damaged tables.
It also holds `solar_reading`, `solar_temperature_reading` and `sonic_reading`,
two of which are actively collecting right now, plus `apscheduler_jobs` and
`pyway`. A whole-schema swap would mean rebuilding five healthy tables, with
current data the historic dump does not contain, in order to fix six broken
ones. The per-table swap never reads or writes any of them.

The staging schemas `weather_hist` and `weather_new` are working space only.
Nothing is ever renamed into `weather` from them; the rows travel by
`INSERT ... SELECT` into `_rebuild` tables that already live in `weather`, which
also keeps the partitioned tables from having to move across schemas — a
manoeuvre with a history of edge cases that this plan avoids entirely.

## Safety model

Nothing in `weather` is modified until the Phase 4 rename. Phases 0–3 only
create new schemas and new tables alongside the live ones, so the recovery can
be abandoned at any point before the swap with a single `DROP`. The Phase 4 swap
is a `RENAME TABLE`, which is atomic, and it preserves the displaced table as
`<table>_pre_recovery` rather than dropping it.

The new data ends up protected three ways: the Phase 0 safety dump, the
`weather_new` staging schema and its dump on the share, and the `_pre_recovery`
tables left behind by the swap.

## Column lists

Used in Phase 3, where the id column is deliberately omitted.

| table | time column | columns excluding `id` |
|---|---|---|
| `outdoor_sensor` | `read_time` | `read_time, battery_ok, sensor_id, temperature_f, humidity, pressure, rain_cum_mm, rain_delta_mm, wind_avg_m_s, wind_max_m_s, wind_dir_deg, light_lux, uv, raw` |
| `indoor_sensor` | `read_time` | `read_time, battery_ok, sensor_id, channel, temperature_f, humidity, raw` |
| `aqi_sensor` | `read_time` | `read_time, pm_1_0_conctrt_std, pm_2_5_conctrt_std, pm_10_conctrt_std, pm_1_0_conctrt_atmosph, pm_2_5_conctrt_atmosph, pm_10_conctrt_atmosph` |
| `light_sensor` | `read_time` | `read_time, lux, visible, infrared, full_spectrum, ir_visible_luminosity, ir_only` |
| `pi_metrics` | `read_time` | `read_time, mem_available, mem_used, mem_percent, disk_available, disk_used, disk_percent, cpu_temp_c` |
| `sdr_metrics` | `start_time` | `start_time, end_time, duration_sec, sensor_cnt` |

`sdr_metrics` is the odd one out: it has no `read_time`, and orders by
`start_time`.

## Phase 0 — preflight and safety net

Collection keeps running. Nothing here changes the database.

Verify the dump still reads back clean:

```bash
cd /mnt/clones/data/weather-migration/db && sha256sum -c weather.sql.gz.sha256
```

Record a before-state inventory of every table: `COUNT(*)`, min and max of the
time column, `MAX(id)` and `AUTO_INCREMENT`. Confirm free space on `/` is
comfortably above 2 GB; with the filter in place the staging schema and the
rebuild tables come to roughly 600 MB between them.

Take a full dump of the current schema, new data and all, to the share with a
checksum. `--single-transaction` makes it consistent despite collection running:

```bash
sudo mariadb-dump --single-transaction --quick --hex-blob \
  --routines --events --triggers --default-character-set=utf8mb4 \
  --databases weather \
  | gzip -6 > /mnt/clones/data/weather-migration/db/weather_pre_recovery_$(date +%Y%m%d_%H%M).sql.gz
```

Write its `sha256` sidecar and verify it reads back.

**Gate:** the safety dump verifies, and the six tables still show a minimum
timestamp after 2026-08-01. If any of them shows historic timestamps, stop —
the situation has changed since this plan was written.

## Phase 1 — reconstitute the historic data

Collection keeps running. The live tables are neither read nor written here.

Load the migration dump into a staging schema, filtered to the six tables so the
`_old` tables and the out-of-scope tables never land on disk.

`mariadb-dump` brackets each table with `-- Table structure for table \`X\`` and
`-- Dumping data for table \`X\`` marker comments, so an `awk` state machine keyed
on those can pass through the file header and then emit only the wanted blocks.
Matching is on the exact table name, so `aqi_sensor_old` does not match
`aqi_sensor`. The two `sed` expressions are anchored at line start, and every
data line in the dump begins with `(`, so no row data can match them:

```bash
gunzip -c /mnt/clones/data/weather-migration/db/weather.sql.gz \
  | awk '
      BEGIN {
        split("outdoor_sensor indoor_sensor aqi_sensor light_sensor pi_metrics sdr_metrics", w, " ")
        for (i in w) want[w[i]] = 1
        header = 1
      }
      /^-- (Table structure|Dumping data) for table `/ {
        header = 0
        match($0, /`[^`]+`/)
        on = (substr($0, RSTART + 1, RLENGTH - 2) in want)
      }
      header || on
    ' \
  | sed -e 's/^CREATE DATABASE .*`weather`/CREATE DATABASE IF NOT EXISTS `weather_hist`/' \
        -e 's/^USE `weather`;/USE `weather_hist`;/' \
  | sudo mariadb
```

The filter drops the dump's trailing session-restore statements along with the
unwanted tables. That is harmless, since they only restore variables in a
session that is ending anyway, but it does mean the `aqi_clean` routine is not
carried into staging either. It does not need to be — the procedure already
exists in `weather` and is verified there in Phase 4.

**Gate:** `weather_hist` contains exactly six tables. If any `_old` table
appears, the filter did not work and the staging schema should be dropped and
the load re-run rather than continuing.

Verify `weather_hist` holds the expected historic counts from the table at the
top of this plan, then capture the full baseline from it: per-table `COUNT(*)`,
min and max of the time column, and per-partition row counts from
`information_schema.PARTITIONS`. This baseline, measured rather than assumed, is
what Phase 3 verifies against.

Build the replacement tables. `CREATE TABLE ... LIKE` inherits the partitioning
and indexes:

```sql
CREATE TABLE weather.<t>_rebuild LIKE weather.<t>;
INSERT INTO weather.<t>_rebuild SELECT * FROM weather_hist.<t>;
```

The `LIKE` takes a brief metadata lock on the live table and the `INSERT`
reads only from staging, so neither disturbs collection.

**Gate:** each `_rebuild` table matches the `weather_hist` baseline exactly on
row count, min and max timestamp, and per-partition counts. The live tables are
still untouched, and this is the last point at which the recovery can be
abandoned by dropping the staging schema and rebuild tables with no downtime
having been taken at all.

## Phase 2 — pause the weather system

Now, and not before. From here the database must stop moving so that the new
data can be captured as a complete, static snapshot.

`weatherwatch` is the only writer. It runs the collection scheduler in-process,
so stopping the unit also stops the `sensor`, `aqi`, `pi_metrics`, `camera`,
`weather_underground`, `db_backup`, `file_backup` and `timelapse` jobs.
`weatherdash` only reads, but it is stopped too so that no connection is holding
the tables open during the Phase 4 rename.

```bash
sudo systemctl stop weatherwatch weatherdash
sudo systemctl disable weatherwatch weatherdash
date -u +%Y-%m-%dT%H:%M:%SZ    # record the freeze moment
```

Both units are `Restart=always` and `WantedBy=multi-user.target`. `stop` is not
defeated by `Restart=always`, since that only acts on unexpected process exit,
but both units are enabled — so without the `disable`, a reboot part way through
would silently restart collection and write rows into a half-built table. They
are re-enabled in Phase 4.

MariaDB itself stays running throughout; the recovery needs it.

**Gate.** Confirm the writes have actually stopped rather than assuming the stop
took effect:

- `systemctl is-active weatherwatch weatherdash` reports inactive for both
- no app connections remain in `SHOW PROCESSLIST` for the `weather` user
- sample `COUNT(*)` and `MAX(id)` on the six tables twice, about ninety seconds
  apart, and confirm both are identical — collection runs on a one-minute cycle,
  so a genuine freeze shows no movement across that window

Record those final counts. They are the authoritative new-data figures that
Phase 3 verifies against, replacing the approximate ones at the top of this plan.

## Phase 3 — capture the new data and apply it to the historic schema

The six tables contain *only* new data, so this takes all of their rows rather
than applying a date filter. The Phase 0 gate and the check below are what make
that safe.

Stage the new rows into their own schema. Keeping them inside SQL rather than
exporting to text avoids any escaping risk with the JSON `raw` columns on
`outdoor_sensor` and `indoor_sensor`:

```sql
CREATE DATABASE weather_new;
-- per table:
CREATE TABLE weather_new.<t> LIKE weather.<t>;
INSERT INTO weather_new.<t> SELECT * FROM weather.<t>;
```

Then dump `weather_new` to the share, gzipped and checksummed, as the durable
off-system copy of the new data.

**Gate:** for each of the six tables, `MIN(<time column>)` in `weather_new` is
later than the historic maximum of 2026-06-29 06:10, and the row count in
`weather_new` equals the frozen count recorded in Phase 2. Both must hold for
all six before continuing.

Append the staged rows to the rebuilt tables, omitting `id` so auto-increment
assigns them above the historic maximum. Ordering by the time column keeps ids
monotonic with time:

```sql
INSERT INTO weather.<t>_rebuild (<columns excluding id>)
SELECT <columns excluding id> FROM weather_new.<t>
ORDER BY <time column>;
```

**Gate**, per table:

- row count equals historic plus new, from the two baselines already captured
- minimum timestamp equals the historic minimum
- maximum timestamp equals the new-data maximum
- ids run `1..COUNT(*)` with no gaps, and `MAX(id)` equals the row count
- ordering by `id` and ordering by the time column agree, so `aqi_clean` stays correct
- per-partition counts equal the historic partition counts plus the new rows' partitions

## Phase 4 — swap and resume

The cutover is a single `RENAME TABLE` naming all twelve renames at once. A
`RENAME TABLE` statement is atomic across everything it lists, so all six tables
flip together or none of them do — there is no window in which the schema is
half recovered. Each displaced table is preserved rather than dropped:

```sql
RENAME TABLE
  weather.outdoor_sensor         TO weather.outdoor_sensor_pre_recovery,
  weather.outdoor_sensor_rebuild TO weather.outdoor_sensor,
  weather.indoor_sensor          TO weather.indoor_sensor_pre_recovery,
  weather.indoor_sensor_rebuild  TO weather.indoor_sensor,
  weather.aqi_sensor             TO weather.aqi_sensor_pre_recovery,
  weather.aqi_sensor_rebuild     TO weather.aqi_sensor,
  weather.light_sensor           TO weather.light_sensor_pre_recovery,
  weather.light_sensor_rebuild   TO weather.light_sensor,
  weather.pi_metrics             TO weather.pi_metrics_pre_recovery,
  weather.pi_metrics_rebuild     TO weather.pi_metrics,
  weather.sdr_metrics            TO weather.sdr_metrics_pre_recovery,
  weather.sdr_metrics_rebuild    TO weather.sdr_metrics;
```

Confirm `aqi_clean` still exists and re-run the verification queries against the
live table names. Only once those pass, lift the Phase 2 pause:

```bash
sudo systemctl enable weatherwatch weatherdash
sudo systemctl start weatherwatch weatherdash
```

The scheduler may fire jobs it missed during the pause as it comes back up.
That is harmless here — it collects a reading, which is what it would have done
anyway — but it means the first rows can arrive in a burst rather than on the
usual one-minute cycle.

**Gate:** within one collection cycle, new rows land in all six tables with ids
continuing above the historic maximum, and `/var/log/WeatherWatch_err.log` is
clean. Spot-check the dashboard for a continuous history with a single expected
gap between 2026-06-29 and 2026-08-13, which is the period the station was down.

## Phase 5 — cleanup, only once confident

Deferred deliberately. Leave the recovery artefacts in place for a few days of
normal operation first.

```sql
DROP DATABASE weather_hist;
DROP DATABASE weather_new;
DROP TABLE weather.<t>_pre_recovery;   -- per table
```

The `_old` backup tables have already been dropped from the live instance and
are not recreated by this plan. Their contents remain in the migration dump on
the share if they are ever needed again.

## Rollback

Before Phase 4, drop `weather_hist`, `weather_new` and the `_rebuild` tables.
Nothing in `weather` will have changed. If this happens before Phase 2, no
downtime is taken at all.

After Phase 4, reverse the rename to put the `_pre_recovery` table back. If the
schema itself is in doubt, restore the Phase 0 safety dump, then re-apply
anything collected between that dump and the freeze from `weather_new`.

## Resource notes

`/` is 117 GB with 88 GB free, so disk is not a real constraint here. The
datadir was 467 MB before the `_old` tables were dropped and should now be
around 270 MB.

The filtered historic set is roughly 295 MB, dominated by `indoor_sensor` at
about 128 MB and `outdoor_sensor` at about 110 MB, the two tables carrying JSON
`raw` columns. It is held twice during the run, once in `weather_hist` and once
in the `_rebuild` tables, so peak additional usage is around 600 MB, falling
back to about 295 MB once Phase 5 drops the staging schemas.

The earlier restore of this dump took roughly seven minutes unfiltered and
should be quicker now, and it falls entirely inside the running-collection
window. Expect only a few minutes of actual downtime across Phases 3 and 4.
