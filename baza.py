import csv

class Tabela:
    ime = None
    podatki = None
    id = None

    def __init__(self, conn):
        self.conn = conn

    def ustvari(self):
        raise NotImplementedError

    def izbrisi(self):
        self.conn.execute("DROP TABLE IF EXISTS {};".format(self.ime))

    def uvozi(self, encoding="UTF-8", **kwargs):
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
        self.conn.execute("DELETE FROM {};".format(self.ime))

    @staticmethod
    def pretvori(stolpci, kwargs):
        return stolpci

    def dodajanje(self, stolpci=None, stevilo=None):
        if stolpci is None:
            assert stevilo is not None
            st = ""
        else:
            st = "({})".format(", ".join(stolpci))
            stevilo = len(stolpci)
        return "INSERT INTO {}{} VALUES ({})". \
            format(self.ime, st, ", ".join(["?"] * stevilo))

    def dodaj_vrstico(self, podatki, poizvedba=None, **kwargs):
        if poizvedba is None:
            poizvedba = self.dodajanje(stevilo=len(podatki))
        cur = self.conn.execute(poizvedba, podatki)
        if self.id is not None:
            return cur.lastrowid


class Zanr(Tabela):
    ime = "zanr"
    id = "id"

    def ustvari(self):
        self.conn.execute("""
            CREATE TABLE zanr (
                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                naziv TEXT
            );
        """)

    def dodaj_vrstico(self, podatki, poizvedba=None):
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
    ime = "oznaka"

    def ustvari(self):
        self.conn.execute("""
            CREATE TABLE oznaka (
                kratica TEXT PRIMARY KEY
            );
        """)

    def dodaj_vrstico(self, podatki, poizvedba=None):
        cur = self.conn.execute("""
            SELECT kratica FROM oznaka
            WHERE kratica = ?;
        """, podatki)
        r = cur.fetchone()
        if r is None:
            super().dodaj_vrstico(podatki, poizvedba)


class Film(Tabela):
    ime = "film"
    podatki = "podatki/film.csv"

    def __init__(self, conn, oznaka):
        super().__init__(conn)
        self.oznaka = oznaka

    def ustvari(self):
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
        insert = self.oznaka.dodajanje(stevilo=1)
        super().uvozi(encoding=encoding, insert=insert)

    @staticmethod
    def pretvori(stolpci, kwargs):
        kwargs["oznaka"] = stolpci.index("oznaka")
        return stolpci

    def dodaj_vrstico(self, podatki, poizvedba=None, insert=None, oznaka=None):
        assert oznaka is not None
        if insert is None:
            insert = self.oznaka.dodajanje(1)
        if podatki[oznaka] is not None:
            self.oznaka.dodaj_vrstico([podatki[oznaka]], insert)
        super().dodaj_vrstico(podatki, poizvedba)


class Oseba(Tabela):
    ime = "oseba"
    podatki = "podatki/oseba.csv"

    def ustvari(self):
        self.conn.execute("""
            CREATE TABLE oseba (
                id  INTEGER PRIMARY KEY,
                ime TEXT
            );
        """)


class Vloga(Tabela):
    ime = "vloga"
    podatki = "podatki/vloga.csv"

    def ustvari(self):
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
    ime = "pripada"
    podatki = "podatki/zanr.csv"

    def __init__(self, conn, zanr):
        super().__init__(conn)
        self.zanr = zanr

    def ustvari(self):
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
        insert = self.zanr.dodajanje(["naziv"])
        super().uvozi(encoding=encoding, insert=insert)

    @staticmethod
    def pretvori(stolpci, kwargs):
        naziv = kwargs["naziv"] = stolpci.index("naziv")
        stolpci[naziv] = "zanr"
        return stolpci

    def dodaj_vrstico(self, podatki, poizvedba=None, insert=None, naziv=None):
        assert naziv is not None
        if insert is None:
            insert = self.zanr.dodajanje(["naziv"])
        podatki[naziv] = self.zanr.dodaj_vrstico([podatki[naziv]], insert)
        super().dodaj_vrstico(podatki, poizvedba)


def ustvari_tabele(tabele):
    for t in tabele:
        t.ustvari()


def izbrisi_tabele(tabele):
    for t in tabele:
        t.izbrisi()


def uvozi_podatke(tabele):
    for t in tabele:
        t.uvozi()


def izprazni_tabele(tabele):
    for t in tabele:
        t.izprazni()


def ustvari_bazo(conn):
    tabele = pripravi_tabele(conn)
    izbrisi_tabele(tabele)
    ustvari_tabele(tabele)
    uvozi_podatke(tabele)


def pripravi_tabele(conn):
    zanr = Zanr(conn)
    oznaka = Oznaka(conn)
    film = Film(conn, oznaka)
    oseba = Oseba(conn)
    vloga = Vloga(conn)
    pripada = Pripada(conn, zanr)
    return [zanr, oznaka, film, oseba, vloga, pripada]


def ustvari_bazo_ce_ne_obstaja(conn):
    with conn:
        cur = conn.execute("SELECT COUNT(*) FROM sqlite_master")
        if cur.fetchone() == (0, ):
            ustvari_bazo(conn)