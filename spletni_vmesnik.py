import bottle
from model import Film, Oseba


@bottle.get('/')
def zacetna_stran():
    return bottle.template(
        'zacetna_stran.html',
        leta=range(1950, 2020),
    )


@bottle.get('/najboljsi/<leto:int>/')
def najboljsi_filmi(leto):
    return bottle.template(
        'najboljsi_filmi.html',
        leto=leto,
        filmi=Film.najboljsi_v_letu(leto)
    )


@bottle.get('/isci/')
def isci():
    iskalni_niz = bottle.request.query['iskalni_niz']
    osebe = Oseba.poisci(iskalni_niz)
    return bottle.template(
        'rezultati_iskanja.html',
        iskalni_niz=iskalni_niz,
        osebe=osebe
    )


bottle.run(debug=True, reloader=True)
