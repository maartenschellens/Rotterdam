import os
import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
from datetime import date

def get_chart(data):
    hover = alt.selection_single(
        fields=["Datum"],
        nearest=True,
        on="mouseover",
        empty="none",
    )

    lines = (
        alt.Chart(data, title="Test")
        .mark_line()
        .encode(
            x="Datum",
            y="Geregistreerde misdrijven (aantal)",
            color="Soort misdrijf",
            strokeDash="Soort misdrijf"
        )
    )

    # Draw points on the line, and highlight based on selection
    points = lines.transform_filter(hover).mark_circle(size=65)

    # Draw a rule at the location of the selection
    tooltips = (
        alt.Chart(data)
        .mark_rule()
        .encode(
            x="Datum",
            y="Geregistreerde misdrijven (aantal)",
            opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
            tooltip=[
                alt.Tooltip("Datum", title="datum"),
                alt.Tooltip("Geregistreerde misdrijven (aantal)", title="aantal misdrijven"),
            ],
        )
        .add_selection(hover)
    )

    return (lines + points + tooltips).interactive()

st.set_page_config(
    page_title="Criminaliteitskalender Rotterdam",
     layout="wide",
     initial_sidebar_state="expanded")

last_month = pd.read_csv(os.path.join(os.getcwd(), "data", "meest_recente_maand_data.csv"),
                delimiter=',')['Perioden']

number_month_dict = {1:'januari',
                                                      2: 'februari',
                                                      3: 'maart',
                                                      4: 'april',
                                                      5: 'mei',
                                                      6: 'juni',
                                                      7: 'juli',
                                                      8: 'augustus',
                                                      9: 'september',
                                                      10: 'oktober',
                                                      11: 'november',
                                                      12: 'december'}

df_ts = pd.read_csv(os.path.join(os.getcwd(), "data", "misdaad_input_correct_dates.csv"),
                delimiter=',')

unieke_jaren = df_ts.groupby(pd.to_datetime(df_ts['Datum']).dt.year)['Datum'].max().values

next_month_number = date.today().month
current_year = date.today().year

last_month_rev = " ".join(last_month.values[0].split()[::-1])

df = pd.read_csv(os.path.join(os.getcwd(), "data", "vf_pag1_alarmwaarden.csv"),
                delimiter=',').drop('Unnamed: 0', axis = 'columns')

df_seasonal = pd.read_csv(os.path.join(os.getcwd(), "data", 'maandafwijkingen_misdaad.csv'),
                delimiter=',').drop('Unnamed: 0', axis = 'columns')

gebieden_gesorteerd = list(np.sort(df[df['Wijken en buurten'].str.contains('Gebied')]['Wijken en buurten'].unique()))
buurten_gesorteerd = list(np.sort(df[~df['Wijken en buurten'].str.contains('Gebied|Gemeente')]['Wijken en buurten'].unique()))

buurten = ['Rotterdam (Gemeente)'] + gebieden_gesorteerd + buurten_gesorteerd

# Create a page dropdown
st.sidebar.write("### Selecteer de analyse")
page = st.sidebar.selectbox("", ["Verleden", "Toekomst"]) 

st.sidebar.write("### Selecteer een gebied")
buurt = st.sidebar.selectbox(
    "",
    buurten)

if page == "Verleden":
    st.title("Vorige maand: {}".format(last_month_rev))


    df_buurt_geselecteerd = df[df['Wijken en buurten'] == buurt].copy()


    df_extremen_geselecteerd = df_buurt_geselecteerd[df_buurt_geselecteerd['Afwijking t.o.v. lineaire trend'] != 'normale groei'].sort_values(by=['groeifactor t.o.v. zelfde maand vorig jaar'], ascending = False).copy()
                                                                                                                                              
    df_normaal_geselecteerd = df_buurt_geselecteerd[df_buurt_geselecteerd['Afwijking t.o.v. lineaire trend'] == 'normale groei'].drop(['Wijken en buurten', 'Afwijking t.o.v. lineaire trend'], axis = 1).copy().set_index('Soort misdrijf')

    df_normaal_geselecteerd['groeifactor t.o.v. zelfde maand vorig jaar'] = df_normaal_geselecteerd['groeifactor t.o.v. zelfde maand vorig jaar'] - 1

    nrows = df_extremen_geselecteerd.shape[0]

    if nrows > 0:

        columns = st.columns(nrows)

        for i in range(nrows):
            columns[i].metric(df_extremen_geselecteerd['Afwijking t.o.v. lineaire trend'].iloc[i] + ' ({} t.o.v. {} in zelfde maand vorig jaar)'.format(int(df_extremen_geselecteerd['Aantal deze maand dit jaar'].iloc[i]), int(df_extremen_geselecteerd['Aantal deze maand vorig jaar'].iloc[i])),
                              df_extremen_geselecteerd['Soort misdrijf'].iloc[i],
                              "{:.0%} ten opzichte van dezelfde maand vorig jaar".format(df_extremen_geselecteerd['groeifactor t.o.v. zelfde maand vorig jaar'].iloc[i] - 1),
                             delta_color = 'inverse')
            
        with st.expander("Benieuwd naar de langetermijnontwikkeling?"):
    
            symbols = st.multiselect("Kies een categorie om te visualiseren", df_extremen_geselecteerd['Soort misdrijf'], df_extremen_geselecteerd['Soort misdrijf'])

            source = df_ts[(df_ts['Soort misdrijf'].isin(symbols)) & (df_ts['Wijken en buurten'] == buurt)]
            chart = get_chart(source)
            st.altair_chart(chart.encode(alt.X('Datum:Q',
                  axis=alt.Axis(values = unieke_jaren, labelAngle=-45))), use_container_width=True)
        
        
    else:
        st.write('Er waren vorige maand geen misdaadcategorieën met extreem afwijkende cijfers')
    
    

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
            'Aantal deze maand dit jaar': int,
            'Aantal deze maand vorig jaar': int}))
# if page == "Heden":
#     st.write('De inhoud van deze pagina moet nog ontwikkeld worden')
if page == 'Toekomst':
    
    df_seasonal_buurt_geselecteerd = df_seasonal[df_seasonal['Wijken en buurten'] == buurt].copy()
    
    next_month_number =date.today().month
    next_month_name = number_month_dict[next_month_number+1]
    months_in_order = np.append(list(number_month_dict.values())[next_month_number+1:], list(number_month_dict.values())[:next_month_number])
    
    st.title("Volgende maand: {} {}".format(next_month_name, current_year))
    
    
    
    df_seasonal_subset_next_month = df_seasonal_buurt_geselecteerd[df_seasonal_buurt_geselecteerd['Maand'] == next_month_name].replace([np.inf, -np.inf], np.nan).dropna().sort_values('Percentage verschil', ascending = False)
    
    if len(df_seasonal_subset_next_month) > 0:
        if len(df_seasonal_subset_next_month) > 3:
            num_columns1 = 3
        else:
            num_columns1 = len(df_seasonal_subset_next_month)
            
        columns_next_month = st.columns(num_columns1)
        
        for i in range(num_columns1):
                        columns_next_month[i].metric('',
                                  df_seasonal_subset_next_month['Soort misdrijf'].iloc[i],
                                  "{:.0%} ten opzichte van het jaargemiddelde".format(df_seasonal_subset_next_month['Percentage verschil'].iloc[i]),
                                 delta_color = 'inverse')
                
    else:
        st.write('Er zijn volgende maand geen verwachte seizoenseffecten in {}'.format(buurt))

    if st.checkbox("Wil je verder vooruit kijken?"):

        for month in months_in_order:
            
            if len(df_seasonal_buurt_geselecteerd[df_seasonal_buurt_geselecteerd['Maand'] == month]) == 0:
                st.write('{} heeft geen verwachte seizoenseffecten'.format(month))
            
            else:
                 with st.expander("{}".format(month)):
                    df_seasonal_subset = df_seasonal_buurt_geselecteerd[df_seasonal_buurt_geselecteerd['Maand'] == month].replace([np.inf, -np.inf], np.nan).dropna().sort_values('Percentage verschil', ascending = False)

                    nrows_seasonal_subset = df_seasonal_subset.shape[0]

                    if nrows_seasonal_subset > 0:
                        if len(df_seasonal_subset) > 3:
                            num_columns2 = 3                    
                        else:
                            num_columns2 = len(df_seasonal_subset)
                            
                        columns_calendar = st.columns(num_columns2)

                        for i in range(num_columns2):
                            columns_calendar[i].metric('',
                                      df_seasonal_subset['Soort misdrijf'].iloc[i],
                                      "{:.0%} ten opzichte van het jaargemiddelde".format(df_seasonal_subset['Percentage verschil'].iloc[i]),
                                     delta_color = 'inverse')

