import pandas as pd
import numpy as np
import os,sys

# CSVファイルを読見込む
# 含まれるデータは
# energy,dose_mgy_per_photon,density_limit
# 左から順に、エネルギー、1フォトンあたりの線量、損傷までのリミット(photons/um2)
df = pd.read_csv("en_dose_lys.csv")
df2 = pd.read_csv("en_dose_oxi.csv")

# energy.vs.dose_mgy_per_photonのグラフを作成する
import matplotlib.pyplot as plt
plt.plot(df['energy'], df['dose_mgy_per_photon'])
plt.plot(df2['energy'], df2['dose_mgy_per_photon'])
plt.xlabel("Energy [keV]")
plt.ylabel("Dose [mGy/photon]")
plt.show()

# energy .vs. dose_mgy_per_photonのグラフについてスプライン補完を行い
# エネルギーが与えられたら、線量を返す関数を作成する
from scipy import interpolate
f = interpolate.interp1d(df['energy'], df['dose_mgy_per_photon'], kind='cubic')

def getDosePerPhoton(energy):
    return f(energy)

def getDensityLimit(energy, target_dose_MGy):
    dose_per_photon = getDosePerPhoton(energy)
    density_limit = target_dose_MGy / dose_per_photon
    return density_limit