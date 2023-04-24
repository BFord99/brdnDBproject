import pandas as pd


df = pd.read_csv('guilds.csv') 

def getNames(): 
  for col in df.columns:
    print(col)

getNames()


df = df.rename(columns={'guild.name' : 'Name', 'guild.id' : 'id' , 'guild.realm.name' : 'realm', 'guild.realm.id' : 'realm_id', 'guild.realm.slug' : 'realm_slug'})

getNames()


df.to_csv('guilds.csv')


print(df.head(5))

