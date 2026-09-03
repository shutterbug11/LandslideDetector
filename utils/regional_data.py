"""
Regional geomorphic database and hotspot profiles for North East India.
Covers all 8 North Eastern states: Sikkim, Assam, Meghalaya, Arunachal Pradesh,
Nagaland, Manipur, Mizoram, and Tripura.
"""

NE_STATES = [
    "Sikkim",
    "Assam",
    "Meghalaya",
    "Arunachal Pradesh",
    "Nagaland",
    "Manipur",
    "Mizoram",
    "Tripura"
]

NE_HOTSPOTS = {
    # ----------------------------------------------------
    # SIKKIM (High Altitude Eastern Himalayas)
    # ----------------------------------------------------
    "Gangtok (East Sikkim)": {
        "state": "Sikkim",
        "lat": 27.3389,
        "lon": 88.6065,
        "elevation": 1650,
        "slope": 36.5,
        "aspect": 195.0,
        "curvature": 0.00045,
        "twi": 3.8,
        "tri": 7.8,
        "geology": "Precambrian Daling quartzites & mica schists",
        "vulnerability": "High",
        "notes": "Intense urban slope loading along NH-10 corridor."
    },
    "Mangan (North Sikkim)": {
        "state": "Sikkim",
        "lat": 27.5042,
        "lon": 88.5298,
        "elevation": 1310,
        "slope": 44.0,
        "aspect": 180.0,
        "curvature": 0.00062,
        "twi": 4.1,
        "tri": 9.2,
        "geology": "Chungthang Formation gniesses & phyllites",
        "vulnerability": "Very High",
        "notes": "Severely vulnerable to debris flows along Teesta River valley."
    },
    "Namchi (South Sikkim)": {
        "state": "Sikkim",
        "lat": 27.1667,
        "lon": 88.3667,
        "elevation": 1315,
        "slope": 31.0,
        "aspect": 160.0,
        "curvature": 0.00030,
        "twi": 3.2,
        "tri": 6.1,
        "geology": "Gondwana Sandstones and shales",
        "vulnerability": "Medium",
        "notes": "Moderate slope failures during extended monsoon showers."
    },
    "Gyalshing (West Sikkim)": {
        "state": "Sikkim",
        "lat": 27.2833,
        "lon": 88.2500,
        "elevation": 1550,
        "slope": 38.0,
        "aspect": 210.0,
        "curvature": 0.00040,
        "twi": 3.6,
        "tri": 7.4,
        "geology": "Darjeeling Gneiss group",
        "vulnerability": "High",
        "notes": "Frequent slips near Pelling-Gyalshing arterial roads."
    },
    "Chungthang (North Sikkim)": {
        "state": "Sikkim",
        "lat": 27.6039,
        "lon": 88.6475,
        "elevation": 1790,
        "slope": 48.0,
        "aspect": 175.0,
        "curvature": 0.00078,
        "twi": 4.5,
        "tri": 10.5,
        "geology": "High-grade Central Crystalline Complex",
        "vulnerability": "Critical",
        "notes": "Site of glacial lake outburst flood (GLOF) and debris avalanches."
    },

    # ----------------------------------------------------
    # MEGHALAYA (Shillong Plateau / World's Wettest Belt)
    # ----------------------------------------------------
    "Shillong (East Khasi Hills)": {
        "state": "Meghalaya",
        "lat": 25.5788,
        "lon": 91.8933,
        "elevation": 1525,
        "slope": 28.0,
        "aspect": 140.0,
        "curvature": 0.00028,
        "twi": 3.4,
        "tri": 5.2,
        "geology": "Shillong Group quartzites and conglomerates",
        "vulnerability": "Medium",
        "notes": "Urban mudslides and cut-slope failures during torrential rain."
    },
    "Cherrapunji / Sohra (East Khasi Hills)": {
        "state": "Meghalaya",
        "lat": 25.2986,
        "lon": 91.7323,
        "elevation": 1430,
        "slope": 42.0,
        "aspect": 185.0,
        "curvature": 0.00055,
        "twi": 4.9,
        "tri": 8.5,
        "geology": "Cretaceous-Tertiary sandstone and limestone scarps",
        "vulnerability": "Very High",
        "notes": "Receives world-record rainfall; dramatic escarpment rockfalls."
    },
    "Mawsynram (East Khasi Hills)": {
        "state": "Meghalaya",
        "lat": 25.2975,
        "lon": 91.5825,
        "elevation": 1400,
        "slope": 40.0,
        "aspect": 190.0,
        "curvature": 0.00052,
        "twi": 5.1,
        "tri": 8.1,
        "geology": "Shella Formation limestone and sandstones",
        "vulnerability": "Very High",
        "notes": "Extreme saturation-induced shallow rotational slides."
    },
    "Tura (West Garo Hills)": {
        "state": "Meghalaya",
        "lat": 25.5141,
        "lon": 90.2033,
        "elevation": 650,
        "slope": 32.0,
        "aspect": 220.0,
        "curvature": 0.00035,
        "twi": 3.9,
        "tri": 6.0,
        "geology": "Archaean Gneissic Complex",
        "vulnerability": "High",
        "notes": "Flash floods coupled with road embankment collapse."
    },

    # ----------------------------------------------------
    # ASSAM (Barail Range & Hill Tracts)
    # ----------------------------------------------------
    "Haflong (Dima Hasao)": {
        "state": "Assam",
        "lat": 25.1747,
        "lon": 93.0205,
        "elevation": 680,
        "slope": 37.0,
        "aspect": 165.0,
        "curvature": 0.00048,
        "twi": 4.6,
        "tri": 7.5,
        "geology": "Barail Group tertiary sandstones and weak shales",
        "vulnerability": "Critical",
        "notes": "Severely prone; severed railway link in historic 2022 landslides."
    },
    "Guwahati Hills (Kamrup Metro)": {
        "state": "Assam",
        "lat": 26.1445,
        "lon": 91.7362,
        "elevation": 180,
        "slope": 26.0,
        "aspect": 120.0,
        "curvature": 0.00022,
        "twi": 3.1,
        "tri": 4.1,
        "geology": "Precambrian granite gneisses with thick red clay overburden",
        "vulnerability": "Medium",
        "notes": "Unplanned hill slope cutting and earth cutting triggered slips."
    },
    "Diphu (Karbi Anglong)": {
        "state": "Assam",
        "lat": 25.8447,
        "lon": 93.4319,
        "elevation": 230,
        "slope": 24.0,
        "aspect": 150.0,
        "curvature": 0.00020,
        "twi": 3.3,
        "tri": 3.8,
        "geology": "Disang shales and weathered gneisses",
        "vulnerability": "Medium",
        "notes": "Shallow mudslides along interior tribal highway cuts."
    },

    # ----------------------------------------------------
    # ARUNACHAL PRADESH (Eastern Himalaya Frontal Belt)
    # ----------------------------------------------------
    "Tawang (West Kameng)": {
        "state": "Arunachal Pradesh",
        "lat": 27.5861,
        "lon": 91.8594,
        "elevation": 3048,
        "slope": 45.0,
        "aspect": 170.0,
        "curvature": 0.00065,
        "twi": 4.0,
        "tri": 9.8,
        "geology": "Higher Himalayan crystallines & schists",
        "vulnerability": "Very High",
        "notes": "Snowmelt combined with torrential monsoon triggers major slides."
    },
    "Itanagar (Papum Pare)": {
        "state": "Arunachal Pradesh",
        "lat": 27.0844,
        "lon": 93.6053,
        "elevation": 750,
        "slope": 33.0,
        "aspect": 190.0,
        "curvature": 0.00034,
        "twi": 3.7,
        "tri": 5.9,
        "geology": "Siwalik Group sandstone and unconsolidated pebble beds",
        "vulnerability": "High",
        "notes": "Weak soft rock formation prone to toe-erosion along streams."
    },
    "Bomdila (West Kameng)": {
        "state": "Arunachal Pradesh",
        "lat": 27.2645,
        "lon": 92.4159,
        "elevation": 2415,
        "slope": 41.0,
        "aspect": 180.0,
        "curvature": 0.00050,
        "twi": 3.8,
        "tri": 8.0,
        "geology": "Bomdila Gneissic complex",
        "vulnerability": "High",
        "notes": "Bhalukpong-Tawang strategic highway frequent blockage zone."
    },
    "Pasighat (East Siang)": {
        "state": "Arunachal Pradesh",
        "lat": 28.0664,
        "lon": 95.3268,
        "elevation": 155,
        "slope": 29.0,
        "aspect": 145.0,
        "curvature": 0.00029,
        "twi": 4.8,
        "tri": 5.1,
        "geology": "Siwalik sedimentary belt along Siang river",
        "vulnerability": "High",
        "notes": "Massive toe erosion by roaring Siang/Brahmaputra tributaries."
    },

    # ----------------------------------------------------
    # NAGALAND (Naga Hills / Indo-Myanmar Orogenic Belt)
    # ----------------------------------------------------
    "Kohima (NH-29 Corridor)": {
        "state": "Nagaland",
        "lat": 25.6751,
        "lon": 94.1086,
        "elevation": 1444,
        "slope": 39.0,
        "aspect": 200.0,
        "curvature": 0.00051,
        "twi": 4.3,
        "tri": 7.6,
        "geology": "Disang Flysch (crumpled splintery shales)",
        "vulnerability": "Critical",
        "notes": "Notorious sinking zone on NH-29 lifeline linking Manipur & Nagaland."
    },
    "Mokokchung (Central Nagaland)": {
        "state": "Nagaland",
        "lat": 26.3256,
        "lon": 94.5218,
        "elevation": 1325,
        "slope": 35.0,
        "aspect": 175.0,
        "curvature": 0.00038,
        "twi": 3.9,
        "tri": 6.8,
        "geology": "Barail sandstones overlying fractured Disang shales",
        "vulnerability": "High",
        "notes": "Structural weakness along active fault zones."
    },
    "Phek (Eastern Nagaland)": {
        "state": "Nagaland",
        "lat": 25.6800,
        "lon": 94.5000,
        "elevation": 1500,
        "slope": 42.0,
        "aspect": 160.0,
        "curvature": 0.00054,
        "twi": 4.1,
        "tri": 8.3,
        "geology": "Ophiolite belt and Disang flysch",
        "vulnerability": "High",
        "notes": "Deep seated translational slips during monsoon downpours."
    },

    # ----------------------------------------------------
    # MANIPUR (Manipur Hills & Imphal Valley Margins)
    # ----------------------------------------------------
    "Noney / Tupul (Railway Yard Zone)": {
        "state": "Manipur",
        "lat": 24.8167,
        "lon": 93.6000,
        "elevation": 820,
        "slope": 43.0,
        "aspect": 190.0,
        "curvature": 0.00058,
        "twi": 4.7,
        "tri": 8.9,
        "geology": "Disang shales interbedded with siltstone",
        "vulnerability": "Critical",
        "notes": "Site of catastrophic June 2022 debris avalanche (Ijei river damming)."
    },
    "Imphal Ridge Margins": {
        "state": "Manipur",
        "lat": 24.8170,
        "lon": 93.9368,
        "elevation": 786,
        "slope": 22.0,
        "aspect": 135.0,
        "curvature": 0.00018,
        "twi": 3.5,
        "tri": 3.5,
        "geology": "Alluvium with fringe Disang sandstone ridges",
        "vulnerability": "Low",
        "notes": "Valley floor is stable; surrounding peripheral ridges susceptible."
    },
    "Tamenglong (Western Manipur)": {
        "state": "Manipur",
        "lat": 24.9856,
        "lon": 93.4981,
        "elevation": 1260,
        "slope": 40.0,
        "aspect": 205.0,
        "curvature": 0.00049,
        "twi": 4.5,
        "tri": 7.9,
        "geology": "Barail series sandstone-shale sequence",
        "vulnerability": "High",
        "notes": "High rainfall catchment; frequent cut-slope collapses on hill highways."
    },

    # ----------------------------------------------------
    # MIZORAM (Lushai Hills / Anticline-Syncline Ridge System)
    # ----------------------------------------------------
    "Aizawl City (Ridge Crest)": {
        "state": "Mizoram",
        "lat": 23.7271,
        "lon": 92.7176,
        "elevation": 1132,
        "slope": 38.0,
        "aspect": 170.0,
        "curvature": 0.00045,
        "twi": 4.2,
        "tri": 7.1,
        "geology": "Surma Group (Bhuban Formation) siltstones and sandstones",
        "vulnerability": "Very High",
        "notes": "Severe slope overburden on steep dip-slopes; frequent building collapses."
    },
    "Lunglei (South Mizoram)": {
        "state": "Mizoram",
        "lat": 22.8872,
        "lon": 92.7419,
        "elevation": 722,
        "slope": 36.0,
        "aspect": 185.0,
        "curvature": 0.00039,
        "twi": 4.0,
        "tri": 6.7,
        "geology": "Upper Bhuban sandstone and shale alternation",
        "vulnerability": "High",
        "notes": "Heavy monsoonal saturation induces translational slope movements."
    },
    "Champhai (Indo-Myanmar Border)": {
        "state": "Mizoram",
        "lat": 23.4739,
        "lon": 93.3274,
        "elevation": 1320,
        "slope": 31.0,
        "aspect": 155.0,
        "curvature": 0.00032,
        "twi": 3.7,
        "tri": 5.8,
        "geology": "Bhuban siltstones with seismic jointing",
        "vulnerability": "Medium",
        "notes": "Co-seismic and rain-triggered slope cracks along border hills."
    },

    # ----------------------------------------------------
    # TRIPURA (Tertiary Anticline Hills)
    # ----------------------------------------------------
    "Jampui Hills (North Tripura)": {
        "state": "Tripura",
        "lat": 23.8200,
        "lon": 92.2700,
        "elevation": 930,
        "slope": 34.0,
        "aspect": 180.0,
        "curvature": 0.00036,
        "twi": 3.8,
        "tri": 6.3,
        "geology": "Bhuban sandstone ridges with porous orange soil",
        "vulnerability": "High",
        "notes": "Highest ridge in Tripura; heavy soil erosion and road subsidence."
    },
    "Dharmanagar (North Tripura)": {
        "state": "Tripura",
        "lat": 24.3733,
        "lon": 92.1628,
        "elevation": 60,
        "slope": 18.0,
        "aspect": 130.0,
        "curvature": 0.00015,
        "twi": 3.2,
        "tri": 2.9,
        "geology": "Tipam Sandstone and alluvium",
        "vulnerability": "Low",
        "notes": "Low undulating hillocks with occasional minor soil wash."
    }
}

SDMA_CONTACTS = {
    "Sikkim": {"helpline": "1070 / 1077", "dept": "Sikkim State Disaster Management Authority (SSDMA)", "phone": "+91-3592-201145"},
    "Meghalaya": {"helpline": "1070 / 1077", "dept": "Meghalaya State Disaster Management Authority (MSDMA)", "phone": "+91-364-2502188"},
    "Assam": {"helpline": "1070 / 1079", "dept": "Assam State Disaster Management Authority (ASDMA)", "phone": "+91-361-2237221"},
    "Arunachal Pradesh": {"helpline": "1070 / 1077", "dept": "Department of Disaster Management, GoAP", "phone": "+91-360-2212260"},
    "Nagaland": {"helpline": "1070", "dept": "Nagaland State Disaster Management Authority (NSDMA)", "phone": "+91-370-2291122"},
    "Manipur": {"helpline": "1070 / 1077", "dept": "Manipur State Disaster Management Authority (Relief & DM)", "phone": "+91-385-2443441"},
    "Mizoram": {"helpline": "1070 / 1077", "dept": "Disaster Management & Rehabilitation, GoM", "phone": "+91-389-2335842"},
    "Tripura": {"helpline": "1070", "dept": "State Disaster Management Authority, Tripura", "phone": "+91-381-2416045"}
}
