import pandas as pd
from KUMA import KUMA

kuma = KUMA()

flux_density = 7.0e10  # phs/um^2/sec
energies_keV = [8.5, 12.4, 20.0]
beam_sizes = [(1, 1), (5, 5), (10, 10)]

rows = []

for energy in energies_keV:
    wavelength = 12.3984 / energy
    for h_beam, v_beam in beam_sizes:
        area = h_beam * v_beam
        flux = area * flux_density
        dose_1sec = kuma.getDose(h_beam, v_beam, flux, wavelength, 1.0)

        rows.append({
            "energy_keV": energy,
            "wavelength_A": wavelength,
            "beam_size_um": f"{h_beam}x{v_beam}",
            "area_um2": area,
            "flux_density_phs_per_um2_per_sec": flux_density,
            "flux_phs_per_sec": flux,
            "dose_1sec_MGy": dose_1sec,
        })

df = pd.DataFrame(rows)

print("Detailed table")
print(df.to_string(index=False, float_format=lambda x: f"{x:.6f}"))

print("\nPivot table")
pivot = df.pivot(index="energy_keV", columns="beam_size_um", values="dose_1sec_MGy")
print(pivot.to_string(float_format=lambda x: f"{x:.6f}"))
