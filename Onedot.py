#!/usr/bin/env python
# coding: utf-8

# In[1]:


#import libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pandas.plotting import register_matplotlib_converters
import pandas_profiling as pp
from deep_translator import GoogleTranslator
from geopy.geocoders import Nominatim
import numpy as np


# In[2]:


target = pd.read_excel('Target Data.xlsx')
target.head()


# In[3]:


target.shape


# In[ ]:





# ### Data Profiling

# In[4]:


data = pd.read_json('supplier_car.json', lines=True, encoding='utf-8')
data.head()


# In[5]:


data['Attribute Names'].unique()


# In[6]:


data['Attribute Values'].unique()


# In[7]:


data.shape


# In[8]:


data.dtypes


# In[9]:


cat_vars = data.select_dtypes(include='object')
data[cat_vars.columns] = data.select_dtypes(['object']).apply(lambda x: x.astype('category'))
data.dtypes


# In[ ]:





# In[ ]:





# #### Missing values

# In[10]:


data.isna().sum()


# In[11]:


data.isna().sum().reset_index(name="n").plot.bar(x='index', y='n', rot=45)


# ### Data distribution
# 

# #### Numeric variables

# In[12]:


register_matplotlib_converters()
data.describe()


# In[13]:


data.boxplot(rot=45)
plt.show()


# In[14]:


#pp.ProfileReport(data)


# ### Pre processing

# In[15]:


target_cols_aux = data['Attribute Names'].unique()
target_cols = ['MakeText','TypeName','TypeNameFull','ModelText','ModelTypeText']

for x in target_cols_aux:
    target_cols.append(x)
target_cols


# In[16]:


target_df = pd.DataFrame(columns = target_cols)
target_df


# In[17]:


target_df = data.reset_index().groupby(['ID','Attribute Names'])['Attribute Values'].aggregate('first').unstack()

target_df = pd.DataFrame(target_df.to_records())
#print(target_df.shape)
target_df.head()


# In[18]:


aux_df = data[['ID','MakeText','TypeName','TypeNameFull','ModelText','ModelTypeText']]
aux_df = aux_df.drop_duplicates()
#print(aux_df.shape)
#aux_df.head()


# In[19]:


target_df = pd.merge(aux_df,target_df)
target_df.set_index('ID',inplace = True)
target_df.sort_values(by=['ID'], ascending=[True],inplace = True)
target_df.columns


# In[20]:


geolocator = Nominatim(user_agent = "geoapiExercises")

cities = target_df['City'].unique()
dict_countries = {}

for city in cities:
    location = geolocator.geocode(city,exactly_one=True)
    coord = str(location[-1][0]) +","+ str(location[-1][1] )

    raw = geolocator.reverse(coord)
    address = raw.raw['address']
    
    country = address.get('country', '')
    if country == 'Schweiz/Suisse/Svizzera/Svizra':
        country = 'Switzerland'
    code = address.get('country_code').upper()    
    dict_countries[city] = [code,country]


#print(dict_countries)


# In[21]:


#reorder and rename columns
column_order = ["BodyTypeText", "BodyColorText",'ConditionTypeText', 'City','Country', 'MakeText', 'FirstRegYear', 'Km','mileage_unit', 'TypeName',
                'ModelTypeText', 'FirstRegMonth','Zip', 'ConsumptionTotalText','TypeNameFull', 'ModelText','Ccm', 'Co2EmissionText',
                'ConsumptionRatingText','Doors', 'DriveTypeText','FuelTypeText', 'Hp', 'InteriorColorText','Properties', 
                'Seats','TransmissionTypeText']

target_df = target_df.reindex(columns=column_order)



column_names = {"BodyTypeText":'carType', "BodyColorText":'color','ConditionTypeText':'condition', 'MakeText':'make',
                'FirstRegYear':'manufacture_year', 'Km':'mileage', 'TypeName':'model','ModelTypeText':'model_variant',
                'FirstRegMonth':'manufacture_month', 'ConsumptionTotalText':'fuel_consumption_unit'}

target_df = target_df.rename(columns=column_names, errors="raise")

target_df['mileage_unit'] = np.where(target_df['mileage'].isnull(), 'null',target_df['mileage_unit'])
target_df['mileage_unit'] = np.where(target_df['mileage'] != 'null', 'kilometer' , target_df['mileage_unit'])

for city in dict_countries.keys():
    target_df['Country'] = np.where(target_df['City'] == city, dict_countries[city][0],target_df['Country'])
    target_df['Zip'] = np.where(target_df['City'] == city, dict_countries[city][1],target_df['Zip'])
target_df.head()


# In[ ]:





# In[22]:


target_df1 = target_df.copy()


# #### Normalization

# In[23]:


#In this stage it is necessary to, at least, alter condition and color to english and the comsumption fuel to only present the units

'''
Occasion -> Occasion
neu -> New
oldtimer -> Used

vorführmodell -> demonstration model
'''
target_df['condition'] = target_df['condition'].map(lambda x: x.lower())
target_df['condition'] = target_df['condition'].replace({'neu': 'new', 'oldtimer': 'used','vorführmodell':'demonstration model'})


# In[24]:



dict_colors = {'anthrazit':'anthracite','amaranth': 'amaranth', 'bernstein': 'amber', 'amethyst': 'amethyst', 'aprikose': 'apricot',
               'aquamarin': 'aquamarine', 'azurblau': 'azure', 'baby blau': 'baby blue', 'beige': 'beige',
               'schwarz': 'black', 'blau': 'blue','bordeaux':'bordeaux', 'blau grün': 'blue-green','blau grun': 'blue-green', 'blau violett': 'blue-violet',
               'erröten': 'blush', 'ziegelrot': 'brick red', 'bronze': 'bronze', 'braun': 'brown',
               'burgund': 'burgundy', 'byzanz': 'byzantium', 'karminrot': 'carmine', 'cerise': 'cerise',
               'himmelblau': 'cerulean', 'champagner': 'champagne', 'chartreuse grün': 'chartreuse green',
               'schokolade': 'chocolate', 'kobaltblau': 'cobalt blue', 'kaffee': 'coffee', 'kupfer': 'copper',
               'koralle': 'coral', 'purpur': 'crimson', 'cyan': 'cyan', 'wüstensand': 'desert sand',
               'elektrisches blau': 'electric blue', 'smaragd': 'emerald', 'erina': 'erin', 'gold': 'gold',
               'grau': 'gray', 'grün': 'green', 'harlekin': 'harlequin', 'indigo': 'indigo', 'elfenbein': 'ivory',
               'jade': 'jade', 'dschungelgrün': 'jungle green', 'lavendel': 'lavender', 'zitrone': 'lemon',
               'lila': 'purple', 'limette': 'lime', 'magenta': 'magenta', 'magentarose': 'magenta rose',
               'kastanienbraun': 'maroon', 'mauve': 'mauve', 'navy blau': 'navy blue', 'ocker': 'ochre',
               'olive': 'olive', 'orange': 'orange', 'orange rot': 'orange-red', 'orchidee': 'orchid', 'pfirsich': 'peach',
               'birne': 'pear', 'immergrün': 'periwinkle', 'persisches blau': 'persian blue', 'rosa': 'pink',
               'pflaume': 'plum', 'preußischblau': 'prussian blue','preussischblau': 'prussian blue', 'puce': 'puce', 'himbeere': 'raspberry', 'rot': 'red',
               'rot-violett': 'red-violet', 'rose': 'rose', 'rubin': 'ruby', 'lachs': 'salmon', 'sangria': 'sangria',
               'saphir': 'sapphire', 'scharlachrot': 'scarlet', 'silber': 'silver', 'schiefer grau': 'slate gray', 
               'frühlingsknospe': 'spring bud', 'frühlingsgrün': 'spring green','fruhlingsgrun': 'spring green',
               'bräunen': 'tan','braunen': 'tan', 'taupe': 'taupe',
               'blaugrün': 'teal', 'türkis': 'turquoise', 'ultramarin': 'ultramarine', 'violett': 'violet',
               'viridian': 'viridian', 'weiß': 'white','weiss': 'white', 'gelb': 'yellow'}


target_df['color'] = target_df['color'].map(lambda x: x.split()[0])
target_df['color'] = target_df['color'].map(lambda x: x.lower())
target_df['color'] = target_df['color'].replace(dict_colors)


# In[25]:



target_df['fuel_consumption_unit'] = target_df['fuel_consumption_unit'].map(lambda x: ''.join([i for i in x if not i.isdigit()]))
target_df['fuel_consumption_unit'] = target_df['fuel_consumption_unit'].map(lambda x: x.replace('.','').replace(' ','').replace('/','_'))
target_df['fuel_consumption_unit'] = target_df['fuel_consumption_unit'].map(lambda x: x + '_consumption' if 'null' not in x else x)
#target_df['fuel_consumption_unit'].unique()


# In[26]:


target_df2 = target_df.copy()
#target_df.columns


# ### Data Integration

# In[27]:


target_df3 = target_df.reset_index(drop=True)
target_df3 = target_df3.drop(columns=['TypeNameFull',
       'ModelText', 'Ccm', 'Co2EmissionText', 'ConsumptionRatingText', 'Doors',
       'DriveTypeText', 'FuelTypeText', 'Hp', 'InteriorColorText',
       'Properties', 'Seats', 'TransmissionTypeText'])
target_df3.head()


# In[28]:



with pd.ExcelWriter('output.xlsx') as writer:  
    target_df1.to_excel(writer, sheet_name='pre-processing')
    target_df2.to_excel(writer, sheet_name='normalisation')
    target_df3.to_excel(writer, sheet_name='integration', index=False)


# In[ ]:




