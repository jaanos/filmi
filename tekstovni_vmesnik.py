from enum import Enum
from model import Film, Oseba


class Meni(Enum):
    def __init__(self, ime, funkcija):
        self.ime = ime
        self.funkcija = funkcija

    def __str__(self):
        return self.ime


def izpisi_vloge(igralec):
    print(igralec.ime)
    for naslov, leto, vloga in igralec.poisci_vloge():
        print(f'- {naslov} ({leto}, {vloga})')


def vnesi_izbiro(moznosti):
    moznosti = list(moznosti)
    for i, moznost in enumerate(moznosti, 1):
        print(f'{i}) {moznost}')
    izbira = int(input('> ')) - 1
    return moznosti[izbira]


def poisci_osebo():
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
    oseba = poisci_osebo()
    izpisi_vloge(oseba)


def najboljsi_filmi():
    leto = input('Katero leto te zanima? ')
    filmi = Film.najboljsi_v_letu(leto)
    for mesto, film in enumerate(filmi, 1):
        print(f'{mesto}) {film.naslov} ({film.ocena}/10)')


def domov():
    print('Adijo!')


class GlavniMeni(Meni):
    ISKAL_OSEBO = ('Iskal osebo', iskanje_osebe)
    POGLEDAL_DOBRE_FILME = ('Pogledal dobre filme', najboljsi_filmi)
    SEL_DOMOV = ('Šel domov', domov)


def glavni_meni():
    print('Pozdravljen v bazi filmov!')
    while True:
        print('Kaj bi rad delal?')
        izbira = vnesi_izbiro(GlavniMeni)
        izbira.funkcija()
        if izbira == GlavniMeni.SEL_DOMOV:
            return


glavni_meni()
