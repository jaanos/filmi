import csv

class Tabela:
    """
    Razred, ki predstavlja tabelo v bazi.

    Polja razreda:
    - ime: ime tabele
    - podatki: datoteka s podatki ali None
    - id: stolpec z lastnostjo AUTOINCREMENT ali None
    """
    ime = None
    podatki = None
    id = None

    def __init__(self, conn):
        """
        Konstruktor razreda.
        """
        self.conn = conn

    def ustvari(self):
        """
        Metoda za ustvarjanje tabele.
        Podrazredi morajo povoziti to metodo.
        """
        raise NotImplementedError

    def izbrisi(self):
        """
        Metoda za brisanje tabele.
        """
        self.conn.execute("DROP TABLE IF EXISTS {};".format(self.ime))

    def uvozi(self, encoding="UTF-8", **kwargs):
        """
        Metoda za uvoz podatkov.

        Argumenti:
        - encoding: kodiranje znakov
        - ostali poimenovani argumenti: za metodo dodaj_vrstico
        """
        if self.podatki is None:
            return
        with open(self.podatki, encoding=encoding) as datoteka:
            podatki = csv.reader(datoteka)
            stolpci = self.pretvori(next(podatki), kwargs)
            poizvedba = self.dodajanje(stolpci)
            for vrstica in podatki:
                vrstica = [None if x == "" else x for x in vrstica]
                self.dodaj_vrstico(vrstica, poizvedba, **kwargs)

    def izprazni(self):
        """
        Metodo za praznjenje tabele.
        """
        self.conn.execute("DELETE FROM {};".format(self.ime))

    @staticmethod
    def pretvori(stolpci, kwargs):
        """
        Prilagodi imena stolpcev
        in poskrbi za ustrezne argumente za dodaj_vrstico.

        Privzeto vrne podane stolpce.
        """
        return stolpci

    def dodajanje(self, stolpci=None, stevilo=None):
        """
        Metoda za gradnjo poizvedbe.

        Arugmenti uporabimo enega od njiju):
        - stolpci: seznam stolpcev
        - stevilo: število stolpcev
        """
        if stolpci is None:
            assert stevilo is not None
            st = ""
        else:
            st = " ({})".format(", ".join(stolpci))
            stevilo = len(stolpci)
        return "INSERT INTO {}{} VALUES ({})". \
            format(self.ime, st, ", ".join(["?"] * stevilo))

    def dodaj_vrstico(self, podatki, poizvedba=None, **kwargs):
        """
        Metoda za dodajanje vrstice.

        Argumenti:
        - podatki: seznam s podatki v vrstici
        - poizvedba: poizvedba, ki naj se zažene
        - poljubni poimenovani parametri: privzeto se ignorirajo
        """
        if poizvedba is None:
            poizvedba = self.dodajanje(stevilo=len(podatki))
        cur = self.conn.execute(poizvedba, podatki)
        if self.id is not None:
            return cur.lastrowid


class Zanr(Tabela):
    """
    Tabela za žanre.
    """
    ime = "zanr"
    id = "id"

    def ustvari(self):
        """
        Ustvari tabelo zanr.
        """
        self.conn.execute("""
            CREATE TABLE zanr (
                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                naziv TEXT UNIQUE
            );
        """)

    def dodaj_vrstico(self, podatki, poizvedba=None):
        """
        Dodaj žanr.

        Če žanr že obstaja, vrne obstoječ ID.
        """
        cur = self.conn.execute("""
            SELECT id FROM zanr
            WHERE naziv = ?;
        """, podatki)
        r = cur.fetchone()
        if r is None:
            return super().dodaj_vrstico(podatki, poizvedba)
        else:
            id, = r
            return id


class Oznaka(Tabela):
    """
    Tabela za oznake.
    """
    ime = "oznaka"

    def ustvari(self):
        """
        Ustvari tabelo oznaka.
        """
        self.conn.execute("""
            CREATE TABLE oznaka (
                kratica TEXT PRIMARY KEY
            );
        """)

    def dodaj_vrstico(self, podatki, poizvedba=None):
        """
        Dodaj oznako.

        Če oznaka že obstaja, je ne dodamo še enkrat.
        """
        cur = self.conn.execute("""
            SELECT kratica FROM oznaka
            WHERE kratica = ?;
        """, podatki)
        r = cur.fetchone()
        if r is None:
            super().dodaj_vrstico(podatki, poizvedba)


class Film(Tabela):
    """
    Tabela za filme.
    """
    ime = "film"
    podatki = "podatki/film.csv"

    def __init__(self, conn, oznaka):
        """
        Konstruktor tabele filmov.

        Argumenti:
        - conn: povezava na bazo
        - oznaka: tabela za oznake
        """
        super().__init__(conn)
        self.oznaka = oznaka

    def ustvari(self):
        """
        Ustavari tabelo film.
        """
        self.conn.execute("""
            CREATE TABLE film (
                id        INTEGER PRIMARY KEY,
                naslov    TEXT,
                dolzina   INTEGER,
                leto      INTEGER,
                ocena     REAL,
                metascore INTEGER,
                glasovi   INTEGER,
                zasluzek  INTEGER,
                oznaka    TEXT    REFERENCES oznaka (kratica),
                opis      TEXT
            );
        """)

    def uvozi(self, encoding="UTF-8"):
        """
        Uvozi podatke o filmih in pripadajoče oznake.
        """
        insert = self.oznaka.dodajanje(stevilo=1)
        super().uvozi(encoding=encoding, insert=insert)

    @staticmethod
    def pretvori(stolpci, kwargs):
        """
        Zapomni si indeks stolpca z oznako.
        """
        kwargs["oznaka"] = stolpci.index("oznaka")
        return stolpci

    def dodaj_vrstico(self, podatki, poizvedba=None, insert=None, oznaka=None):
        """
        Dodaj film in pripadajočo oznako.

        Argumenti:
        - podatki: seznam s podatki o filmu
        - poizvedba: poizvedba za dodajanje filma
        - insert: poizvedba za dodajanje oznake
        - oznaka: indeks stolpca z oznako
        """
        assert oznaka is not None
        if insert is None:
            insert = self.oznaka.dodajanje(1)
        if podatki[oznaka] is not None:
            self.oznaka.dodaj_vrstico([podatki[oznaka]], insert)
        super().dodaj_vrstico(podatki, poizvedba)


class Oseba(Tabela):
    """
    Tabela za osebe.
    """
    ime = "oseba"
    podatki = "podatki/oseba.csv"

    def ustvari(self):
        """
        Ustvari tabelo oseba.
        """
        self.conn.execute("""
            CREATE TABLE oseba (
                id  INTEGER PRIMARY KEY,
                ime TEXT
            );
        """)


class Vloga(Tabela):
    """
    Tabela za vloge.
    """
    ime = "vloga"
    podatki = "podatki/vloga.csv"

    def ustvari(self):
        """
        Ustvari tabelo vloga.
        """
        self.conn.execute("""
            CREATE TABLE vloga (
                film  INTEGER   REFERENCES film (id),
                oseba INTEGER   REFERENCES oseba (id),
                tip   CHARACTER CHECK (tip IN ('I',
                                'R') ),
                mesto INTEGER,
                PRIMARY KEY (
                    film,
                    oseba,
                    tip
                )
            );
        """)


class Pripada(Tabela):
    """
    Tabela za relacijo pripadnosti filma žanru.
    """
    ime = "pripada"
    podatki = "podatki/zanr.csv"

    def __init__(self, conn, zanr):
        """
        Konstruktor tabele pripadnosti žanrom.

        Argumenti:
        - conn: povezava na bazo
        - zanr: tabela za žanre
        """
        super().__init__(conn)
        self.zanr = zanr

    def ustvari(self):
        """
        Ustvari tabelo pripada.
        """
        self.conn.execute("""
            CREATE TABLE pripada (
                film INTEGER REFERENCES film (id),
                zanr INTEGER REFERENCES zanr (id),
                PRIMARY KEY (
                    film,
                    zanr
                )
            );
        """)

    def uvozi(self, encoding="UTF-8"):
        """
        Uvozi pripadnosti filmov in pripadajoe žanre.
        """
        insert = self.zanr.dodajanje(["naziv"])
        super().uvozi(encoding=encoding, insert=insert)

    @staticmethod
    def pretvori(stolpci, kwargs):
        """
        Spremeni ime stolpca z žanrom
        in si zapomni njegov indeks.
        """
        naziv = kwargs["naziv"] = stolpci.index("naziv")
        stolpci[naziv] = "zanr"
        return stolpci

    def dodaj_vrstico(self, podatki, poizvedba=None, insert=None, naziv=None):
        """
        Dodaj pripadnost filma in pripadajoči žanr.

        Argumenti:
        - podatki: seznam s podatki o pripadnosti
        - poizvedba: poizvedba za dodajanje pripadnosti
        - insert: poizvedba za dodajanje žanra
        - oznaka: indeks stolpca z žanrom
        """
        assert naziv is not None
        if insert is None:
            insert = self.zanr.dodajanje(["naziv"])
        podatki[naziv] = self.zanr.dodaj_vrstico([podatki[naziv]], insert)
        super().dodaj_vrstico(podatki, poizvedba)


def ustvari_tabele(tabele):
    """
    Ustvari podane tabele.
    """
    for t in tabele:
        t.ustvari()


def izbrisi_tabele(tabele):
    """
    Izbriši podane tabele.
    """
    for t in tabele:
        t.izbrisi()


def uvozi_podatke(tabele):
    """
    Uvozi podatke v podane tabele.
    """
    for t in tabele:
        t.uvozi()


def izprazni_tabele(tabele):
    """
    Izprazni podane tabele.
    """
    for t in tabele:
        t.izprazni()


def ustvari_bazo(conn):
    """
    Izvede ustvarjanje baze.
    """
    tabele = pripravi_tabele(conn)
    izbrisi_tabele(tabele)
    ustvari_tabele(tabele)
    uvozi_podatke(tabele)


def pripravi_tabele(conn):
    """
    Pripravi objekte za tabele.
    """
    zanr = Zanr(conn)
    oznaka = Oznaka(conn)
    film = Film(conn, oznaka)
    oseba = Oseba(conn)
    vloga = Vloga(conn)
    pripada = Pripada(conn, zanr)
    return [zanr, oznaka, film, oseba, vloga, pripada]


def ustvari_bazo_ce_ne_obstaja(conn):
    """
    Ustvari bazo, če ta še ne obstaja.
    """
    with conn:
        cur = conn.execute("SELECT COUNT(*) FROM sqlite_master")
        if cur.fetchone() == (0, ):
            ustvari_bazo(conn)