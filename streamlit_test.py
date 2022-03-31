import os
import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
from datetime import date

st.set_page_config(
    page_title="Criminaliteitskalender Rotterdam",
     layout="wide",
     initial_sidebar_state="expanded")

last_month = pd.read_csv(os.path.join(os.getcwd(), "data", "meest_recente_maand_data.csv"),
                delimiter=',')['Perioden']

next_month_number = date.today().month
current_year = date.today().year

last_month_rev = " ".join(last_month.values[0].split()[::-1])

df = pd.read_csv(os.path.join(os.getcwd(), "data", "vf_pag1_alarmwaarden.csv"),
                delimiter=',').drop('Unnamed: 0', axis = 'columns')

df_seasonal = pd.read_csv(os.path.join(os.getcwd(), "data", 'maandafwijkingen_misdaad.csv'),
                delimiter=',').drop('Unnamed: 0', axis = 'columns')

neighbourhoods = np.sort(df['Wijken en buurten'].unique())

st.sidebar.write("### Selecteer buurt van Rotterdam")
buurt = st.sidebar.selectbox(
    "",
    (neighbourhoods))

# Create a page dropdown 
page = st.sidebar.selectbox("Kies je analyse", ["Verleden", "Toekomst"]) 

if page == "Verleden":
    st.title("Vorige maand: {}".format(last_month_rev))

    df_buurt_geselecteerd = df[df['Wijken en buurten'] == buurt].copy()

    df_extremen_geselecteerd = df_buurt_geselecteerd[df_buurt_geselecteerd['Afwijking t.o.v. lineaire trend'] != 'normale groei'].copy()
    df_normaal_geselecteerd = df_buurt_geselecteerd[df_buurt_geselecteerd['Afwijking t.o.v. lineaire trend'] == 'normale groei'].drop(['Wijken en buurten', 'Afwijking t.o.v. lineaire trend'], axis = 1).copy().set_index('Soort misdrijf')

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

    with st.expander("Benieuwd naar categorieën met normale groeicijfers?"):
        st.table(df_normaal_geselecteerd.style.applymap(color_val, subset = ['groeifactor t.o.v. zelfde maand vorig jaar']).format({
        'groeifactor t.o.v. zelfde maand vorig jaar': '{:,.0%}'.format,
       }))
# if page == "Heden":
#     st.write('De inhoud van deze pagina moet nog ontwikkeld worden')
if page == 'Toekomst':
    
    df_seasonal_buurt_geselecteerd = df_seasonal[df_seasonal['Wijken en buurten'] == buurt].copy()
    
    next_month_number =date.today().month
    month_order_list = df_seasonal_buurt_geselecteerd['Maand'].unique()
    next_month_name = month_order_list[next_month_number]
    months_in_order = np.append(month_order_list[next_month_number+1:], month_order_list[:next_month_number])
    
    st.title("Volgende maand: {} {}".format(next_month_name, current_year))
    
    columns_next_month = st.columns(3)
    
    df_seasonal_subset_next_month = df_seasonal_buurt_geselecteerd[df_seasonal_buurt_geselecteerd['Maand'] == next_month_name].replace([np.inf, -np.inf], np.nan).dropna().sort_values('pct_tov_mediaan', ascending = False)
    
    for i in range(3):
                    columns_next_month[i].metric('',
                              df_seasonal_subset_next_month['Soort misdrijf'].iloc[i],
                              "{:.0%} ten opzichte van het jaargemiddelde".format(df_seasonal_subset_next_month['pct_tov_mediaan'].iloc[i]),
                             delta_color = 'inverse')
            
    if st.checkbox("Wil je verder vooruit kijken?"):

        for month in months_in_order:
             with st.expander("{}".format(month)):
                df_seasonal_subset = df_seasonal_buurt_geselecteerd[df_seasonal_buurt_geselecteerd['Maand'] == month].replace([np.inf, -np.inf], np.nan).dropna().sort_values('pct_tov_mediaan', ascending = False)

                nrows_seasonal_subset = df_seasonal_subset.shape[0]

                if nrows_seasonal_subset > 0:

    #                 Tijdelijk negeren we het aantal rijen en gebruiken we 3 rijen als maximale input
                    columns_calendar = st.columns(3)

                    for i in range(3):
                        columns_calendar[i].metric('',
                                  df_seasonal_subset['Soort misdrijf'].iloc[i],
                                  "{:.0%} ten opzichte van het jaargemiddelde".format(df_seasonal_subset['pct_tov_mediaan'].iloc[i]),
                                 delta_color = 'inverse')

