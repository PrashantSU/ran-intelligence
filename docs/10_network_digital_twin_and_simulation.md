# Network Digital Twin and Simulation

## 1. Purpose

The Network Digital Twin and Simulation component will provide a controlled environment for studying how changes in network conditions affect RAN performance.

It will allow us to generate network scenarios, change selected parameters and observe the resulting KPI behaviour.

This is useful for two reasons:

- We can test how the platform behaves under different network conditions.
- We can generate labelled scenarios for anomaly detection, forecasting and incident investigation.

For example, we could simulate a cell experiencing increasing traffic demand and observe how PRB utilisation and user throughput change.

We could then introduce interference and compare its effects on SINR, BLER and throughput.

The simulation will be designed for experimentation and educational purposes. It will not be presented as a complete or standards-compliant 5G NR network simulator.

## 2. Scope

The initial simulation environment will focus on selected RAN behaviours.

It should support:

- Multiple base stations and cells.
- Multiple user equipments (UEs).
- Traffic demand and resource utilisation.
- Radio channel conditions.
- Interference between cells.
- User scheduling.
- Basic beamforming experiments.
- Backhaul delay scenarios.
- KPI generation and performance comparison.

The design should allow new scenarios and models to be added without changing the rest of the platform.

## 3. Simulation Architecture

The simulation will be implemented as a separate Python module.

It will generate network configurations, execute scenarios and produce structured measurement outputs.

```text
Network Configuration
        |
        v
Scenario Definition
        |
        v
Network Topology
        |
        v
Channel and Radio Conditions
        |
        v
Traffic Generation
        |
        v
Resource Allocation
        |
        v
KPI Calculation
        |
        v
Simulation Results
        |
        v
Analytics and Visualisation
```

The generated results should follow the same general measurement schema used by the data ingestion and KPI analytics components.

This will make it possible to analyse simulated and public measurements using common platform interfaces, while retaining information about their different origins.

## 4. Network Configuration

A simulation should begin with a configurable network setup.

The initial configuration may include:

| Parameter | Description |
|---|---|
| num_base_stations | Number of simulated base stations |
| users_per_cell | Number of UEs associated with each cell |
| num_antennas | Number of antennas per base station |
| carrier_frequency | Operating carrier frequency |
| bandwidth | Available channel bandwidth |
| transmit_power | Base station transmit power |
| simulation_duration | Total simulation time |
| time_step | Duration of one simulation step |
| noise_level | Receiver noise assumptions |
| traffic_profile | Traffic demand assigned to users |

These parameters should be configurable through a file rather than hardcoded throughout the simulation.

We should also record the configuration used for every experiment so that results can be reproduced.

## 5. Network Topology

The topology module will define the relationship between base stations, cells and users.

Each base station should have:

- A unique identifier.
- A position or simplified location.
- An antenna configuration.
- One or more associated cells.
- A configured transmit power.

Each UE should have:

- A unique identifier.
- A serving cell.
- A position or simplified mobility state.
- A traffic demand profile.
- A set of radio measurements.

The first implementation can use a simple geometric layout.

For example, three base stations can be placed at different coordinates, with users distributed around them.

This is sufficient for initial experiments involving cell association, coverage and interference.

## 6. Radio Channel and Propagation Model

The radio channel module will estimate the signal conditions between a base station and a UE.

The first version should use a simplified propagation model.

Possible components include:

- Distance-based path loss.
- Shadowing.
- Small-scale fading.
- Receiver noise.
- Inter-cell interference.

The received signal strength can be estimated using a simplified link-budget calculation.

A general form is:

\[
P_r = P_t + G_t + G_r - PL - L
\]

where:

- \(P_r\) is received power in dBm.
- \(P_t\) is transmit power in dBm.
- \(G_t\) is transmitter antenna gain.
- \(G_r\) is receiver antenna gain.
- \(PL\) is path loss in dB.
- \(L\) represents additional losses.

The exact propagation model and its assumptions should be documented.

We should not describe the results as field measurements or claim that a simplified propagation model captures every real-world radio effect.

## 7. Traffic Generation

The traffic module will generate different levels of user demand.

Initially, it should support:

- Constant traffic.
- Periodic traffic.
- Random traffic variation.
- Sudden traffic increases.
- Bursty traffic.

These profiles will help us study network behaviour under different load conditions.

For example, a sudden increase in demand across several users may increase cell load and PRB utilisation.

Traffic generation should be reproducible using configurable random seeds.

## 8. Resource Allocation and Scheduling

The scheduling module will determine how available radio resources are assigned to users.

The initial implementation should include a few simple scheduling strategies.

### 8.1 Round Robin

Users receive resources in a rotating order.

This provides a straightforward baseline for comparison.

### 8.2 Proportional Fair Scheduling

The scheduler balances instantaneous channel quality against historical user throughput.

A simplified scheduling metric is:

\[
M_i(t) = \frac{R_i(t)}{\bar{R}_i(t)}
\]

where:

- \(R_i(t)\) is the estimated achievable rate for user \(i\).
- \(\bar{R}_i(t)\) is the user's historical average throughput.

### 8.3 Best Channel Quality

Resources are assigned preferentially to users with better estimated channel conditions.

This provides a useful comparison against fairness-oriented scheduling.

The simulation should compare throughput, resource utilisation and fairness across these scheduling strategies.

The initial scheduler will be an abstraction. It will not implement every detail of the commercial 5G NR MAC scheduler.

## 9. Interference Scenarios

Interference experiments will help us study the relationship between radio conditions and network performance.

The simulation should support scenarios such as:

- Increased interference from neighbouring cells.
- Changes in transmit power.
- Increased cell overlap.
- Changes in user distribution.
- Interference affecting only selected users.

The resulting measurements should include relevant KPIs such as SINR, BLER and throughput.

A scenario should specify exactly what changed and when it was introduced.

This makes it possible to compare normal and degraded network behaviour.

## 10. Beamforming and Coordinated Beamforming Lab

This is an important part of the project because it connects the platform with the type of wireless research I have previously worked on.

The simulation should eventually include a dedicated 5G NR research environment.

Possible experiments include:

- Simple beam steering.
- Multi-user beamforming.
- Interference-aware beamforming.
- Coordinated beamforming between base stations.
- Scheduling under limited or delayed information.
- Comparison of different precoding strategies.

The initial implementation should start with simplified channel and beamforming models.

More advanced experiments can be added later using NumPy and PyTorch.

For example, we can compare:

- No coordination.
- Independent beamforming.
- Coordinated beamforming.
- Coordination using delayed channel information.

The results may include:

- Sum rate.
- Per-user throughput.
- 5th-percentile user throughput.
- Inter-cell interference.
- Scheduling performance.

Any comparison should use the same underlying channel scenarios and clearly documented assumptions.

The goal is to build a reproducible research environment, not to reproduce proprietary Huawei software or data.

## 11. Backhaul Delay Experiments

The simulation should support delayed information exchange between base stations.

This will allow us to study how outdated channel or scheduling information affects coordinated network decisions.

For example, the simulation could compare:

- No backhaul delay.
- One simulation-step delay.
- Several simulation-step delays.
- Prediction-assisted coordination.

The results can help illustrate the relationship between information freshness and network performance.

We can later use this environment to test prediction models and compare their performance against simple baselines.

## 12. KPI Generation

Every simulation run should generate structured outputs that can be analysed by the rest of the platform.

Possible measurements include:

| KPI | Description |
|---|---|
| RSRP | Reference signal received power |
| RSRQ | Reference signal received quality |
| SINR | Signal-to-interference-plus-noise ratio |
| CQI | Channel quality indicator |
| MCS | Modulation and coding scheme |
| BLER | Block error rate |
| Throughput | Data rate achieved by a user or cell |
| PRB utilisation | Proportion of available physical resource blocks in use |
| Cell load | Estimated demand or resource usage |
| Interference power | Estimated interference level |

Not all KPIs need to be calculated in the first version.

Each KPI should have a documented definition, unit and calculation method.

Simulated values should be clearly identified as simulated.

## 13. What-if Analysis

The platform should provide a way to modify simulation parameters and compare outcomes.

For example:

**Scenario A:** Normal network conditions.

**Scenario B:** Increased traffic demand.

**Scenario C:** Increased inter-cell interference.

**Scenario D:** Increased traffic demand combined with interference.

The platform should display how the selected KPIs change between scenarios.

A comparison might include:

- Average user throughput.
- 5th-percentile throughput.
- Average SINR.
- BLER.
- PRB utilisation.
- Cell load.

The comparison should use consistent simulation settings wherever possible.

This helps isolate the effect of individual changes.

The results should also include a description of the assumptions behind each scenario.

## 14. Integration with Other Platform Components

The simulation environment should be independent but connected to the main platform.

Its outputs should be usable by:

**Data ingestion**

Simulation results can be exported in the platform's supported data formats.

**KPI analytics**

Generated measurements can be analysed using the same KPI calculations.

**Anomaly detection**

We can introduce known abnormal conditions and test whether detection methods identify them.

**Forecasting**

Simulated time series can be used to test forecasting models under controlled conditions.

**Incident investigation**

The platform can investigate simulated incidents where the underlying scenario is known.

**Evaluation**

Known scenario labels can help measure the performance of diagnostic and anomaly detection methods.

The source of every dataset must remain identifiable. Public, synthetic and simulated measurements should never be mixed without recording their provenance.

## 15. Proposed Python Module Structure

```text
src/
└── ran_intelligence/
    └── simulation/
        ├── __init__.py
        ├── config.py
        ├── topology.py
        ├── channel.py
        ├── traffic.py
        ├── interference.py
        ├── scheduler.py
        ├── beamforming.py
        ├── backhaul.py
        ├── kpi_generator.py
        ├── scenarios.py
        ├── runner.py
        └── results.py
```

Responsibilities:

- `config.py`: Simulation configuration and parameter validation.
- `topology.py`: Base stations, cells and UE placement.
- `channel.py`: Radio channel and propagation calculations.
- `traffic.py`: Traffic demand generation.
- `interference.py`: Interference modelling.
- `scheduler.py`: Resource allocation strategies.
- `beamforming.py`: Beamforming experiments.
- `backhaul.py`: Delayed information exchange.
- `kpi_generator.py`: KPI calculations.
- `scenarios.py`: Reusable scenario definitions.
- `runner.py`: Simulation execution.
- `results.py`: Result storage and export.

## 16. Testing and Evaluation

The simulation should be tested at both the component and scenario levels.

### Component tests

Examples:

- Verify that path loss increases with distance under the selected model.
- Check that generated traffic follows the configured profile.
- Verify that resource allocation respects available capacity.
- Check that KPI calculations use the expected units.
- Confirm that fixed random seeds produce reproducible results.

### Scenario tests

Examples:

- Increasing traffic demand should increase resource demand under the same scheduling assumptions.
- Introducing interference should affect the relevant radio measurements.
- Changing scheduling policies should produce measurable differences where the scenario allows them.
- Adding backhaul delay should affect delayed coordination experiments when the model depends on that information.

These are expected behaviours under specified assumptions, not universal guarantees for every simulation setup.

### Performance evaluation

We should also record:

- Simulation execution time.
- Number of cells and users.
- Number of simulation steps.
- Memory usage.
- Results across repeated random seeds.

## 17. Implementation Order

The simulation will be built in stages.

**Stage 1 — Basic network topology**

Create base stations, cells and UE placement.

**Stage 2 — Radio conditions**

Implement a simple propagation model and calculate received signal conditions.

**Stage 3 — Traffic generation**

Generate constant, periodic and variable traffic profiles.

**Stage 4 — Basic scheduling**

Implement Round Robin, Proportional Fair and Best Channel Quality scheduling.

**Stage 5 — KPI generation**

Calculate and export the initial set of network KPIs.

**Stage 6 — Interference scenarios**

Introduce controlled interference and compare the resulting measurements.

**Stage 7 — Beamforming experiments**

Add simplified beamforming and coordinated beamforming models.

**Stage 8 — Backhaul delay**

Introduce delayed information exchange and prediction-assisted experiments.

**Stage 9 — Platform integration**

Connect simulation outputs to analytics, anomaly detection and incident investigation.

**Stage 10 — What-if interface**

Allow users to configure and compare scenarios through the Streamlit application.

## 18. Expected Outcome

The final component should provide a reproducible environment for studying selected RAN behaviours.

Engineers should be able to create network scenarios, change parameters, compare scheduling and coordination strategies, and inspect the resulting KPIs.

It will also provide controlled data for testing the wider RAN Intelligence Platform.

The main value is the combination of practical network analytics with a research-oriented environment for studying 5G radio behaviour.
