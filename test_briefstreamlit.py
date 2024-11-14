
from datetime import datetime
from streamlit.testing.v1 import AppTest

#Permet de mettre en cache une version de l'app streamlit.
at = AppTest.from_file("briefstreamlit.py").run(timeout=15)

#test que quand l'utilisateur choisi une colonne, c'est bien elle qui s'affiche.
def test_columnname():
    
    at.selectbox[0].set_value("year").run(timeout=15)
    assert at.selectbox[0].value == "year"

#test que le vrai nombre de ligne correspond bien à celui du dataframe dans l'app.
def test_rownumbers():

    dataframe = at.dataframe[0].value
    assert len(dataframe) == 548400

#test que le vrai nombre de colonne correspond bien à celui du dataframe dans l'app.   
def test_columnnumbers():

    dataframe = at.dataframe[0].value
    assert dataframe.shape[1] == 15

#test des checkbox 
def test_checkbox(): 
    assert at.checkbox[0].value == False
    at.checkbox[0].check().run(timeout=15) 
    assert at.checkbox[0].value == True

def test_checkbox2(): 
    assert at.checkbox[1].value == False
    at.checkbox[1].check().run(timeout=15) 
    assert at.checkbox[1].value == True
  
def test_checkbox3(): 
    assert at.checkbox[2].value == False
    at.checkbox[2].check().run(timeout=15) 
    assert at.checkbox[2].value == True 

#test le text_input
def test_car(): 
    at.text_input[0].set_value("toyota").run(timeout=15)
    assert at.text_input[0].value == "toyota"

#test si les valeurs min et max du dataframe sont bonne,
#ainsi que la fonctionalité du slider.
def test_price():
    at.slider[1].set_value((1,230000)).run(timeout=15)
    result_df = at.dataframe[0].value
    min = result_df["sellingprice"].min()
    max = result_df["sellingprice"].max()
    assert min >= 1
    assert max <= 230000
    assert at.slider[1].value[0] == 1
    assert at.slider[1].value[1] == 230000

#test si le date_input marche et donnes les bonnes dates min et max.
def test_date():
    at.selectbox[0].set_value("saledate").run(timeout=15)
    start_date = datetime(2014,1,1)
    end_date = datetime(2015,7,21)
    at.date_input[0].set_value((start_date, end_date)).run(timeout=15)
    result_df = at.dataframe[0].value
    assert result_df["saledate"].min() >= start_date
    assert result_df["saledate"].max() <= end_date
    