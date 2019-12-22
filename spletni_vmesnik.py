import json
import bottle
from model import Film, Oseba

with open('nastavitve.json') as f:
    nastavitve = json.load(f)
    SKRIVNOST = nastavitve['skrivnost']

def zahtevaj_prijavo():
    if bottle.request.get_cookie('uporabnik', secret=SKRIVNOST) != 'admin':
        bottle.abort(401, 'Nimate pravice za urejanje!')


@bottle.get('/prijava/')
def prijava():
    return bottle.template(
        'prijava.html',
        napaka=None
    )

@bottle.post('/prijava/')
def prijava_post():
    ime = bottle.request.forms['uporabnisko_ime']
    geslo = bottle.request.forms['geslo']
    if ime == geslo:
        bottle.response.set_cookie('uporabnik', ime, path='/', secret=SKRIVNOST)
        bottle.redirect('/')
    else:
        return bottle.template(
            'prijava.html',
            napaka='Uporabniško ime in geslo se ne ujemata!'
        )



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

@bottle.get('/dodaj-osebo/')
def dodaj_osebo():
    zahtevaj_prijavo()
    return bottle.template(
        'dodaj_osebo.html',
        napaka=None
    )

@bottle.post('/dodaj-osebo/')
def dodaj_osebo_post():
    zahtevaj_prijavo()
    ime = bottle.request.forms['ime']
    if not ime[0].isupper():
        return bottle.template(
            'dodaj_osebo.html',
            napaka='Ime se mora začeti z veliko začetnico!'
        )
    else:
        oseba = Oseba(ime)
        oseba.dodaj_v_bazo()
        bottle.redirect('/')

@bottle.get('/isci/')
def isci():
    iskalni_niz = bottle.request.query.getunicode('iskalni_niz')
    osebe = Oseba.poisci(iskalni_niz)
    return bottle.template(
        'rezultati_iskanja.html',
        iskalni_niz=iskalni_niz,
        osebe=osebe
    )


bottle.run(debug=True, reloader=True)
