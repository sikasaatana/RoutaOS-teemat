# RoutaOS-teemat

Teemat RoutaOS:n Asetuksiin (Asetukset > Ulkoasu > Teema > **+ Lataa lisää teemoja**).
RoutaOS 0.99.57+ hakee luettelon osoitteesta

    https://raw.githubusercontent.com/sikasaatana/RoutaOS-teemat/main/teemat.txt

Repon pitää olla **julkinen**, jotta RoutaOS voi ladata siitä ilman kirjautumista.

## Teemat

| Teema | Tyyli |
|---|---|
| Revontuli | tumma, vihreät revontulet |
| Kaamos | sininen kaamosyö, oranssi valo |
| Ruska | syksyn ruskea ja oranssi |
| Tunturi | vaalea, lumiset tunturit |
| Saaristo | meri ja auringonlasku |
| Juhannus | vaalea kulta, yötön yö |
| Hämärä | violetti iltahämärä |
| Metsä | usvainen kuusimetsä |
| Lumi | puhtaan valkoinen |
| Sauna | tumma puu ja kiukaan hehku |

Jokaisessa on `.teema` (värit), kuvakaappaus (`<tunnus>.jpg`) ja taustakuva (`<tunnus>-tausta.jpg`, 1600×900).

## Uusi teema

1. Tee `<tunnus>.teema` (tunnus: pienet kirjaimet, numerot, `-` ja `_`):
   ```
   nimi=Oma teema
   tekija=Nimi
   versio=1.0
   kuvaus=Lyhyt kuvaus
   kuva=<tunnus>.jpg
   taustakuva=<tunnus>-tausta.jpg
   tausta=#RRGGBB
   ikkuna=#RRGGBB
   teksti=#RRGGBB
   korostus=#RRGGBB
   ```
   Pakolliset värit: `tausta`, `ikkuna`, `teksti`, `korostus`. Valinnaiset: `otsikko`, `otsikko_passiivinen`, `reuna`, `reuna_passiivinen`, `teksti_himmea`, `sulje`, `paneeli`, `paneeli_teksti`.
2. Lisää kuvat samaan kansioon (JPG baseline tai PNG).
3. Aja `python3 tee_luettelo.py` (päivittää `teemat.txt`:n ja kuvien SHA-256-summat).
4. Commit ja push. RoutaOS:ssä: Lisää teemoja > Päivitä.

`tee_taustat.py` piirtää tämän repon taustakuvat ohjelmallisesti (numpy + Pillow).

Kuvat ja teemat: Jesse Väisänen.
