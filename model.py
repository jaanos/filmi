from enum import Enum
import baza
import sqlite3

conn = sqlite3.connect('filmi.db')
baza.ustvari_bazo_ce_ne_obstaja(conn)
conn.execute('PRAGMA foreign_keys = ON')

zanr, oznaka, film, oseba, vloga, pripada = baza.pripravi_tabele(conn)


class Film:
    """
    Razred za film.
    """

    insert = film.dodajanje(["naslov", "leto", "ocena"])
    insert_vloga = vloga.dodajanje(["film", "oseba", "tip"])

    def __init__(self, id, naslov, leto, ocena):
        """
        Konstruktor filma.
        """
        self.id = id
        self.naslov = naslov
        self.leto = leto
        self.ocena = ocena

    def __str__(self):
        """
        Znakovna predstavitev filma.

        Vrne naslov filma.
        """
        return self.naslov

    @staticmethod
    def najboljsi_v_letu(leto):
        """
        Vrne najboljših 10 filmov v danem letu.
        """
        sql = """
            SELECT id, naslov, leto, ocena
            FROM film
            WHERE leto = ?
            ORDER BY ocena DESC
            LIMIT 10
        """
        for id, naslov, leto, ocena in conn.execute(sql, [leto]):
            yield Film(id, naslov, leto, ocena)

    def dodaj_film(self, reziserji, igralci):
        assert self.id is None
        with conn:
            self.id = film.dodaj_vrstico(
                [self.naslov, self.leto, self.ocena],
                self.insert
            )
            for oseba in reziserji:
                vloga.dodaj_vrstico(
                    [self.id, oseba.id, TipVloge.R.name],
                    self.insert_vloga
                )
            for oseba in igralci:
                vloga.dodaj_vrstico(
                    [self.id, oseba.id, TipVloge.I.name],
                    self.insert_vloga
                )


class Oseba:
    """
    Razred za osebo.
    """

    insert = oseba.dodajanje(["ime"])

    def __init__(self, id, ime):
        """
        Konstruktor osebe.
        """
        self.id = id
        self.ime = ime

    def __str__(self):
        """
        Znakovna predstavitev osebe.

        Vrne ime osebe.
        """
        return self.ime

    def poisci_vloge(self):
        """
        Vrne vloge osebe.
        """
        sql = """
            SELECT film.naslov, film.leto, vloga.tip
            FROM film
                JOIN vloga ON film.id = vloga.film
            WHERE vloga.oseba = ?
            ORDER BY leto
        """
        for naslov, leto, tip_vloge in conn.execute(sql, [self.id]):
            yield (naslov, leto, TipVloge[tip_vloge])

    @staticmethod
    def poisci(niz):
        """
        Vrne vse osebe, ki v imenu vsebujejo dani niz.
        """
        sql = "SELECT id, ime FROM oseba WHERE ime LIKE ?"
        for id, ime in conn.execute(sql, ['%' + niz + '%']):
            yield Oseba(id, ime)

    def dodaj_osebo(self):
        assert self.id is None
        with conn:
            self.id = oseba.dodaj_vrstico([self.ime], self.insert)


class TipVloge(Enum):
    """
    Oznake za tip vloge.
    """
    I = 'igralec'
    R = 'režiser'

    def __str__(self):
        """
        Znakovna predstavitev tipa vloge.
        """
        return self.value