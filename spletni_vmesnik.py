import bottle

@bottle.get('/')
def pozdravi():
    return 'Živjo!'

bottle.run()
