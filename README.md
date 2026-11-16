# freshcart-pipelines

Data Engineering assignment **From Git to Gold**: version control and CI, an ELT pipeline on Snowflake, an ML pipeline in Mage, and an event stream on RabbitMQ.

## How the four pieces fit together

```
code in Git ──push──> GitHub ──> CI (pytest) ──> green / red
                         │
      ┌──────────────────┼─────────────────────┐
      ▼                  ▼                      ▼
  elt/ (FreshCart)   iris_project/ (Mage)   stream/ (RabbitMQ)
  Extract -> Load    load -> validate ->    dispatcher -> topic exchange
  -> Transform       prepare -> train ->    -> driver queues (ACK / NACK)
  -> Check           save + evaluate
  bronze/silver/gold  tests gate each step
```

## Repository layout

| Path | What it contains |
|------|------------------|
| `elt/` | FreshCart ELT notebook (Snowflake: bronze, silver, quarantine, gold) |
| `iris_project/` | Mage project, pipeline `iris_classifier` with a test after each block |
| `stream/` | `dispatcher.py` and `driver.py` (RabbitMQ topic exchange `rapido-dispatch`) |
| `tests/` | pytest test for the `prepare_data` block |
| `.github/workflows/ci.yml` | GitHub Actions: checkout, Python 3.12, install, pytest on every push |

## Part A: Git and CI

CI runs `python -m pytest` on every push. The history shows a passing run, a deliberately failing run (`test_size=0.3` in `prepare_data.py`) and the fixing commit.

## Part B: FreshCart ELT (Snowflake)

Extract (sample API data to raw files), Load (`PUT` + `COPY INTO` bronze), Transform (SQL to silver, dim, ref, gold), Check (`quality_checks()`).
Run the notebook top to bottom; you are asked for your Snowflake account and username, and the password is requested with `getpass` (never saved).

## Part C: Mage ML pipeline

Blocks: `load_iris` -> `validate_data` -> `prepare_data` -> `train_model` -> `save_results` and `evaluate_model`.

```bash
pip install mage-ai scikit-learn
mage run iris_project iris_classifier --test
mage run iris_project iris_classifier --test --runtime-vars '{"max_depth": 1}'
```

With `max_depth = 1` the accuracy test fails (about 0.63, so `save_results` never runs and no CSV is written.

## Part D: RabbitMQ stream

```bash
python stream/driver.py Ravi "bangalore.koramangala.*"
python stream/driver.py Control "bangalore.#"
python stream/dispatcher.py             # one message every 2 s; every 10th is bad (no zone)
python stream/dispatcher.py --demo-d1   # publish the six routing keys from the D1 table
```

Set `AMQP_URL` for a hosted broker (never commit it). Messages without a `zone` field are rejected with `basic_nack(requeue=False)`; all others get `basic_ack`.

## Secrets

`.env`, `*.pkl`, `*.csv`, `mage.log` and `__pycache__/` are in `.gitignore`. No credentials are stored in this repository.
