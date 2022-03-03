import os
import streamlit as st
import numpy as np
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="Criminaliteitskalender Rotterdam",
     layout="wide",
     initial_sidebar_state="expanded")

#last_month = pd.read_csv("C:/Users/rotterdam/Documents/Python scripts/meest_recente_maand_data.csv",
#                delimiter=',')['Perioden']

last_month = pd.read_csv(os.path.join(os.getcwd(), "data", "meest_recente_maand_data.csv"),
                delimiter=',')['Perioden']

last_month_rev = " ".join(last_month.values[0].split()[::-1])


#df = pd.read_csv("C:/Users/rotterdam/Documents/Python scripts/vf_pag1_alarmwaarden.csv",
#                delimiter=',').drop('Unnamed: 0', axis = 'columns')

df = pd.read_csv(os.path.join(os.getcwd(), "data", "vf_pag1_alarmwaarden.csv"),
                delimiter=',').drop('Unnamed: 0', axis = 'columns')

neighbourhoods = np.sort(df['Wijken en buurten'].unique())

st.sidebar.write("### Selecteer buurt van Rotterdam")
buurt = st.sidebar.selectbox(
    "",
    (neighbourhoods))

# Create a page dropdown 
page = st.sidebar.selectbox("Kies je analyse", ["Verleden", "Heden", "Toekomst"]) 

if page == "Verleden":
    st.title("Vorige maand: {}".format(last_month_rev))

    df_buurt_geselecteerd = df[df['Wijken en buurten'] == buurt].copy()

    df_extremen_geselecteerd = df_buurt_geselecteerd[df_buurt_geselecteerd['Afwijking t.o.v. lineaire trend'] != 'normale groei'].copy()
    df_normaal_geselecteerd = df_buurt_geselecteerd[df_buurt_geselecteerd['Afwijking t.o.v. lineaire trend'] == 'normale groei'].drop(['Wijken en buurten', 'Afwijking t.o.v. lineaire trend'], axis = 1).copy()

    df_normaal_geselecteerd['groeifactor t.o.v. zelfde maand vorig jaar'] = df_normaal_geselecteerd['groeifactor t.o.v. zelfde maand vorig jaar'] - 1

    nrows = df_extremen_geselecteerd.shape[0]

    if nrows > 0:

        columns = st.columns(nrows)

        for i in range(nrows):
            columns[i].metric(df_extremen_geselecteerd['Afwijking t.o.v. lineaire trend'].iloc[i] + ' ten opzichte van dezelfde maand vorig jaar',
                              df_extremen_geselecteerd['Soort misdrijf'].iloc[i],
                              "{:.0%} ten opzichte van dezelfde maand vorig jaar".format(df_extremen_geselecteerd['groeifactor t.o.v. zelfde maand vorig jaar'].iloc[i] - 1),
                             delta_color = 'inverse')
    else:
        st.write('Er zijn deze maand geen misdaadcategorieën met extreem afwijkende cijfers')


    def color_val(val):
        """
        Takes a scalar and returns a string with
        the css property `'color: red'` for negative
        strings, black otherwise.
        """
        if val > 0:
            color = 'red'
        else:
            color = 'green'
        return 'color: %s' % color

    with st.expander("Zie alle veelvoorkomende categorieën met normale groeicijfers"):
        st.table(df_normaal_geselecteerd.style.applymap(color_val, subset = ['groeifactor t.o.v. zelfde maand vorig jaar']).format({
        'groeifactor t.o.v. zelfde maand vorig jaar': '{:,.0%}'.format,
    }))
if page == "Heden":
    st.write('De inhoud van deze pagina moet nog ontwikkeld worden')
if page == 'Toekomst':
    st.title("Volgende maand: de criminaliteitskalender")
    st.write('De inhoud van deze pagina moet nog ontwikkeld worden')