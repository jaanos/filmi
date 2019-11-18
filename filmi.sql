--
-- File generated with SQLiteStudio v3.0.3 on pon. nov. 18 10:49:29 2019
--
-- Text encoding used: UTF-8
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: zanr
CREATE TABLE zanr (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    naziv TEXT
);

-- Table: oznaka
CREATE TABLE oznaka (
    kratica TEXT PRIMARY KEY
);

-- Table: film
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

-- Table: oseba
CREATE TABLE oseba (
    id  INTEGER PRIMARY KEY,
    ime TEXT
);

-- Table: vloga
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

-- Table: pripada
CREATE TABLE pripada (
    film INTEGER REFERENCES film (id) ON DELETE CASCADE,
    zanr INTEGER REFERENCES zanr (id) ON UPDATE CASCADE,
    PRIMARY KEY (
        film,
        zanr
    )
);

COMMIT TRANSACTION;
