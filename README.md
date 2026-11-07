# Assignment 2 — Smart Energy Stream Processing Framework

A standalone Python implementation of an event-driven stream-processing framework for the AI-Powered Smart Energy Management System. It uses simulated in-memory IoT meter events and requires no third-party libraries.

## Run

Requires Python 3.10 or newer.

```bash
python demo.py
python -m unittest discover -s tests -v
```

## Where the four required OOP concepts are implemented

1. **Abstract Base Classes:** `StreamProcessor` extends `ABC`; its `process()` method uses `@abstractmethod`.
2. **Inheritance and polymorphism:** `ActiveMeterFilter`, `EnergyMetricsTransformer`, `EventCounter`, and `Pipeline` inherit from `StreamProcessor`. The pipeline invokes processors through the same `process()` API, while each subclass implements its own behavior.
3. **Operator overloading:** `StreamProcessor.__or__()` and `Pipeline.__or__()` overload `|`. Example: `ActiveMeterFilter(0.1) | EnergyMetricsTransformer()`.
4. **Iterators and generators:** `Pipeline.__iter__()` and `Pipeline.__next__()` implement the iterator protocol. `Pipeline.run()` is a generator using `yield` to emit processed events one at a time.

## Pipeline stages

- `ActiveMeterFilter` removes inactive meters and readings below `min_power_kw`.
- `EnergyMetricsTransformer` calculates load balance, carbon-equivalent estimate, and peak-tariff status.
- `Pipeline` connects processors and passes each event through them in sequence.

## Calculation assumptions

- Carbon equivalent = `energy_kwh * carbon_kg_per_kwh`; the default factor is illustrative and should be replaced with a factor specified by your course or data source.
- Load balance = `power_kw - baseline_load_kw`.
- Peak tariff is flagged when `power_kw >= peak_tariff_threshold_kw`.
- Events are processed sequentially from an iterable. This educational implementation does not connect to Kafka/MQTT and does not include persistence, retries, distributed processing, or asynchronous backpressure.

## Suggested presentation flow

1. Show `StreamProcessor` and explain its abstract `process()` contract.
2. Show the concrete processors and explain inheritance/polymorphism.
3. Demonstrate `filter | transformer` and explain the overloaded `|` operator.
4. Run `demo.py` to show inactive/sub-threshold events being discarded and valid events enriched.
5. Point to `run()`, `__iter__()`, and `__next__()` to explain generator and iterator behavior.

## Class Diagram

<img width="1576" height="754" alt="assignment2_uml" src="https://github.com/user-attachments/assets/1b8b44bf-1aac-4d97-ad9e-e6f113046421" />

