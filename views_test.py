# myapp/views.py
'''
# myapp/views.py

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import GSL_grouped_ISK_2022, bruecken_ISK_2022, tunnel_ISK_2022, weichen_ISK_2022, stuetzauwerke_ISK_2022, schallschutzwaende_ISK_2022, bahnuebergaenge_ISK_2022, stationen_ISK_2022 
from django.core.paginator import Paginator
from .filters import GSLFilter
import plotly.express as px
import plotly.graph_objects as go
import json
import pandas as pd
import csv
from django.utils.safestring import mark_safe
import numpy as np
from .forms import MultiSelectFilterForm 
from django.db.models import Sum


mapbox_access_token = 'pk.eyJ1IjoiYW5ka29jaDkzIiwiYSI6ImNsMTZiNnU4dTE5MzQzY3MwZnV1NjVqOGoifQ.ZxCDeRkr59lifDEm4PIWQA'




def get_model_fields(model):
    return [field for field in model._meta.get_fields() if field.concrete and not field.name.startswith('_')]


##def analysis(request):
#    return render(request, 'myapp/analysis.html')
def analysis_view(request):
    filters = GSLFilter(request.GET, queryset=GSL_grouped_ISK_2022.objects.all())
    gsllist = filters.qs

    model_data = {}
    streckennummer = request.GET.get('STR_NR', '')
    counts = {}
    sums = {}

    form = MultiSelectFilterForm(request.GET or None)

    option_to_model = {
        'Brücken': bruecken_ISK_2022,
        'Tunnel': tunnel_ISK_2022,
        'Weichen': weichen_ISK_2022,
        'Stützbauwerke': stuetzauwerke_ISK_2022,
        'Schallschutzwände': schallschutzwaende_ISK_2022,
        'Bahnübergänge': bahnuebergaenge_ISK_2022
    }

    if form.is_valid():
        selected_options = form.cleaned_data['selected_options']
        selected_bundeslaender = form.cleaned_data['selected_bundeslaender']

        filtered_ids = gsllist.values_list('STR_NR', flat=True)

        for option, model in option_to_model.items():
            if option in selected_options:
                queryset = model.objects.filter(gsl_grouped_isk_2022__STR_NR__in=filtered_ids)
                if selected_bundeslaender:
                    queryset = queryset.filter(LAND__in=selected_bundeslaender)

                counts[option] = queryset.count()

                # Calculate sums for specific columns based on the model
                if option == 'Brücken':
                    sums['Fläche Brücken'] = queryset.aggregate(Sum('FLAECHE'))['FLAECHE__sum'] or 0
                elif option in ['Tunnel', 'Stützbauwerke', 'Schallschutzwände']:
                    sum_key = f'Länge {option}'
                    sums[sum_key] = queryset.aggregate(Sum('LAENGE'))['LAENGE__sum'] or 0

                fields = [field.name for field in model._meta.fields if field.name != 'geometry']
                paginator = Paginator(queryset, 5)
                page_number = request.GET.get(f'page_{option}')
                page_obj = paginator.get_page(page_number)

                model_data[option] = {'page_obj': page_obj, 'fields': fields}



    if 'download-csv' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="filtered_data.csv"'

        writer = csv.writer(response)
        fields = [field for field in GSL_grouped_ISK_2022._meta.get_fields() if field.concrete]
        writer.writerow([field.name for field in fields])

        for obj in gsllist:
            writer.writerow([getattr(obj, field.name) for field in fields])

        return response

    if 'download-excel' in request.GET:
        df = pd.DataFrame(list(gsllist.values(*[field.name for field in GSL_grouped_ISK_2022._meta.get_fields() if field.concrete])))
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="filtered_data.xlsx"'
        df.to_excel(response, index=False)

        return response

    all_bridges = bruecken_ISK_2022.objects.filter(gsl_grouped_isk_2022__in=gsllist).distinct()


    if all_bridges.exists():
        #hover_text_bu = df_bu_new.apply(lambda row: f"REGION: {row['REGION']}<br>NETZ: {row['NETZ']}<br>STR_NR: {row['STR_NR']}<br>LAGE_KM: {row['LAGE_KM']}<br>BAUFORM: {row['BAUFORM']}", axis=1)
            
        # Für Brücken (df_br_new)
        hover_text_br = [
            f"LAND: {bridge.LAND}<br>EIU: {bridge.EIU}<br>REGION: {bridge.REGION}<br>NETZ: {bridge.NETZ}<br>"
            f"ANLAGEN_NR: {bridge.ANLAGEN_NR}<br>ANLAGEN_UNR: {bridge.ANLAGEN_UNR}<br>"
            f"VON_KM: {bridge.VON_KM}<br>BIS_KM: {bridge.BIS_KM}<br>VON_KM_I: {bridge.VON_KM_I}<br>"
            f"BIS_KM_I: {bridge.BIS_KM_I}<br>RIKZ: {bridge.RIKZ}<br>RIL_100: {bridge.RIL_100}<br>"
            f"STR_MEHRFACHZUORD: {bridge.STR_MEHRFACHZUORD}<br>FLAECHE: {bridge.FLAECHE}<br>"
            f"BR_BEZ: {bridge.BR_BEZ}<br>BAUART: {bridge.BAUART}<br>BESCHREIBUNG: {bridge.BESCHREIBUNG}<br>"
            f"ZUST_KAT: {bridge.ZUST_KAT}<br>WL_SERVICEEINR: {bridge.WL_SERVICEEINR}<br>Match: {bridge.Match}"
            for bridge in all_bridges
        ]


        # Für Tunnel (df_tu_new)
        #hover_text_tu = df_tu_new.apply(lambda row: f"REGION: {row['REGION']}<br>NETZ: {row['NETZ']}<br>STR_NR: {row['STR_NR']}<br>VON_KM: {row['VON_KM']}<br>BIS_KM: {row['BIS_KM']}<br>LAENGE: {row['LAENGE']}<br>BAUWEISE: {row['BAUWEISE']}", axis=1)

        #hover_text_strecke = df_isk_GSL_new.apply(lambda row: f"REGION: {row['REGION']}<br>NETZ: {row['NETZ']}<br>STR_NR: {row['STR_NR']}<br>VON_KM: {row['VON_KM']}<br>BIS_KM: {row['BIS_KM']}<br>LAENGE: {row['LAENGE']}", axis=1)

        #hover_text_weiche = df_isk_weichen_new.apply(lambda row: f"REGION: {row['REGION']}<br>NETZ: {row['NETZ']}<br>STR_NR: {row['STR_NR']}<br>LAGE_KM: {row['LAGE_KM']}", axis=1)



        fig = go.Figure()

        # Datainklusion 4 

        # Datainklusion 2

        fig.add_trace(go.Scattermapbox(
            lat=[bridge.GEOGR_BREITE for bridge in all_bridges if bridge.GEOGR_BREITE is not None],
            lon = [bridge.GEOGR_LAENGE for bridge in all_bridges if bridge.GEOGR_LAENGE is not None],
            mode='markers',
            marker=dict(size=7, color='#006587'),
            hoverinfo='text',
            hovertext=hover_text_br,
            name='Brücken',
            showlegend=True,
        ))




        # Datainklusion 3 

        # Calculate the mean of the latitudes and longitudes
        lat1 = np.mean([bridge.GEOGR_BREITE for bridge in all_bridges if bridge.GEOGR_BREITE is not None])
        lon1 = np.mean([bridge.GEOGR_LAENGE for bridge in all_bridges if bridge.GEOGR_LAENGE is not None])

        # Continue with updating the layout and showing the figure as before
        fig.update_layout(
            mapbox=dict(
                accesstoken=mapbox_access_token,
                center={"lat": lat1, "lon": lon1},
                zoom=5.5,
                style='outdoors'
            ),
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99
            ),
            title="Geoplot Strecken, Weichen, Bahnübergänge, Brücken und Tunnel",
            title_font=dict(color='#003366', size=24),
            title_x=0.5,
            margin=dict(b=40),
        )

        
        # COPY for later 


        fig.update_layout(
        mapbox=dict(
        accesstoken=mapbox_access_token,
        center={"lat": lat1, "lon": lon1},
        zoom=9.0,
        style='outdoors'
        ),
        legend=dict(
        font=dict(
            size=20  
        )
        ),

        
        #Slider für Zoom
        
        sliders=[dict(
        active=4,
        currentvalue={
            "prefix": "Zoom: ",
            "visible": False,
            "xanchor": "right",
            "font": {
                "size": 20,
                "color": "black"
            }
        },
        pad={"t": 50},
        steps=[
            dict(method='relayout', args=['mapbox.zoom', 2], label = "Rauszoomen"),
            dict(method='relayout', args=['mapbox.zoom', 3], label = ""),
            dict(method='relayout', args=['mapbox.zoom', 4], label = ""),
            dict(method='relayout', args=['mapbox.zoom', 5], label = ""),
            dict(method='relayout', args=['mapbox.zoom', 6], label = ""),
            dict(method='relayout', args=['mapbox.zoom', 7], label = ""),
            dict(method='relayout', args=['mapbox.zoom', 8], label = ""),
            dict(method='relayout', args=['mapbox.zoom', 9], label = ""),
            dict(method='relayout', args=['mapbox.zoom', 10], label = "Reinzoomen"),
        ],
        x=0.05,
        xanchor="left",
        len=0.9,
        y=-0.035,
        yanchor="bottom",
        bgcolor="#006587",  # Slider background color
        activebgcolor="#AAD228",  # Slider background color when active
        tickwidth=7,
        ticklen = 0,
        bordercolor="white",  # Slider border color
        borderwidth=2,  # Slider border width
        font=dict(size=15, color="#006587"),

        )],
        
        # Title-Bezeichnung
        
        showlegend=True,
        title_text="Geoplot Strecken, Weichen, Bahnübergänge, Brücken und Tunnel",
        title_font=dict(size=24, color="#003366"),
        title_pad=dict(t=20, b=20),
        
        # Dropdown für Map-Ansicht
        updatemenus=[dict(
        buttons=[
            dict(args=[{"mapbox.style": "outdoors"}],
                label="Outdoors",
                method="relayout"),
            dict(args=[{"mapbox.style": "satellite"}],
                label="Satellite",
                method="relayout"),
            dict(args=[{"mapbox.style": "light"}],
                label="Hell",
                method="relayout"),
            dict(args=[{"mapbox.style": "dark"}],
                label="Dunkel",
                method="relayout"),
            dict(args=[{"mapbox.style": "streets"}],
                label="Straße",
                method="relayout"),
            dict(args=[{"mapbox.style": "satellite-streets"}],
                label="Satellite mit Straßen",
                method="relayout"),
        ],
        direction="down",
        pad={"r": 10, "t": 10},
        showactive=True,
        x=1,
        xanchor="right",
        y=1.1,
        yanchor="top",
        bgcolor="#001C4F",
        font=dict(size=15, color="white")  
        )]
        )



        plot_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
    else:
        no_data_message = "Für diese Streckennummer ist keine Geo-Visualisierung verfügbar."
        plot_html = mark_safe(f"<div style='text-align: center; padding: 20px;'>{no_data_message}</div>")

    paginator = Paginator(gsllist, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

     # Retrieve the list of columns to exclude from the request
    exclude_columns = ['geometry']



    # Filter out the excluded columns
    fields = [field for field in GSL_grouped_ISK_2022._meta.get_fields() if field.concrete and field.name not in exclude_columns]

    #print("Model data:", model_data)

    context = {
        'page_obj': page_obj,
        'fields': fields,
        'filters': filters,
        'plot_html': plot_html,
        'form': form,
        'model_data': model_data,
        'streckennummer': streckennummer,
        'counts': counts,
        'sums': sums,
    }


    return render(request, 'myapp/analysis.html', context)


def hlk_view(request):
    data = [
        {'lat': 40.7128, 'lon': -74.0060, 'name': 'New York'},
        {'lat': 34.0522, 'lon': -118.2437, 'name': 'Los Angeles'},
        # Add more data points as needed
    ]

    # Convert your data into a DataFrame or use your existing DataFrame
    df = pd.DataFrame(data)

    # Create a Plotly Express map
    fig = px.scatter_geo(df,
                         lat='lat',
                         lon='lon',
                         hover_name='name',  # Displays the 'name' value on hover
                         projection="natural earth")

    # Convert the figure to HTML and JavaScript code
    plot_div = fig.to_html(full_html=False)

    # Pass the plot to the template
    context = {'plot_div': plot_div}
    return render(request, 'myapp/hlk.html', context)

def main_view(request):
    return render(request, 'myapp/main.html')

def geo_view(request):
    return render(request, 'myapp/geo.html')

def pb_view(request):
    stations_list = stationen_ISK_2022.objects.all()
    paginator = Paginator(stations_list, 10)  # Show 10 stations per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'myapp/personenbahnhoefe.html', {'page_obj': page_obj})

def station_detail(request, station_number):
    station = get_object_or_404(stationen_ISK_2022, number=station_number)
    return render(request, 'myapp/pb_detail.html', {'station': station})





'''