import pandas as pd
import numpy as np


##input table

laser_source = {
    "val":[3.0e-1,1.55e-6],
    "unit":["W","m"]}
laser_source_index = ["Tx power(avg)","Wavelength"]
laser_source_df = pd.DataFrame(laser_source, index = laser_source_index)

Tx_antenna ={
    "val":[4.93e-03,0,1.00e-04,0,0, -1.0,0,1],
    "unit":["m","m","rad","m","m","dB","W/m^2","num"]
}
Tx_antenna_index = ["Tx radius W_Tx","Equiv. hard diameter D_Tx","Divergence theta_Tx","Rayleigh range Z_Tx","Beam radius at Rx W","Tx optics loss a_Tx_optics","On-axis intensity at Rx","Numb. of indep. beams"]
Tx_antenna_df = pd.DataFrame(Tx_antenna, index = Tx_antenna_index)


Link_geometry={
    "val":[0,4.00e05, 0, 20.0, 0],
    "unit":["m","m","m","deg","m"]
}
Link_geometry_index = ["Link distance Z","Tx height", "Rx height", "Elevation alpha at R", "Fresnel scale"]
Link_geometry_df = pd.DataFrame(Link_geometry, index = Link_geometry_index)

Rx_antenna = {
    "val":[2.85e-1, 0, 0, 0, 1, -3.0],
    "unit":["m","m","rad","m","numb","dB"]
}
Rx_antenna_index = ["Rx aperture radius W_Rx", "Equiv. hard diameter D_Rx", "DL-FoV radius theta_Rx", 
                    "Rayleigh range Z_Rx", "Numb. of apertures", "Rx optics loss a_Rx_optics" ]
Rx_antenna_df = pd.DataFrame(Rx_antenna, index = Rx_antenna_index)


Rx_requirements = {
    "val":[1.0e-6, -45.7, 2.67e-08, 2.08e02, 1.0e-2],
    "unit":[" ","dBm","W","ph/bit", " " ]
}
Rx_requirements_index = ["Target BER", "Target Rx Power[dBm]", "Target Rx Power[W]", 
                         "Target Rx Power[ph/bit]", "Fade loss probability P_Fade"]
Rx_requirements_df = pd.DataFrame(Rx_requirements, index = Rx_requirements_index)

Rx_sensitivity_model = {
    "val":[1e9, 10,0, 1.0e1, 5.0e0],
    "unit":["bit/s","","ph/bit","ph/bit","ph/bit"]
}
Rx_sensitivity_model_index = ["Data rate(physical layer)", "Amplification factor","Backgr.light noise sigma00","Rx constant noise sigma01","sigma10"]
Rx_sensitivity_model_df = pd.DataFrame(Rx_sensitivity_model, index = Rx_sensitivity_model_index)

Rx_requirements = {
    "val":[1.0e-6, 0, 0,0,1.0e-2],
    "unit":["","dBm","W","ph/bit",""]
}
Rx_requirements_index = ["Target BER","Target Rx Power[dBm]","Target Rx Power[W]","Target Rx Power[ph/bit]","Fade loss probability P_fade"]
Rx_requirements_df = pd.DataFrame(Rx_requirements, index = Rx_requirements_index)

##output table

laser_safety = {
    "val": np.zeros(7),
    "unit":["W","","m","W/m^2","W/m^2","dB","m"]
}
laser_safety_index = ["Tx Pow(avg)P_Tx", "Tx optics loss a_Tx-optics", "Minimum beam radius W_Tx",
                     "Max.emitted intensity I_emit", "Max. permitted intensity I_safe",
                     "Safety margin M_safety", "NOHD"]

laser_safety_df = pd.DataFrame(laser_safety, index = laser_safety_index)

Static = {
    "val":np.zeros(15),
    "unit": ["dBm", "dB","dBi", "dB", "dBi", "dB", "dB", "dB", "dB","dB","dB","dBm","dBm","dB",""]
}
Static_index = ["Tx power", "Tx optics loss", "Tx gain", "Isotropic space loss", "Rx gain", "Near-field loss", 
               "Mean Tx pointing loss", "Clear-sky attenuation", "Beam-spread loss", "Mean Rx Strehl ratio", "Rx optics loss",
               "Static Rx Power", "Target Rx power", "Link margin", "Static BER"]
Static_df = pd.DataFrame(Static, index = Static_index)

Dynamic_fades = {
    "val": np.zeros(7),
    "unit": ["dB","dB","dB","dBm","dBm","dB",""]
}

Dynamic_fades_index = ["Tx pointing fade loss", "Scintillation fade loss", "Rx Strehl ratio", "Rx power at prob","Target Rx power",
            "Link margin at prob", "Ber at prob"]
Dynamic_fades_df = pd.DataFrame(Dynamic_fades, index = Dynamic_fades_index)



