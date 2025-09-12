import streamlit as st
import pandas as pd
import altair as alt

from graphviz import Digraph
import streamlit.components.v1 as components
import linkbudget_df
import linkbudget_lib as ll
from PIL import Image

##st_data
## st_numinput set
st.markdown("""
    <style>
    div[data-baseweb="input"] button {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

st.title("FSO_Link Budget Tool")

#page_config
logo = Image.open("gr_logo.png")
st.set_page_config(
    page_title = "FSO_Link Budget Tool",
    page_icon = logo,
    layout = "wide",
    initial_sidebar_state = "expanded"
)
alt.themes.enable("dark")

green_logo = "GR.png"
##session_state
laser_source_cal_li = []
Tx_Antenna_cal_li = ["Equiv. hard diameter D_Tx","Rayleigh range Z_Tx", "Beam radius at Rx W","On-axis intensity at Rx"]
Link_geometry_cal_li =["Link distance Z", "Fresnel scale"]
Rx_antenna_cal_li = ["Equiv. hard diameter D_Rx","DL-FoV radius theta_Rx","Rayleigh range Z_Rx"]
Rx_sensitivity_model_cal_li = []
Rx_requirements_cal_li =[]
if "laser_source" not in st.session_state:
    st.session_state.laser_source = linkbudget_df.laser_source_df
if "Tx_antenna" not in st.session_state:
    st.session_state.Tx_antenna = linkbudget_df.Tx_antenna_df
if "Tx_pointing_error" not in st.session_state:
    st.session_state.Tx_pointing_error = linkbudget_df.Tx_pointing_error_df
if "Link_geometry" not in st.session_state:
    st.session_state.Link_geometry = linkbudget_df.Link_geometry_df
if "Clear_sky_attenuation" not in st.session_state:
    st.session_state.Clear_sky_attenuation = linkbudget_df.Clear_sky_attenuation_df
if "Rx_antenna" not in st.session_state:
    st.session_state.Rx_antenna = linkbudget_df.Rx_antenna_df
if "Rx_requirements" not in st.session_state:
    st.session_state.Rx_requirements = linkbudget_df.Rx_requirements_df
if "Rx_sensitivity_model" not in st.session_state:
    st.session_state.Rx_sensitivity_model = linkbudget_df.Rx_sensitivity_model_df
##output_Df는 styler로 미리 색상지정

if "laser_safety" not in st.session_state:
    st.session_state.laser_safety = linkbudget_df.laser_safety_df
if "Static" not in st.session_state:
    st.session_state.Static = linkbudget_df.Static_df
if "Dynamic_fades" not in st.session_state:
    st.session_state.Dynamic_fades = linkbudget_df.Dynamic_fades_df

tab1, tab2 = st.tabs(['Tool', 'Flow chart'])
with tab1:
    ## ui에 표시되는 data_editor객체들은 수정시, 좌측 변수에 그 값이 반영됨.    
    col1, col2, col3 = st.columns(3)
    with col1:
        
        st.header("Tx parameters")
        with st.expander("Laser source",expanded =True):
            st.session_state.laser_source = ll.input_df_val(st.session_state.laser_source, laser_source_cal_li,"ls")
        with st.expander("Tx antenna",expanded=True):
            st.session_state.Tx_antenna = ll.input_df_val(st.session_state.Tx_antenna,Tx_Antenna_cal_li,"ant")
        with st.expander("Tx pointing error", expanded=False):
            st.session_state.Tx_pointing_error = ll.input_df_val(st.session_state.Tx_pointing_error,[],"txp")
    with col2:
        st.header("Channel parameters")
        with st.expander("Link geometry", expanded=True):
            st.session_state.Link_geometry = ll.input_df_val(st.session_state.Link_geometry, Link_geometry_cal_li,"geo")
        with st.expander("Clear-sky attenuation", expanded=False):
            st.session_state.Clear_sky_attenuation = ll.input_df_val(st.session_state.Clear_sky_attenuation,[],"Csa")
    with col3:
        st.header("Rx parameters")
        with st.expander("Rx antenna",expanded=True):
            st.session_state.Rx_antenna = ll.input_df_val(st.session_state.Rx_antenna,Rx_antenna_cal_li,"rxa")
        with st.expander("Rx requirements",expanded=False):
            st.session_state.Rx_requirements = ll.input_df_val(st.session_state.Rx_requirements, Rx_requirements_cal_li,"rxr")
        with st.expander("Rx sensitivity model",expanded=False):
            st.session_state.Rx_sensitivity_model = ll.input_df_val(st.session_state.Rx_sensitivity_model,Rx_sensitivity_model_cal_li,"rxs")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Laser(CW) safety")
        styled_laser_safety = st.session_state.laser_safety.style.set_properties(
        subset =(["Safety margin M_safety"],["val"]),**{"background-color":"Salmon"})
        laser_safety_de = st.dataframe(styled_laser_safety.format({"val":"{:.1e}"}))
    with col2:
        st.header("Static")
        styled_Static = st.session_state.Static.style.set_properties(
        subset = (["Link margin"],["val"]),**{"background-color":"SpringGreen"}
    )
        Static_de = st.dataframe(styled_Static.format({"val":"{:.1f}"}),height=600)
    with col3:
        st.header("Dynamic(fades)")
        styled_Dynamic_fades = st.session_state.Dynamic_fades.style.set_properties(
        subset =(["Link margin at prob"],["val"]),**{"background-color":"Salmon"}
    )
        Dynamic_fades_de = st.dataframe(styled_Dynamic_fades.format({"val":"{:.1f}"}))
with tab2:
    ##flow charat
    st.header("Laser (CW) Safety")
    graph_code_1 = """
    digraph Safety {
        rankdir=BT;  // 방향: RL(왼→오른쪽), TB(위→아래)
    
        node [shape=box, fontname="NanumGothic", fontsize=12]
        edge [arrowhead = none, color = gray40, penwidth = 1]
        "Safety margin M_safety" [color = ".666 1 1", style=filled, shape=oval, fontcolor = white]
        
        "Max.emitted intensity I_emit" [color =cornflowerblue, style =filled, fontcolor = white]
        "Max.permitted intensity I_safe" [color = cornflowerblue, style =filled, fontcolor = white]

        "Tx_optic loss a_Tx-Optics" [color=lightskyblue, style=filled]
        "Tx Pow(avg.)P_tx" [color=lightskyblue, style=filled]
        "Minimum beam radius W_Tx"[color=lightskyblue, style=filled]

        "Tx_optic loss a_Tx-Optics" ->"Max.emitted intensity I_emit"
        "Tx Pow(avg.)P_tx" -> "Max.emitted intensity I_emit"
        "Minimum beam radius W_Tx" ->"Max.emitted intensity I_emit"

        "Max.emitted intensity I_emit"-> "Safety margin M_safety"
        "Max.permitted intensity I_safe"-> "Safety margin M_safety"
        
    }
    """
    st.graphviz_chart(graph_code_1)
    st.header("Static")

    graph_code_2 = """
    digraph Static {
        rankdir = RL;
        node [shape=box, fontname="NanumGothic", fontsize=12]
        edge [arrowhead = none, color = gray40, penwidth = 1]
        "Link margin" [color = ".666 1 1", style=filled, shape=oval, fontcolor = white]

        "Static Rx power" [color =cornflowerblue, style =filled, fontcolor = white,fontsize =10]
        "Target Rx power" [color =cornflowerblue, style =filled, fontcolor = white,fontsize =10]
        //Static
        "Tx power" [color=lightskyblue, style=filled,fontsize =8]
        "Tx optics loss" [color=lightskyblue, style=filled,fontsize =8]
        "Tx gain" [color=lightskyblue, style=filled,fontsize =8]
        "Isotropic space loss" [color=lightskyblue, style=filled,fontsize =8]
        "Rx gain" [color=lightskyblue, style=filled,fontsize =8]
        "Near-field loss" [color=lightskyblue, style=filled,fontsize =8]
        "Mean Tx pointing loss" [color=lightskyblue, style=filled,fontsize =8]
        "Clear-sky attenuation" [color=lightskyblue, style=filled,fontsize =8]
        "Beam-spread loss" [color=lightskyblue, style=filled,fontsize =8]
        "Mean Rx Strehl ratio" [color=lightskyblue, style=filled,fontsize =8]
        "Rx optics loss" [color=lightskyblue, style=filled,fontsize =8]
        //Target 
        "BER" [color=lightskyblue, style=filled,fontsize =8]
        "P_fade" [color=lightskyblue, style=filled,fontsize =8]
        "Amplification_factor" [color=lightskyblue, style=filled,fontsize =8]
        //input level
        "Wavelength" [color = ".458 1 1" ,style=filled,fontsize =5]
        "Link distance,Z" [label = "Link distance \n\n Z", color = ".458 1 1" ,style=filled,fontsize =5] 
        "Divergence theta_Tx" [label ="Divergence \n\n theta_Tx", color = ".458 1 1" ,style=filled,fontsize =5]
        "DL-FoV radius theta_Rx" [label = "DL-FoV radius \n\ntheta_Rx",color = ".458 1 1" ,style=filled,fontsize =5] 

        "Tx pointing error" [color = ".458 1 1" ,style=filled,fontsize =5] 
        "Beam radius at Rx W" [label = "Beam radius \n\n at Rx W",color = ".458 1 1" ,style=filled,fontsize =5] 
        "Elevation angle at R" [label = "Elevation \n\n angle at R",color = ".458 1 1" ,style=filled,fontsize =5] 
        "effective atmospheric thickness" [label = "Elevation \n\n\n angle at R",color = ".458 1 1" ,style=filled,fontsize =5] 
        "visibility" [label = "Elevation \n\n\n angle at R",color = ".458 1 1" ,style=filled,fontsize =5] 
        "Rx height H_Rx" [label = "Rx height\n\n H_Rx", color = ".458 1 1",style=filled,fontsize =5]
        "Equiv.hard diameter D_Rx" [label = "Equiv.hard \n\n diameter D_Rx",color = ".458 1 1" ,style=filled,fontsize =5] 
        "Rayleigh range Z_TX"[label = "Rayleigh \n\n range Z_TX",color = ".458 1 1" ,style=filled,fontsize =5] 
        "Rayleigh range Z_RX"[label = "Rayleigh \n\n range Z_RX",color = ".458 1 1" ,style=filled,fontsize =5] 

        //Tree
        "Divergence theta_Tx"-> "Tx gain"  
        "Wavelength" -> "Isotropic space loss"
        "Link distance,Z" -> "Isotropic space loss"
        "DL-FoV radius theta_Rx"-> "Rx gain"  
        "Link distance,Z"->"Near-field loss"
        "Rayleigh range Z_TX"->"Near-field loss"
        "Rayleigh range Z_RX"->"Near-field loss"

        "Divergence theta_Tx" -> "Mean Tx pointing loss" 
        "Tx pointing error"-> "Mean Tx pointing loss" 

        "visibility" -> "Clear-sky attenuation"
        "effective atmospheric thickness" -> "Clear-sky attenuation"
        "Elevation angle at R" -> "Clear-sky attenuation"
        "Wavelength" -> "Clear-sky attenuation"
        "Elevation angle at R" -> "Clear-sky attenuation"

        "Equiv.hard diameter D_Rx" -> "Mean Rx Strehl ratio"
        "Elevation angle at R" -> "Mean Rx Strehl ratio"
        "Wavelength"-> "Mean Rx Strehl ratio"
        "Rx height H_Rx"-> "Mean Rx Strehl ratio"

        "Tx power" -> "Static Rx power"
        "Tx optics loss" -> "Static Rx power"
        "Tx gain" -> "Static Rx power"
        "Isotropic space loss" -> "Static Rx power"
        "Rx gain" -> "Static Rx power"
        "Near-field loss" -> "Static Rx power"
        "Mean Tx pointing loss" -> "Static Rx power"
        "Clear-sky attenuation" -> "Static Rx power"
        "Beam-spread loss" -> "Static Rx power"
        "Mean Rx Strehl ratio" -> "Static Rx power"
        "Rx optics loss" -> "Static Rx power"
        
        "BER"->"Target Rx power"
        "P_fade"->"Target Rx power"
        "Amplification_factor"->"Target Rx power"

        "Static Rx power" -> "Link margin"
        "Target Rx power" -> "Link margin"
        }
        """
    st.graphviz_chart(graph_code_2)
    st.header("Dynamic")

    graph_code_3 = """
    digraph Dynamic {
    rankdir = RL;
    node [shape=box, fontname="NanumGothic", fontsize=14]
    edge [arrowhead = none, color = gray40, penwidth = 1]
    "Link margin at probe" [color = ".666 1 1", style=filled, shape=oval, fontcolor = white]

    "Rx power at prob" [color =cornflowerblue, style =filled, fontcolor = white,fontsize =10]
    "Target Rx power" [color =cornflowerblue, style =filled, fontcolor = white,fontsize =10]
    //
    "Static Rx power" [color=lightskyblue, style=filled,fontsize =8]
    "Dynamic Rx power" [color=lightskyblue, style=filled,fontsize =8]
    
    
    "Tx pointing fade loss" [color = ".541 1 1" ,style=filled,fontsize =6]
    "Scintillation fade loss" [color = ".541 1 1" ,style=filled,fontsize =6]
    "Rx Strehl ratio" [color = ".541 1 1" ,style=filled,fontsize =6]

    "Tx power" [color = ".541 1 1" ,style=filled,fontsize =6]
    "Tx optics loss" [color = ".541 1 1" ,style=filled,fontsize =6]
    "Tx gain" [color = ".541 1 1" ,style=filled,fontsize =6]
    "Isotropic space loss" [color = ".541 1 1" ,style=filled,fontsize =6]
    "Rx gain" [color = ".541 1 1" ,style=filled,fontsize =6]
    "Near-field loss" [color = ".541 1 1" ,style=filled,fontsize =6]

    "Mean Tx pointing loss" [color = ".541 1 1" ,style=filled,fontsize =6]
    "Clear-sky attenuation" [color = ".541 1 1" ,style=filled,fontsize =6]
    "Beam-spread loss" [color = ".541 1 1" ,style=filled,fontsize =6]
    "Mean Rx Strehl ratio" [color = ".541 1 1" ,style=filled,fontsize =6]
    "Rx optics loss" [color = ".541 1 1" ,style=filled,fontsize =6]

    
    //Target 
    "BER" [color=lightskyblue, style=filled,fontsize =8]
    "P_fade" [color=lightskyblue, style=filled,fontsize =8]
    "Amplification_factor" [color=lightskyblue, style=filled,fontsize =8]

    //input level
    "Wavelength" [color = ".458 1 1" ,style=filled,fontsize =3]
    "Link distance,Z" [label = "Link distance \n\n\n Z",color = ".458 1 1" ,style=filled,fontsize =3] 
    "Divergence theta_Tx" [label ="Divergence \n\n theta_Tx", color = ".458 1 1" ,style=filled,fontsize =3]
    "DL-FoV radius theta_Rx" [label = "DL-FoV radius \n\n\ntheta_Rx",color = ".458 1 1" ,style=filled,fontsize =3] 
    "σ_theta" [color = ".458 1 1" ,style=filled,fontsize =3] 
    "Beam radius at Rx W" [label = "Beam radius \n\\nnat Rx W",color = ".458 1 1" ,style=filled,fontsize =3] 
    "Elevation angle at R" [label = "Elevation \n\n\n angle at R",color = ".458 1 1" ,style=filled,fontsize =3] 
    
    
    "Rx height H_Rx" [label = "Rx height\n\n\n H_Rx", color = ".458 1 1",style=filled,fontsize =3]
    "Equiv.hard diameter D_Rx" [label = "Equiv.hard \n\n\n diameter D_Rx",color = ".458 1 1" ,style=filled,fontsize =3] 
    "Rayleigh range Z_TX"[label = "Rayleigh \n\n\n range Z_TX",color = ".458 1 1" ,style=filled,fontsize =3] 
    "Rayleigh range Z_RX"[label = "Rayleigh \n\n\n range Z_RX",color = ".458 1 1" ,style=filled,fontsize =3] 
    "effective atmospheric thickness" [label = "Elevation \n\n\n angle at R",color = ".458 1 1" ,style=filled,fontsize =3] 
    "visibility" [label = "Elevation \n\n\n angle at R",color = ".458 1 1" ,style=filled,fontsize =3] 
    "Tx pointing error" [color = ".458 1 1" ,style=filled,fontsize =3]
    //static rx power
    "Divergence theta_Tx"-> "Tx gain"  
    "Wavelength" -> "Isotropic space loss"
    "Link distance,Z" -> "Isotropic space loss"
    "DL-FoV radius theta_Rx"-> "Rx gain"  
    "Link distance,Z"->"Near-field loss"
    "Rayleigh range Z_TX"->"Near-field loss"
    "Rayleigh range Z_RX"->"Near-field loss"

    "Divergence theta_Tx" -> "Mean Tx pointing loss" 
    "Tx pointing error"-> "Mean Tx pointing loss" 

    "visibility" -> "Clear-sky attenuation"
    "effective atmospheric thickness" -> "Clear-sky attenuation"
    "Elevation angle at R" -> "Clear-sky attenuation"
    "Wavelength" -> "Clear-sky attenuation"
    "Elevation angle at R" -> "Clear-sky attenuation"

    "Equiv.hard diameter D_Rx" -> "Mean Rx Strehl ratio"
    "Elevation angle at R" -> "Mean Rx Strehl ratio"
    "Wavelength"-> "Mean Rx Strehl ratio"
    "Rx height H_Rx"-> "Mean Rx Strehl ratio"

    //dynamic rx power tree
        
    "σ_theta"-> "Tx pointing fade loss" 
    "Link distance,Z" -> "Tx pointing fade loss"
    "Beam radius at Rx W" -> "Tx pointing fade loss" 
    //scintillaton +
    

    "Equiv.hard diameter D_Rx" -> "Rx Strehl ratio"
    "Elevation angle at R" -> "Rx Strehl ratio"
    "Wavelength"-> "Rx Strehl ratio"
    "Rx height H_Rx"-> "Rx Strehl ratio"


    "Tx power" -> "Static Rx power"
    "Tx optics loss" -> "Static Rx power"
    "Tx gain" -> "Static Rx power"
    "Isotropic space loss" -> "Static Rx power"
    "Rx gain" -> "Static Rx power"
    "Near-field loss" -> "Static Rx power"
    "Mean Tx pointing loss" -> "Static Rx power"
    "Clear-sky attenuation" -> "Static Rx power"
    "Beam-spread loss" -> "Static Rx power"
    "Mean Rx Strehl ratio" -> "Static Rx power"
    "Rx optics loss" -> "Static Rx power"


    "Tx pointing fade loss" -> "Dynamic Rx power"
    "Scintillation fade loss" -> "Dynamic Rx power"
    "Rx Strehl ratio" -> "Dynamic Rx power"
    
    "Static Rx power" -> "Rx power at prob"
    "Dynamic Rx power" -> "Rx power at prob"
    
    "BER"->"Target Rx power"
    "P_fade"->"Target Rx power"
    "Amplification_factor"->"Target Rx power"
    
    "Rx power at prob"->  "Link margin at probe"
    "Target Rx power" -> "Link margin at probe"
    }
    """
    st.graphviz_chart(graph_code_3)

    st.header("Only Dynamic Rx power")
    graph_code_4 = """
    digraph Dynamic {
    rankdir = RL;
    node [shape=box, fontname="NanumGothic", fontsize=14]
    edge [arrowhead = none, color = gray40, penwidth = 1]

    "Dynamic Rx power" [color=lightskyblue, style=filled,fontsize =8]
    
    
    "Tx pointing fade loss" [color = ".541 1 1" ,style=filled,fontsize =6]
    "Scintillation fade loss" [color = ".541 1 1" ,style=filled,fontsize =6]
    "Rx Strehl ratio" [color = ".541 1 1" ,style=filled,fontsize =6]


    

    //input level
    "Wavelength" [color = ".458 1 1" ,style=filled,fontsize =3]
    "Link distance,Z" [label = "Link distance \n\n\n Z",color = ".458 1 1" ,style=filled,fontsize =3] 
    
    "σ_theta" [color = ".458 1 1" ,style=filled,fontsize =3] 
    "Beam radius at Rx W" [label = "Beam radius \n\\nnat Rx W",color = ".458 1 1" ,style=filled,fontsize =3] 
    "Elevation angle at R" [label = "Elevation \n\n\n angle at R",color = ".458 1 1" ,style=filled,fontsize =3] 
    
    
    "Rx height H_Rx" [label = "Rx height\n\n\n H_Rx", color = ".458 1 1",style=filled,fontsize =3]
    "Equiv.hard diameter D_Rx" [label = "Equiv.hard \n\n\n diameter D_Rx",color = ".458 1 1" ,style=filled,fontsize =3] 

    //dynamic rx power tree
        
    "σ_theta"-> "Tx pointing fade loss" 
    "Link distance,Z" -> "Tx pointing fade loss"
    "Beam radius at Rx W" -> "Tx pointing fade loss" 
    //scintillaton +
    

    "Equiv.hard diameter D_Rx" -> "Rx Strehl ratio"
    "Elevation angle at R" -> "Rx Strehl ratio"
    "Wavelength"-> "Rx Strehl ratio"
    "Rx height H_Rx"-> "Rx Strehl ratio"


    "Tx pointing fade loss" -> "Dynamic Rx power"
    "Scintillation fade loss" -> "Dynamic Rx power"
    "Rx Strehl ratio" -> "Dynamic Rx power"
    

    }
    """
    st.graphviz_chart(graph_code_4)

with st.sidebar:
    st.image(green_logo, width = 200)
    st.title("Configuration")
    mode_li = ["NO AO","WITH AO"]
    selected_mode = st.selectbox("Select mode", mode_li, index = len(mode_li)-1)
    if st.button('cal_input params'):
        # Tx_antenna none val cal
        #link_geometry
        laser_source_de = st.session_state.laser_source 
        Link_geometry_de = st.session_state.Link_geometry
        Tx_antenna_de = st.session_state.Tx_antenna
        Rx_antenna_de = st.session_state.Rx_antenna 
        Rx_sensitivity_model_de = st.session_state.Rx_sensitivity_model
        Rx_requirements_de = st.session_state.Rx_requirements

        lambda_ = laser_source_de.loc["Wavelength"]["val"]
        H_tx =Link_geometry_de.loc["Tx height","val"]
        H_rx =Link_geometry_de.loc["Rx height","val"]
        alpha_r =Link_geometry_de.loc["Elevation alpha at R","val"]
        
        Link_geometry_de.loc["Link distance Z","val"] = ll.Link_distance(H_tx,H_rx,alpha_r)
        Z = Link_geometry_de.loc["Link distance Z"]["val"]
        Link_geometry_de.loc["Fresnel scale","val"] = ll.Fresnel_scale(lambda_,Z)
        st.session_state.Link_geometry = Link_geometry_de.copy()
        W = Tx_antenna_de.loc["Tx radius W_Tx"]["val"]
        
        
        P = laser_source_de.loc["Tx power(avg)"]["val"]
        alpha_Tx_optics = Tx_antenna_de.loc["Tx optics loss a_Tx_optics","val"] 
        Tx_antenna_de.loc["Equiv. hard diameter D_Tx","val"] =ll.Equiv_hard_diam(W)
        Tx_antenna_de.loc["Divergence theta_Tx","val"] = ll.Divergence_Theta(lambda_, W)
        Tx_antenna_de.loc["Rayleigh range Z_Tx","val"] = ll.Rayleigh_range(lambda_, W)
        Tx_antenna_de.loc["Beam radius at Rx W","val"] = ll.Beam_radius_at_RX(lambda_, W,Z)
        Tx_antenna_de.loc["On-axis intensity at Rx","val"] = ll.On_axis_intensity_at_Rx(lambda_,W, P,Z, alpha_Tx_optics)
        st.write('calculated')
        st.session_state.Tx_antenna = Tx_antenna_de.copy()
        
    
        # Rx antenna unknown val cal
        # D_Rx, Theta_Rx, Z_Rx --> equal formula in Tx -> reuse
        W_Rx = Rx_antenna_de.loc["Rx aperture radius W_Rx","val"] 
        Rx_antenna_de.loc["Equiv. hard diameter D_Rx","val"] =ll.Equiv_hard_diam(W_Rx)
        Rx_antenna_de.loc["DL-FoV radius theta_Rx","val"] = ll.Divergence_Theta(lambda_, W_Rx)
        Rx_antenna_de.loc["Rayleigh range Z_Rx","val"] = ll.Rayleigh_range(lambda_, W_Rx)
    
        #Rx_requirements cal
        amplification_factor = Rx_sensitivity_model_de.loc["Amplification factor","val"]
        R_b = Rx_sensitivity_model_de.loc["Data rate(physical layer)","val"]
        BER = Rx_requirements_de.loc["Target BER","val"]
        P_fade = Rx_requirements_de.loc["Fade loss probability P_fade","val"]
        amplification_factor = Rx_sensitivity_model_de.loc["Amplification factor","val"]
    
        st.session_state.Rx_antenna = Rx_antenna_de.copy()
        P1,P2,P3 = ll.Target_Rx_power(BER,P_fade,amplification_factor, R_b, lambda_)

        Rx_requirements_de.loc["Target Rx Power[dBm]","val"] = P1
        Rx_requirements_de.loc["Target Rx Power[W]","val"] = P2
        Rx_requirements_de.loc["Target Rx Power[ph/bit]","val"] = P3
        st.session_state.Rx_requirements = Rx_requirements_de.copy()

        st.rerun()

    if st.button('Cal_output'):
        #output -> styler type <- df 에 값 저장하고 나중에 변환
        #Laser (CW) safety cal
        laser_source_de = st.session_state.laser_source 
        Link_geometry_de = st.session_state.Link_geometry
        Tx_antenna_de = st.session_state.Tx_antenna
        Rx_antenna_de = st.session_state.Rx_antenna 
        Rx_sensitivity_model_de = st.session_state.Rx_sensitivity_model
        Rx_requirements_de = st.session_state.Rx_requirements
        alpha_Tx_optics = Tx_antenna_de.loc["Tx optics loss a_Tx_optics","val"] 
        P_tx = laser_source_de.loc["Tx power(avg)"]["val"]
        W_tx = Tx_antenna_de.loc["Tx radius W_Tx"]["val"]
        Z_tx = Tx_antenna_de.loc["Rayleigh range Z_Tx","val"]
        I_emit_ = ll.I_emit(P_tx,alpha_Tx_optics,W_tx)
        I_safe = 1.0e+03
        st.session_state.laser_safety.loc["Tx Pow(avg)P_Tx","val"] = P_tx
        st.session_state.laser_safety.loc["Tx optics loss a_Tx-optics","val"]  =  ll.lin_a_tx(alpha_Tx_optics)
        st.session_state.laser_safety.loc["Minimum beam radius W_Tx","val"] = W_tx
        st.session_state.laser_safety.loc["Max.emitted intensity I_emit","val"] = ll.I_emit(P_tx,alpha_Tx_optics,W_tx)
        st.session_state.laser_safety.loc["Max. permitted intensity I_safe","val"] = I_safe #define val
        st.session_state.laser_safety.loc["Safety margin M_safety","val"] =  ll.M_safety(I_emit_,I_safe)
        st.session_state.laser_safety.loc["NOHD","val"] = ll.NOHD(Z_tx,I_emit_, I_safe)
        #st.session_state.laser_safety = laser_safety_de.copy()
        
        P_tx_W = laser_source_de.loc["Tx power(avg)"]["val"]
        theta_tx = Tx_antenna_de.loc["Divergence theta_Tx","val"]
        lambda_ = laser_source_de.loc["Wavelength"]["val"]
        Z = Link_geometry_de.loc["Link distance Z"]["val"]
        theta_rx =Rx_antenna_de.loc["DL-FoV radius theta_Rx"]["val"]
        Z_tx = Tx_antenna_de.loc["Rayleigh range Z_Tx","val"]
        Z_rx = Rx_antenna_de.loc["Rayleigh range Z_Rx","val"]
        D_Rx = Rx_antenna_de.loc["Equiv. hard diameter D_Rx","val"]
        D_Tx = Tx_antenna_de.loc["Equiv. hard diameter D_Tx","val"]

        alpha = Link_geometry_de.loc["Elevation alpha at R","val"]
        H = Link_geometry_de.loc["Tx height","val"]

        r0 =  ll.Fried_param(ll.HV_func, alpha=20, H = 4e05, lambda_ = 1.55e-6)
        sigma_theta = st.session_state.Tx_pointing_error.loc["Tx pointing error standard deviation","val"]
        W_R = Tx_antenna_de.loc["Beam radius at Rx W","val"]
        sigma_00 = Rx_sensitivity_model_de.loc["Backgr.light noise sigma00","val"]
        sigma_01 = Rx_sensitivity_model_de.loc["Rx constant noise sigma01","val"]
        sigma_10 = Rx_sensitivity_model_de.loc["sigma10","val"]
        R_b = Rx_sensitivity_model_de.loc["Data rate(physical layer)","val"]
        #cal
        Tx_pointing_error = st.session_state.Tx_pointing_error.loc["Tx pointing error","val"]
        visibility =st.session_state.Clear_sky_attenuation.loc["visibility","val"]
        h_eff =st.session_state.Clear_sky_attenuation.loc["effective atmospheric thickness","val"]
        alpha_r = Link_geometry_de.loc["Elevation alpha at R","val"]
        P_tx_W =ll.W_to_dBm(P_tx_W)
        L_tx = Tx_antenna_de.loc["Tx optics loss a_Tx_optics","val"]
        G_tx = ll.Tx_gain(theta_tx)
        L_is = ll.Isotropic_space_loss(lambda_,Z)
        G_rx = ll.Rx_gain(theta_rx) 
        L_nf = ll.Near_field_loss(Z,Z_tx,Z_rx)
        #L_point = -0.6
        L_point = ll.Mean_Tx_pointing_loss(Tx_pointing_error,theta_tx)
        L_att = ll.Clear_sky_attenuation(visibility,h_eff, alpha_r,lambda_)
        L_spread = ll.Beam_spread_loss(D_Tx,D_Rx,lambda_,Z,W_R)
        P_target=Rx_requirements_de.loc["Target Rx Power[dBm]","val"]
        
        if selected_mode == "WITH AO":
            L_mean_strehl = 0.0
        else:
            L_mean_strehl = ll.SR_shortterm(D_Rx,r0)
        L_rx_opt = Rx_antenna_de.loc["Rx optics loss a_Rx_optics"]["val"]

        P_static= P_tx_W + L_tx + G_tx  +L_is + G_rx + L_nf + L_point+ L_att + L_mean_strehl + L_rx_opt
        if selected_mode == "WITH AO":
            BER_static = 0.0
        else:
            BER_static =  ll.BER_at_probe(sigma_00, sigma_01,sigma_10, P_static, lambda_,R_b)

        L_rx_opt = Rx_antenna_de.loc["Rx optics loss a_Rx_optics"]["val"]
        st.session_state.Static.loc["Tx power","val"] = P_tx_W
        st.session_state.Static.loc["Tx optics loss","val"] = L_tx
        st.session_state.Static.loc["Tx gain","val"] = G_tx 
        st.session_state.Static.loc["Isotropic space loss","val"] = L_is
        st.session_state.Static.loc["Rx gain","val"] = G_rx 
        st.session_state.Static.loc["Near-field loss","val"] = L_nf 
        st.session_state.Static.loc["Mean Tx pointing loss","val"] = L_point
        st.session_state.Static.loc["Clear-sky attenuation","val"] =L_att
        st.session_state.Static.loc["Beam-spread loss","val"] = L_spread
        st.session_state.Static.loc["Mean Rx Strehl ratio","val"] = L_mean_strehl
        st.session_state.Static.loc["Rx optics loss","val"] = L_rx_opt

        st.session_state.Static.loc["Static Rx Power","val"] = P_static
        st.session_state.Static.loc["Target Rx power","val"] = P_target
        st.session_state.Static.loc["Link margin","val"] = ll.Link_margin(P_target, P_static)
        st.session_state.Static.loc["Static BER","val"] = BER_static
        #st.session_state.Static = Static_de.copy()
        
        P_target = Rx_requirements_de.loc["Target Rx Power[dBm]","val"]
        P_fade = Rx_requirements_de.loc["Fade loss probability P_fade","val"]
        Z = Link_geometry_de.loc["Link distance Z"]["val"]
        sigma_r = ll.sigma_R(ll.HV_func,Z,lambda_)
        #sigma_i=  ll.sigma_I(sigma_r)

        sigma_eff = ll.sigma_eff(D_Rx,sigma_r,lambda_,Z)
        rho_thr =  P_fade 


        #cal
        L_tx_pointing = ll.Tx_pointing_fade_loss(P_fade,sigma_theta, theta_tx)
        L_sc = ll.Scintillation_loss(rho_thr, sigma_eff)
        D_Rx = Rx_antenna_de.loc["Equiv. hard diameter D_Rx","val"]
        r0 =  ll.Fried_param(ll.HV_func, alpha=20, H = 4e05, lambda_ = 1.55e-6)
        
        if selected_mode == "WITH AO":
            Rx_strehl = 0.0
        else:

            Rx_strehl = ll.SR_longterm(D_Rx,r0)
            #ll.Mean_Rx_Strehl_ratio(D_Rx,r0)
        P_dynamic =  L_tx_pointing + L_sc + Rx_strehl

        P_static = st.session_state.Static.loc["Static Rx Power","val"]
        P_probe = P_dynamic + P_static

        
         
        if selected_mode == "WITH AO":
            BER_probe = 0.0
        else:
            BER_probe =  ll.BER_at_probe(sigma_00, sigma_01,sigma_10, P_probe, lambda_,R_b)
        #

        #assign
        st.session_state.Dynamic_fades.loc["Tx pointing fade loss","val"] = L_tx_pointing
        st.session_state.Dynamic_fades.loc["Scintillation fade loss","val"] = L_sc
        st.session_state.Dynamic_fades.loc["Rx Strehl ratio","val"] = Rx_strehl
        st.session_state.Dynamic_fades.loc["Rx power at prob","val"] = P_probe
        st.session_state.Dynamic_fades.loc["Target Rx power","val"]  = P_target
        st.session_state.Dynamic_fades.loc["Link margin at prob","val"] = P_probe- P_target
        st.session_state.Dynamic_fades.loc["Ber at prob","val"] = BER_probe
        #st.session_state.Dynamic_fades = Dynamic_fades_de.copy()
