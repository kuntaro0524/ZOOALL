#!/usr/bin/env python3
"""Measure PIN flux through the same Device path used by ZooNavigator."""

import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "Libs"))

import BLFactory


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler("measure_flux.log")],
    )
    blf = BLFactory.BLFactory()
    blf.initDevice()
    try:
        flux = blf.device.measureFlux()
        print(f"Flux: {flux:.3e} photons/sec")
    finally:
        blf.ms.close()


if __name__ == "__main__":
    main()
