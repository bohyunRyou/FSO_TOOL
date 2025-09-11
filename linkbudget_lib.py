import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 
import math
from scipy import integrate
from scipy.special import erfinv,erfcinv
import streamlit as st
##stream lit data구현

def input_df_val(session_df, cal_list,key_prefix):
    '''session_df : st.session.dataframe , cal_list: 입력값을 통해 산출되는 값에 해당하는 index
    return : df -> session_df에 저장됨.'''
    df_index_li = list(session_df.index)
    df = session_df
    for x in df_index_li:
        c1,c2,c3 = st.columns([5,4,2])
        if x in cal_list:
            ## cal_list값 출력
            with c1:
                st.markdown(f"<div style='text-align:right'>{x+":"}</div>", unsafe_allow_html=True)
            with c2:
                c_v = session_df.loc[x,"val"]
                st.markdown(f"<span style = 'color:purple'><i>{c_v:.2e}</i></span>",
                            unsafe_allow_html=True)
            with c3:
                st.markdown(session_df.loc[x,"unit"])
        else: 
            ## 입력값 사용자로 부터 받거나, default값 출력
            with c1:
                st.markdown(f"<div style='text-align:right'>{x+":"}</div>", unsafe_allow_html=True)
            with c2:
                key = f"ni_{key_prefix}_{x}"
                default_val = session_df.loc[x,"val"]
                if "Numb" in x:
                    default_val= int(default_val)
                    input_val = st.number_input("",default_val,
                                                format="%d", label_visibility = "collapsed" ,key=key)
                else:
                    input_val = st.number_input("",default_val,
                                                format="%.2e",label_visibility="collapsed",key=key)
                df.loc[x,"val"] = input_val
            with c3:
                st.markdown(session_df.loc[x,"unit"])
    return df

#input 함수 연결
# tx antenna cal

def Equiv_hard_diam(W):
    #Equiv.hard diameter
    val = 8**(1/2)*W
    return val
def Divergence_Theta(lambda_, W):
    #Gaussian half divergence
    #lambda_: wavelength, W: Gaussian beam radius
    val = lambda_/(np.pi*W)
    return val
def Rayleigh_range(lambda_, W):
    #Rayleigh range Z_Tx
    val = np.pi*W*W/lambda_
    return val

def Beam_radius_at_RX(lambda_, W,Z):
    # Z: Link distance
    Z_R = Rayleigh_range(lambda_,W)
    
    val = W*np.sqrt(1+(Z/Z_R)**2)
    
    return val
    
def On_axis_intensity_at_Rx(lambda_,W, P,Z, alpha_Tx_optics):
    # P: Tx power(avg.) ,  Beamradius at Rx, alpha_Tx_optics: Tx optics loss
    P_eff = P*10**(alpha_Tx_optics/10)
    W_tx = Beam_radius_at_RX(lambda_,W,Z)
    #print(P_eff,W_tx)
    val = 2*P_eff/(np.pi*W_tx**2)
    return val

#Target Power
def Target_Rx_power(BER,P_fade,amplification_factor, R_b, lambda_): 
    #const
    h = 6.626e-34
    c =299792458
    n_ideal= -np.log(2*BER) # idealized n(phonton)
    n_det = amplification_factor*n_ideal
    z_fade = np.sqrt(2)*erfcinv(2*P_fade)
    
    #b = sigma_tx/theta_tx
    #sigma_db = 17.372*(b)**2
    #M_fade = z_fade*sigma_db
    P_sens = n_det*h*c*R_b/(lambda_)
    val = 10*np.log10(1e3*P_sens) #+ M_fade
    val2 = 10**((val-30)/10)
    val3 = val2/(h*c/lambda_)/R_b
    return val,val2,val3
#link_geom cal
def Link_distance(H_tx,H_rx,alpha_r):
    #slant dist
    Re= 6.371e6
    R_r = Re + H_rx
    R_s = Re+ H_tx
    angle = (90-alpha_r)*np.pi/180
    z =  -R_r*np.cos(angle) + np.sqrt(R_s**2 - (R_r*np.sin(angle))**2)
    return z
def Fresnel_scale(lambda_,Z):
    val = np.sqrt(lambda_*Z)
    return val

# laser(CW) safety cal

def lin_a_tx(a_tx):
    #dB단위 선형화
    val = 10**(a_tx/10)
    return val

def I_emit(P_tx,a_tx,W_tx):
    #unit : W/m^2
    val = (2*P_tx*lin_a_tx(a_tx))/(math.pi*W_tx**2)
    return val
def M_safety(I_emit,I_safe):
    #unit : dB
    val = I_emit/I_safe
    val = 10*np.log10(val)
    return val
def NOHD(Z_tx,I_emit, I_safe):
    #unit : m
    val = Z_tx*(I_emit/I_safe -1)**(1/2)
    return val 
#Static cal
def W_to_dBm(val):
    val = 10*np.log10(val*1e3)
    return val
def Tx_gain(theta_tx):
    #unit : dBi
    val = 8/(theta_tx**2)
    val = 10*np.log10(val)
    return val
def Isotropic_space_loss(lambda_,Z):
    #unit : dB
    val = (lambda_/(4*np.pi*Z))**2
    val = 10*np.log10(val)
    return val
def Rx_gain(theta_rx):
    #unit : dBi
    val = 8/(theta_rx**2)
    val = 10*np.log10(val)
    return val
def Near_field_loss(Z,Z_tx,Z_rx):
    #linear화
    #unit : dB
    val = (Z**2)/(Z**2 +(Z_tx+Z_rx)**2)
    val = 10*np.log10(val)
    return val   
def Mean_Tx_pointing_loss(Tx_pointing_error,theta_tx):
    val = Tx_pointing_error/theta_tx
    val = np.exp(-2*val*val)
    val = 10*np.log10(val)
    return val
def Clear_sky_attenuation(visibility,h_eff, elevation,lambda_):
    elevation = elevation
    
    d_atm = h_eff/np.sin(elevation*np.pi/180)/1e3
    visibility = visibility/1e3
    if visibility>50:
        q = 1.6
    elif visibility>6:
        q = 1.3
    elif visibility>1:
        q = 0.585*visibility**(1/3)
    else:
        q = 0
    print(q)
    print(d_atm)
    coeff = 3.91/visibility*(lambda_/0.55e-6)**(-q)
    print(coeff)
    val = np.exp(-coeff*d_atm)
    val = 10*np.log10(val)
    return val

#def Beam_spread_loss():
def Mean_Rx_Strehl_ratio(D_T,r0):
    #D_rx:equiv hard diameter ,r0: Fried's parameter
    val = 1 + (D_T/r0)**(5/3)
    val = val**(-6/5)
    val = 10*np.log10(val)  # unit to dB 
    return val

def Static_Rx_power(P_tx_W,L_tx,G_tx ,L_is,G_rx,L_nf,L_point,L_att,L_mean_strehl,L_rx_opt):
    #unit : dB
    val = P_tx_W+L_tx+G_tx+L_is+G_rx+L_nf+L_point+L_att+L_mean_strehl+L_rx_opt
    return val

def Link_margin(P_target, P_static):
    val = P_static - P_target
    return val
def Fried_param(HV_func, alpha=20, H = 4e05, lambda_ = 1.55e-6):
    #xi = zenith angle, 90- elevation angle(alpha)
    #k: wave num
    #H: satellite's altitude 
    #plane wave formula
    xi = 90- alpha
    xi = xi*np.pi/180 # deg to rad convert
    k = 2*np.pi/lambda_
    h_ogs = 0
    val,err = integrate.quad(HV_func, h_ogs, H,epsabs=1e-12, epsrel=1e-9)
    val = 0.423*k*k*val/math.cos(xi)
    val = val**(-3/5)
    return val
def HV_func(h):
    #표준값 5/7 표준 대기 난류 모델. 고도 5km에서 강한 난류, 7m/s고도풍 속도기반
    w = 21
    A = 1.7e-14
    val = 0.00594*(w/27)**2*(1e-5*h)**10*np.exp(-h/1000) + 2.7*1e-16*np.exp(-h/1500)+ A*np.exp(-h/100)
    return val

def h(z):
    Re = 6.371e6
    h_rx = 0
    alpha = 20*np.pi/180
    R0 = Re + h_rx
    val = np.sqrt(R0**2 + z**2 + 2*R0*z*np.sin(alpha)) - Re
    return val
def integrand(z):
    val = HV_func(h(z))*z**(5/6)
    return val 
    
def sigma_R(HV_func,z,lambda_):
    # In weak turbulence, sigma_I^2 can be approximated by the Rytov Index.
    # val -> squared ->root 
    val,err = integrate.quad(integrand,0,z,epsabs=1e-12, epsrel=1e-9)
    val = val*(19.2/(lambda_**(7/6)))
    val = np.sqrt(val)
    return val
def Tx_pointing_fade_loss(P_fade,sigma_tx, theta_tx):
    #unit: dB
    
    b_tx = sigma_tx/theta_tx
    val = P_fade**(4*b_tx**2)
    val = 10*np.log10(val)
    return val

def sigma_I(sigma_r):
    val1 = (0.49*sigma_r**2)/(1+1.11*sigma_r**(12/5))**(7/6) + 0.51*sigma_r**2/(1+0.69*sigma_r**(12/5))**(5/6)
    val = np.exp(val1)-1
    val = np.sqrt(val)
    return val
    
def sigma_eff(D, sigma_I, lambda_, Z):
    # Aperture averaging
    # D: equiv hard diam, sigma_I : point scintillation index, lambda_ : wavelength, Z: slant distance
    k = np.pi*2/lambda_
    
    A_pw = (1 + 1.062*k*D*D/(4*Z))**(-7/6)
    val = A_pw*sigma_I**2
    val = np.sqrt(val)
    return val
def Scintillation_loss(rho_thr, sigma_eff):
    val = 4.343*(erfinv(2*rho_thr - 1)*(2*np.log(sigma_eff**2 + 1))**(1/2)- (1/2)*np.log(sigma_eff**2+1))
    return val
    
def SR_shortterm(D,r):
    val = (1 + 0.28*(D/r)**(5/3))
    val = 1/val
    val = 10*np.log10(val)
    return val
def SR_longterm(D,r):
    val = r/D
    val2 = val**2 - 0.6159*val**3 + 0.5*val**5
    val2 = 10*np.log10(val2)
    return val2
def BER_at_probe(sigma_00, sigma_01,sigma_10, P_probe, lambda_, Rb):
    #RX Power at probe [dB]
    #sigma_00, sigma_01: signal indep, sigma_10: signal dep
    h = 6.26e-34 #plank's const
    c = 299792458 #light speed
    P = 10**((P_probe-30)/10) # unit conv dBm->W 
    Ns = P*lambda_/(h*c*Rb)
    #print(Ns)
    sigma_tot = np.sqrt(sigma_00**2 + sigma_01**2 + Ns*sigma_10**2)
    val = math.erfc(Ns/(np.sqrt(2)*sigma_tot))/2
    return val       