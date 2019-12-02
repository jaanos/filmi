from enum import Enum
import baza
import sqlite3

conn = sqlite3.connect('filmi.db')
baza.ustvari_bazo_ce_ne_obstaja(conn)
conn.execute('PRAGMA foreign_keys = ON')


class Film:
    """
    Razred za film.
    """

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


class Oseba:
    """
    Razred za osebo.
    """

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