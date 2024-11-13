#main

import pandas as pd
import streamlit as st

from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

df = pd.read_csv('car_sales2.csv', delimiter=',',encoding='utf-8')

result = df

st.sidebar.header("Filter Options")

#AJOUTE CASE SOUS FORME DE CHECKBOX
modify = st.sidebar.checkbox("Add filters and chose order")

#CONVERTI LES DATES AU BON FORMAT, DE OBJET A DATETIME
#.dt.tz_localize(None) RENDS LES TIMEZONES NAIVES
df["saledate"] = pd.to_datetime(df["saledate"]).dt.tz_localize(None)

#CONVERTI LA COLONNE MAKE AU FORMAT CATEGORY
df["make"] = df["make"].astype("category")

print(df.info())

#FUNCTION POUR AJOUTER UN FILTRE FABRIQUANT ET MODELE
def make_model(df,option,int_filtered_value,asc):
    
    #ON DEFINI LES VARIABLES POUR LE SLIDER DES PRIX
                min_value = int(min(df["sellingprice"]))
                max_value = int(max(df["sellingprice"]))
    #SLIDER DES PRIX
                price = st.sidebar.slider("select price range",min_value = min_value, max_value=max_value, value=(min_value,max_value))
    #FILTRE DES PRIX 
                price_filtered_value = (df["sellingprice"] >= price[0]) & (df["sellingprice"] <= price[1])
    
    #PRENDS UN TEXTE EN ENTREE
                maker = st.sidebar.text_input("choose maker")
    #UTILISE ISIN() POUR TROUVER LE FABRIQUANT DANS SA COLONNE    RETOURNE LISTE DE BOOLEEN     
                filter_make = df["make"].isin([maker.lower()])
    #ESPERLUETTE (&) COMBINE LES LISTES DE BOOLEEN        
                all = filter_make & int_filtered_value & price_filtered_value
    #UTILISE (loc[]) POUR CREER UNE NOUVELLE DATAFRAME SELON LE FILTRE     RETOURNE LISTE D'OBJET 
                make_finder = df.loc[all,:]
    #UTILISE (sort_values) AFIN DE TRIER SELON LA COLONNE ET L'ORDRE CHOISI
                result = make_finder.sort_values(option, ascending=asc)
        #CHECKBOX POUR DECIDER D'APPLIQUER FILTRE POUR LE MODELE   RETOURNE TRUE OU FALSE  
                model=st.sidebar.checkbox("model filter")
        #CONDITIONELLE (IF) QUI PERMET OU NON LE FILTRAGE PAR MODELE         
                if model :  
            #(unique()) APPLIQUER AU FILTRE DES FABRIQUANTS AFIN D'ISOLER LES MODELES PROPRES AU FABRIQUANT
            #RETOURNE LISTE DE MODELES
                    model_uni = make_finder["model"].unique()
            #(MULTISELECT) OFFRE LE CHOIX DE FILTRER PLUSIEURS MODELE EN MEME TEMPS
                    model = st.sidebar.multiselect("choose model",model_uni)
                    model_filter = df["model"].isin(model)
            #RAJOUTE LE FILTRE MODELE      
                    all = all & model_filter & price_filtered_value
                    make_finder = df.loc[all,:]
                    result = make_finder.sort_values(option, ascending=asc)   
            #ELSE QUI RESTAURE LE BON FILTRE
                else :
                    all = (filter_make & int_filtered_value) & price_filtered_value
                    make_finder = df.loc[all,:]
                    result = make_finder.sort_values(option, ascending=asc) 
                return(result)

#APPLIQUE CONDITION SI CHECKBOX EST (TRUE)
if modify :

    asc = st.sidebar.checkbox("Ascending order")
    option = st.sidebar.selectbox("chose a category",(df.columns)) 
    modify2 = st.sidebar.checkbox("Chose two columns to compare")
#APPLIQUE CONDITION SI CHECKBOX EST (TRUE) POUR AGGREGATION    
    if modify2 :
    #CREATION DES DATFRAMES QUANTITATIVE ET QUALITATIVE    
        newdf = df.select_dtypes(include=['int64', 'float64']).columns
        newdf2 = df.select_dtypes(include=['category', 'object']).columns
    
        group_columns = st.sidebar.multiselect("Choose categorical columns to group by", newdf2)
        agg_columns = st.sidebar.multiselect('Choose numeric columns for aggregation', newdf)
    #SI LES DEUX COLONNES RESEIGNER..    
        if agg_columns and group_columns:
    #..AGGREGATION
            grouped_df = df.groupby(group_columns)[agg_columns].agg(['mean', 'sum', 'min', 'max'])
            grouped_df = grouped_df.sort_values(by=group_columns, ascending=asc)
            st.write(grouped_df)  
       
    make=st.sidebar.checkbox("more filters")
#SI COLONNE NUMERIQUE    
    if pd.api.types.is_numeric_dtype(df[option]) | pd.api.types.is_float_dtype(df[option]):
        min_value = int(min(df[option]))
        max_value = int(max(df[option]))
        step1 = max(1, (max_value - min_value) // 100)
        value1 = st.slider("select value",min_value,max_value,step=step1,value=(min_value, max_value))
    #FILTRE EN RAPPORT AVEC LA RANGEE CHOISI   
        int_filtered_value = (df[option] >= value1[0]) & (df[option] <= value1[1])
    #APPLIQUE CONDITION SI CHECKBOX EST (TRUE)
        if make :
    #APPLIQUE FUNCTION        
            result = make_model(df,option,int_filtered_value,asc)  
    #SINON NE PREND QUE VALEURS DE FILTRE RESEIGNER PLUS HAUT (int_filtered_value)                  
        else :
            make_finder = df.loc[int_filtered_value,:]
            result = make_finder.sort_values(option, ascending=asc)
    #MEME CHOSE POUR LES DATES        
    elif pd.api.types.is_datetime64_any_dtype(df[option]):
        min_value = df[option].min()
        max_value = df[option].max()
        date_value = st.date_input("date",value=(min_value.date(), max_value.date()), min_value=min_value.date(), max_value=max_value.date())
       #VERIFICATION QU'IL Y A BIEN DEUX DATES
        if isinstance(date_value, tuple) and len(date_value) == 2:
            start_date, end_date = date_value
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)
            date_filter = (df[option] >= start_date) & (df[option] <= end_date)
            date_finder = df.loc[date_filter,:]
            result = date_finder.sort_values(option, ascending=asc)
        else :
            pass
        if make :
           result = make_model(df,option,date_filter,asc)
    #MEME CHOSE POUR LES OBJET,CATEGORIE
    else :
        uni = df[option].unique()
        sel = st.sidebar.multiselect("chose",uni)
        filt = df[option].isin(sel)
        res = df.loc[filt,:]
        result = res.sort_values(option, ascending=asc)
    
        if make :
           result = make_model(df,option,filt,asc)         

else:
    pass
    
st.write(result)

#BOUTON TELECHARGEMENT
st.download_button(
   label = "Download csv", 
   data = result.to_csv().encode("utf-8"),
   file_name = "cardataframe.csv",
   mime = "text/csv"
)
