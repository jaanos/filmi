from enum import Enum
from model import Film, Oseba


class Meni(Enum):
    """
    Razred za izbire v menijih.
    """
    def __init__(self, ime, funkcija):
        """
        Konstruktor izbire.
        """
        self.ime = ime
        self.funkcija = funkcija

    def __str__(self):
        """
        Znakovna predstavitev izbire.
        """
        return self.ime


def izpisi_vloge(igralec):
    """
    Izpiše vse vloge podanega igralca.
    """
    print(igralec.ime)
    for naslov, leto, vloga in igralec.poisci_vloge():
        print(f'- {naslov} ({leto}, {vloga})')


def vnesi_izbiro(moznosti):
    """
    Uporabniku da na izbiro podane možnosti.
    """
    moznosti = list(moznosti)
    for i, moznost in enumerate(moznosti, 1):
        print(f'{i}) {moznost}')
    izbira = int(input('> ')) - 1
    return moznosti[izbira]


def poisci_osebo():
    """
    Poišče osebo, ki jo vnese uporabnik.
    """
    while True:
        ime_igralca = input('Kdo te zanima? ')
        osebe = list(Oseba.poisci(ime_igralca))
        if len(osebe) == 1:
            return osebe[0]
        elif len(osebe) == 0:
            print('Te osebe ne najdem. Poskusi znova.')
        else:
            print('Našel sem več igralcev, kateri od teh te zanima?')
            return vnesi_izbiro(osebe)


def iskanje_osebe():
    """
    Izpiše vloge za osebo, ki jo vnese uporabnik.
    """
    oseba = poisci_osebo()
    izpisi_vloge(oseba)


def najboljsi_filmi():
    """
    Izpiše najboljših 10 filmov v letu, ki ga vnese uporabnik.
    """
    leto = input('Katero leto te zanima? ')
    filmi = Film.najboljsi_v_letu(leto)
    for mesto, film in enumerate(filmi, 1):
        print(f'{mesto}) {film.naslov} ({film.ocena}/10)')


def domov():
    """
    Pozdravi pred izhodom.
    """
    print('Adijo!')


class GlavniMeni(Meni):
    """
    Izbire v glavnem meniju.
    """
    ISKAL_OSEBO = ('Iskal osebo', iskanje_osebe)
    POGLEDAL_DOBRE_FILME = ('Pogledal dobre filme', najboljsi_filmi)
    SEL_DOMOV = ('Šel domov', domov)


def glavni_meni():
    """
    Prikazuje glavni meni, dokler uporabnik ne izbere izhoda.
    """
    print('Pozdravljen v bazi filmov!')
    while True:
        print('Kaj bi rad delal?')
        izbira = vnesi_izbiro(GlavniMeni)
        izbira.funkcija()
        if izbira == GlavniMeni.SEL_DOMOV:
            return


glavni_meni()
