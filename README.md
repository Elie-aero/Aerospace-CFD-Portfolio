<div align="center">

# Elie Moussa

**Mechanical & Thermal Engineering Student | Numerical Simulation | Aerospace**  
**Polytech Nantes — 4A, Diplôme d’ingénieur TEM**

[LinkedIn](https://www.linkedin.com/in/moussaelie/) · [Email](mailto:eliemoussacareer@outlook.com)

</div>

---

# ISA Atmosphere & TAS-to-CAS Conversion

A **MATLAB/Simulink aerospace simulation project** for atmospheric-state modelling and airspeed conversion across representative flight conditions.

| | |
|---|---|
| **Domain** | Flight mechanics / atmospheric modelling |
| **Tools** | MATLAB, Simulink |
| **Core work** | ISA model, TAS-to-CAS conversion, coordinate transformation |
| **Documentation** | Technical report + model verification cases |

## Project overview

The model combines an **International Standard Atmosphere (ISA)** subsystem with a **True Airspeed (TAS) to Calibrated Airspeed (CAS)** conversion workflow. Supporting Earth-to-body coordinate transformation logic is also included.

The objective was not only to build the model, but to structure it so that the main calculations could be inspected and checked independently.

## Technical scope

- Atmospheric properties as a function of altitude using ISA relationships
- TAS-to-CAS conversion workflow
- Modular Simulink subsystem architecture
- Earth-to-body coordinate transformation logic
- Verification at representative altitude and airspeed conditions
- Technical documentation of the methodology and results

## Model architecture

<p align="center">
  <img src="assets/figures/isa-tas-cas-subsystem.png" width="48%" alt="ISA and TAS-to-CAS Simulink subsystem" />
  <img src="assets/figures/earth-to-body-transformation.png" width="48%" alt="Earth-to-body coordinate transformation model" />
</p>

## Verification cases

<p align="center">
  <img src="assets/figures/validation-sea-level-tas-150.png" width="48%" alt="Sea-level TAS 150 verification case" />
  <img src="assets/figures/validation-12000m-tas-200.png" width="48%" alt="12000 m TAS 200 verification case" />
</p>

The model is shown at two substantially different operating conditions to demonstrate its behaviour across changing atmospheric states.

## Technical report

**[View the complete project report](docs/isa-tas-cas-report.pdf)**

---

## About me

I am a **4A engineering student at Polytech Nantes** in the *Thermique, Énergétique et Mécanique (TEM)* programme, with a **BSc in Mechanical Engineering**.

My technical interests are centered on **thermal-fluid systems, numerical simulation, aerospace propulsion, turbomachinery, and thermal management**. I am developing my portfolio around engineering work that can be explained, reproduced, and supported by technical evidence.

**Current objective:** Summer 2027 internship in aerospace, thermal-fluid engineering, or numerical simulation.
