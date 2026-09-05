"""Ideal rocket nozzle + simplified 1D vertical ascent simulation.

Reproduces the baseline portfolio case using a simplified ISA atmosphere,
altitude-dependent gravity, aerodynamic drag, propellant depletion, and
SciPy ODE integration. This is a fundamentals-first 1D model, not CFD.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

# Engine / nozzle assumptions
PC = 7.0e6          # chamber pressure [Pa]
TC = 3400.0         # chamber temperature [K]
GAMMA = 1.22
MW = 22.0           # exhaust molecular weight [kg/kmol], approximate
R = 8314.462618 / MW
D_T = 0.10          # throat diameter [m]
EPS = 20.0          # expansion ratio Ae/At

# Vehicle assumptions
M0 = 1500.0         # initial mass [kg]
M_DRY = 900.0       # dry mass [kg]
CD = 0.45
A_REF = 0.35        # reference area [m^2]

# Numerical settings
G0 = 9.80665
R_EARTH = 6_371_000.0
COAST_TIME = 60.0
MAX_STEP = 0.05


def gravity(h):
    return G0 * (R_EARTH / (R_EARTH + h))**2


def atmosphere(h):
    """Simplified ISA: lapse-rate troposphere, isothermal above 11 km."""
    T0, P0, R_AIR, L = 288.15, 101325.0, 287.05287, 0.0065
    h = max(float(h), 0.0)
    if h <= 11_000.0:
        T = T0 - L*h
        P = P0 * (T/T0)**(G0/(R_AIR*L))
    else:
        T11 = T0 - L*11_000.0
        P11 = P0 * (T11/T0)**(G0/(R_AIR*L))
        T = T11
        P = P11 * np.exp(-G0*(h-11_000.0)/(R_AIR*T))
    return T, P, P/(R_AIR*T)


def area_mach(M):
    term = (2/(GAMMA+1)) * (1 + (GAMMA-1)*M**2/2)
    return (1/M) * term**((GAMMA+1)/(2*(GAMMA-1)))


def nozzle(Pa):
    At = np.pi*(D_T/2)**2
    Ae = EPS*At
    mdot = PC*At*np.sqrt(GAMMA/(R*TC)) * (2/(GAMMA+1))**((GAMMA+1)/(2*(GAMMA-1)))
    Me = brentq(lambda M: area_mach(M)-EPS, 1.0001, 50.0)
    Te = TC/(1 + (GAMMA-1)*Me**2/2)
    Pe = PC*(Te/TC)**(GAMMA/(GAMMA-1))
    Ve = Me*np.sqrt(GAMMA*R*Te)
    thrust = mdot*Ve + (Pe-Pa)*Ae
    isp = thrust/(mdot*G0)
    return thrust, isp, mdot, Me


def thrust_at_altitude(h):
    _, Pa, _ = atmosphere(h)
    return max(nozzle(Pa)[0], 0.0)


def run():
    _, _, mdot, Me = nozzle(101325.0)
    burn_time = (M0-M_DRY)/mdot
    final_time = burn_time + COAST_TIME

    def rhs(t, y):
        h, v, m = y
        hm = max(h, 0.0)
        _, _, rho = atmosphere(hm)
        burning = (t <= burn_time) and (m > M_DRY + 1e-6)
        thrust = thrust_at_altitude(hm) if burning else 0.0
        mass_flow = mdot if burning else 0.0
        drag = 0.5*rho*CD*A_REF*v*abs(v)
        return [v, (thrust-drag-m*gravity(hm))/m, -mass_flow]

    sol = solve_ivp(rhs, (0.0, final_time), [0.0, 0.0, M0],
                    max_step=MAX_STEP, rtol=1e-7, atol=1e-9)
    t, h, v, m = sol.t, sol.y[0], sol.y[1], sol.y[2]

    thrust_hist = np.zeros_like(t)
    q_hist = np.zeros_like(t)
    for i in range(len(t)):
        _, _, rho = atmosphere(h[i])
        burning = (t[i] <= burn_time) and (m[i] > M_DRY + 1e-6)
        thrust_hist[i] = thrust_at_altitude(h[i]) if burning else 0.0
        q_hist[i] = 0.5*rho*v[i]**2

    history = pd.DataFrame({
        "t_s": t, "h_m": h, "v_mps": v, "m_kg": m,
        "thrust_N": thrust_hist, "q_Pa": q_hist
    })

    imax = int(np.argmax(q_hist))
    summary = pd.DataFrame([{
        "burn_time_s": burn_time,
        "burnout_altitude_m": float(np.interp(burn_time, t, h)),
        "burnout_velocity_mps": float(np.interp(burn_time, t, v)),
        "max_q_Pa": float(q_hist[imax]),
        "max_q_time_s": float(t[imax]),
        "max_q_altitude_m": float(h[imax]),
        "max_q_velocity_mps": float(v[imax]),
        "max_altitude_in_window_m": float(np.max(h)),
        "velocity_at_end_mps": float(v[-1]),
        "final_time_s": float(t[-1]),
    }])

    altitudes = np.linspace(0, 60_000, 121)
    rows = []
    for altitude in altitudes:
        _, Pa, _ = atmosphere(altitude)
        T, isp, _, _ = nozzle(Pa)
        rows.append((altitude, Pa, T, isp))
    sweep = pd.DataFrame(rows, columns=["altitude_m", "ambient_pressure_Pa", "thrust_N", "isp_s"])

    return history, summary, sweep, Me, mdot


def save_outputs(history, summary, sweep):
    root = Path(__file__).resolve().parents[1]
    data_dir, fig_dir = root/"data", root/"figures"
    data_dir.mkdir(exist_ok=True)
    fig_dir.mkdir(exist_ok=True)

    history.to_csv(data_dir/"rocket_ascent_timeseries.csv", index=False)
    summary.to_csv(data_dir/"rocket_ascent_summary.csv", index=False)
    sweep.to_csv(data_dir/"nozzle_altitude_sweep.csv", index=False)

    q = history.q_Pa.to_numpy()
    imax = int(np.argmax(q))
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    axes[0,0].plot(history.t_s, history.h_m/1000); axes[0,0].set(title="Altitude vs Time", xlabel="Time [s]", ylabel="Altitude [km]")
    axes[0,1].plot(history.t_s, history.v_mps); axes[0,1].set(title="Vertical Velocity vs Time", xlabel="Time [s]", ylabel="Velocity [m/s]")
    axes[0,2].plot(history.t_s, history.thrust_N/1000); axes[0,2].set(title="Thrust vs Time", xlabel="Time [s]", ylabel="Thrust [kN]")
    axes[1,0].plot(history.t_s, q/1000); axes[1,0].scatter(history.t_s.iloc[imax], q[imax]/1000); axes[1,0].set(title="Dynamic Pressure vs Time", xlabel="Time [s]", ylabel="q [kPa]")
    axes[1,1].plot(history.t_s, history.m_kg); axes[1,1].set(title="Mass vs Time", xlabel="Time [s]", ylabel="Mass [kg]")
    axes[1,2].axis("off")
    for ax in axes.ravel()[:5]: ax.grid(True)
    fig.suptitle("1D Rocket Ascent — Key Time Histories")
    fig.tight_layout()
    fig.savefig(fig_dir/"rocket-ascent-dashboard-regenerated.png", dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    history, summary, sweep, Me, mdot = run()
    save_outputs(history, summary, sweep)
    print(f"Exit Mach: {Me:.2f}")
    print(f"Mass flow: {mdot:.2f} kg/s")
    print(summary.to_string(index=False))
