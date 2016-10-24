# - *- coding: utf- 8 - *-
import twitter
import flickr_api
import random
import networkx as nx
from flickr_api.api import flickr
import sys, requests, json

# Llaves de API Flickr
FLICKR_API_KEY = "76827ad9eaad1bd3a99714a4d0bddb58"
FLICKR_API_SECRET = "cf97b6510ae41c68"

flickr_api.set_keys(api_key = FLICKR_API_KEY, api_secret = FLICKR_API_SECRET)

# Cantidad de tweets para traer del timeline (max. 200 por api)
tweetCount = 100

userCheck = False

#################################
### Connection to Twitter API ###
#################################

TWITTER_CONSUMER_KEY = "vaIY3GCpoLs2KNZjU0O1OwbKe"
TWITTER_CONSUMER_SECRET = "zMeF2HN5FZukSD2BrlhTiwasvAXw3uG6wssan0RXcEoeApXwoA"
TWITTER_ACCESS_TOKEN_KEY = "34757935-HGoJ1rJjoqyZbpefIoF5XbqJfNgnIUpIJhmeP4c8m"
TWITTER_ACCESS_TOKEN_SECRET = "pgJ8OSOQ3SDZsSL41OiAy79i7qGbxmnB8yHBlNCIzNKwX"

try:
    api = twitter.Api(consumer_key = TWITTER_CONSUMER_KEY,
                  consumer_secret = TWITTER_CONSUMER_SECRET,
                  access_token_key = TWITTER_ACCESS_TOKEN_KEY,
                  access_token_secret = TWITTER_ACCESS_TOKEN_SECRET)                
except:
    print "No se pudo conectar a la API de Twitter, lamentamos las molestias."
    sys.exit()           

############################
### Check if user exists ###
############################       

while not userCheck:
    
    # Si se deja en blanco el input, usa el usuario loggeado (@tommehthecat)
    print "Bienvenido a Twitter Analytics!"
    print "Escribe 'exit' si quieres salir."
    print "Que usuario quieres buscar?"
    user = raw_input()
    
    if user == "exit":
        print "Hasta luego!"
        sys.exit()
    
    if user and not user.startswith('@'):
        user = '@' + user
        
    if not user:
        try:
            foundUser.id = ''
            break
        except NameError:
            print 'Usuario Inválido.'
            sys.exit()
            
    
    try:
        foundUser = api.GetUser(screen_name = user)
        userCheck = True
        print '\n'
    except:
        print "El usuario {} no fue encontrado, vuelve a intentar.".format(user)


def mostUsedWords( tweets ):
    most_used_words = []
    for tweet in tweets:
        encoded_tweet = tweet.text.encode('utf-8')
        tweet_words = str(encoded_tweet).split(' ')
        for tweet_word in tweet_words:
            used = False
            for used_word in most_used_words:
                if( tweet_word == used_word['text']):
                    used_word['repeated'] = used_word['repeated'] + 1
                    used = True
            if not( used ):
                new_word = {'text': tweet_word, 'repeated': 1}
                if not(new_word['text'].startswith('@')):
                    most_used_words.append(new_word)
    for j in range(1, len(most_used_words)):
        key = most_used_words[j]
        i = j - 1
        while( i >= 0 and most_used_words[i]['repeated'] < key['repeated']):
            most_used_words[i + 1] = most_used_words[i]
            i = i - 1
        most_used_words[i + 1] = key
    print 'Las palabras más usadas por {} son:'.format(user)
    for i in range(10):
        print ('{}.- {}, {} veces.'
        .format(i + 1, most_used_words[i]['text'], most_used_words[i]['repeated']))


def findWordIn( word, tweets ):
    count = 0
    for tweet in tweets:
        encoded_tweet = tweet.text.encode('utf-8')
        tweet_words = str(encoded_tweet).split(' ')
        for tweet_word in tweet_words:
            if( tweet_word == word ):
                count = count + 1
    print 'La palabra {} fue utilizada por {}, {} veces'.format(word, user, count)

            
def getTrendingTopics():   
    
    print 'Mostrando trending topics globales:\n'    
    
    trending_topics = api.GetTrendsCurrent()
    for topic in trending_topics:
        print topic.name
        
        
def getLocalTrendingTopics():
    
    send_url = 'http://freegeoip.net/json'
    r = requests.get(send_url)
    j = json.loads(r.text)   
    
    location = flickr.places.findByLatLon(
        lat = j['latitude'], 
        lon = j['longitude'], 
        format = "json", 
        nojsoncallback = 1)
    
    n = json.loads(location)
    woeid = n['places']['place'][0]['woeid']  
    place_name = n['places']['place'][0]['name']
    
    print 'Mostrando trending topics cerca de {}:\n'.format(place_name)
    
    trending_topics = api.GetTrendsWoeid(woeid)
    for topic in trending_topics:
        print topic.name

def getShortestNetwork():
    
    tw_file = file('twitter_combined.txt')
    id_found = False
    
    users = set()

    for line in tw_file:
        line_array = line.split()
        
        for Id in line_array:
            users.add(Id)
            
        if str(foundUser.id) in line:
            id_found = True
    
    if not id_found:
        print "El id de usuario no fue encontrado en la muestra. Elige otro."
        return
    
    users = list(users)
    query = True
    
    while query:
        random_id = random.choice(users)
        
        user = api.GetUser(user_id = random_id).screen_name
        
        print "Elige otro usuario al cual quieres llegar (sugerencia: @{})".format(user)
        target_user = raw_input()
        if target_user and not target_user.startswith('@'):
            target_user = '@' + target_user
        
        try:
            secondUser = api.GetUser(screen_name = target_user)
            print '\n'
        except:
            print "El usuario {} no fue encontrado, vuelve a intentar.".format(target_user)
    
        if str(secondUser.id) in users:
            query = False
        else:
            print "El usuario {} no esta en nuestra base de datos, vuelve a intentar.".format(target_user)
    
    print "Calculando camino mas corto..."
    
    G = nx.read_edgelist("twitter_combined.txt", nodetype = int)
    nodes = G.nodes()
    
    shortest_path = nx.shortest_path(
        G, 
        source=nodes[nodes.index(foundUser.id)], 
        target=nodes[nodes.index(secondUser.id)])
        
    print "Consiguiendo el nombre de los usuarios..."
    
    names_shortest_path = list()
    for Id in shortest_path:
        user = api.GetUser(user_id = Id).screen_name
        names_shortest_path.append(user)
        
    print "El camino mas corto del usuario @{} a @{} es: ".format(foundUser.screen_name, secondUser.screen_name)
    print '\n'
        
    for name in names_shortest_path:
        print "@{}".format(name)

                
            
##############################
#### Get timeline from user ###
###############################
timeline = api.GetUserTimeline(user_id = foundUser.id, count = tweetCount)

    
while True:
    print '################################'
    print 'Seleccione una de las opciones'
    print '1.- Ver los últimos tweets'
    print '2.- Ver las palabras mas usadas'
    print '3.- Busqueda por palabra'
    print '4.- Ver los trending topics globales'
    print '5.- Ver los trending topics cercanos'
    print '6.- NUEVO! Ver red mas cercana entre un usuario y otro'
    print '0.- Salir'
    while True:
        try:
            option = int(input())
            break
        except (ValueError, NameError):
            print 'Oops, intentalo otra vez'
    
    if(option == 1):
        print 'Estos son los tweets de {}'.format(user)
        for i in range(10):
            print '{} .- {}'.format(i+1, timeline[i].text.encode('utf-8'))
            print '\n'
    elif( option == 2 ):
        mostUsedWords(timeline)
    elif(option == 3):
        print 'Ingrese la palabra para la busqueda.'
        word = str(raw_input())
        findWordIn(word, timeline)
    elif( option == 4):
        getTrendingTopics()
    elif( option == 5):
        getLocalTrendingTopics()
    elif(option == 6):
        getShortestNetwork()
    elif( option == 0 ):
        print 'Hasta luego!'
        sys.exit()
    else:
        print 'Opción invalida, adios'
        sys.exit()
    raw_input("Presiona una tecla para continuar...")



