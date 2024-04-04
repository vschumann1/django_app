'''        

lats = [bridge.GEOGR_BREITE for bridge in all_bridges if bridge.GEOGR_BREITE is not None]
        lons = [bridge.GEOGR_LAENGE for bridge in all_bridges if bridge.GEOGR_LAENGE is not None]

        hover_texts = [
            f"LAND: {bridge.LAND}<br>EIU: {bridge.EIU}<br>REGION: {bridge.REGION}<br>NETZ: {bridge.NETZ}<br>"
            f"ANLAGEN_NR: {bridge.ANLAGEN_NR}<br>ANLAGEN_UNR: {bridge.ANLAGEN_UNR}<br>"
            f"VON_KM: {bridge.VON_KM}<br>BIS_KM: {bridge.BIS_KM}<br>VON_KM_I: {bridge.VON_KM_I}<br>"
            f"BIS_KM_I: {bridge.BIS_KM_I}<br>RIKZ: {bridge.RIKZ}<br>RIL_100: {bridge.RIL_100}<br>"
            f"STR_MEHRFACHZUORD: {bridge.STR_MEHRFACHZUORD}<br>FLAECHE: {bridge.FLAECHE}<br>"
            f"BR_BEZ: {bridge.BR_BEZ}<br>BAUART: {bridge.BAUART}<br>BESCHREIBUNG: {bridge.BESCHREIBUNG}<br>"
            f"ZUST_KAT: {bridge.ZUST_KAT}<br>WL_SERVICEEINR: {bridge.WL_SERVICEEINR}<br>Match: {bridge.Match}"
            for bridge in all_bridges
        ]

        fig = go.Figure(go.Scattermapbox(
            lat=lats,
            lon=lons,
            mode='markers',
            marker=go.scattermapbox.Marker(size=9),
            text=hover_texts,
        ))

        fig.update_layout(
            mapbox=dict(
                accesstoken='pk.eyJ1IjoiYW5ka29jaDkzIiwiYSI6ImNsMTZiNnU4dTE5MzQzY3MwZnV1NjVqOGoifQ.ZxCDeRkr59lifDEm4PIWQA',
                zoom=5,
                center=dict(lat=sum(lats) / len(lats), lon=sum(lons) / len(lons)) if lats and lons else dict(lat=0, lon=0),
                style='streets'
            ),
            margin={"r":0,"t":0,"l":0,"b":0}
        )

        '''


fields_order_and_rename = {
                'gsl_grouped_isk_2022': 'STR_NR',
                'LAND':'LAND',
                'EIU':'EIU',
                'REGION':'REGION',
                'NETZ':'NETZ',
                'ANLAGEN_NR':'ANLAGEN_NR',
                'VON_KM':'VON_KM',
                'BIS_KM':'BIS_KM',
                'VON_KM_I':'VON_KM_I',
                'BIS_KM_I':'BIS_KM_I',
                'RIKZ':'RIKZ',
                'RIL_100':'RIL_100',
                'STR_MEHRFACHZUORD':'STR_MEHRFACHZUORD',
                'LAENGE':'LAENGE',
                'ANZ_STR_GL':'ANZ_STR_GL',
                'QUERSCHN':'QUERSCHN',
                'BAUWEISE':'BAUWEISE',
                'WL_SERVICEEINR':'WL_SERVICEEINR'

            }