# Hrvatska lokalizacija

`hr.json` je baza prijevoda javnih UI tekstova. `hr-overrides.json` sadrži
ručne ispravke; `apple-hr.json` prevodi naše dodatke. Redoslijed primjene je
baza → ispravke → dodatci. Ključ je točan izvorni engleski tekst, a vrijednost
hrvatski prijevod.

Baza je proizvedena lokalno na Macu modelom
[Helsinki-NLP/opus-mt-en-sla](https://huggingface.co/Helsinki-NLP/opus-mt-en-sla),
revizija `0bc26914f2f82c3dd5b235e420aa2c711a5ed3d8`, ciljni token `>>hrv<<`.
Korišteni su samo javni tekstovi iz kataloga aplikacije. Model nije dio appa;
za izgradnju aplikacije nisu potrebni Python ML paketi niti model weights.
Model card navodi Apache-2.0; aplikacija i naš izvor ostaju pod GPLv3.

Ručno su popravljeni česti elementi navigacije, API vjerodajnice, kritične
poruke o brisanju/obnovi/migraciji, zadržani formatni argumenti, kod i URL-ovi.
Pokrivenost kataloga nije isto što i završena jezična provjera svakog zaslona.
Neke duže rečenice još mogu zvučati neprirodno; popravljati ih u overrides,
a ne prepisivati cijeli upstream katalog.

```sh
python3 scripts/fork/localize.py
```

Provjera mora proći bez nedostajućih ključeva, promijenjenih placeholdera,
koda u backtickovima, HTTP URL-ova ili ostataka ćirilice. Izvještaj se uvijek
osvježava u `.build/localization-gaps.json`. `--allow-incomplete` služi samo
za dijagnostiku i ne koristi se pri normalnoj izgradnji.

`src/ios/hr.lproj/InfoPlist.strings` sadrži 18 ručno prevedenih sistemskih
opisa dopuštenja. Na novoj upstream verziji pregledati i promjene
`InfoPlist.strings`, `Info.plist` i neregistrirane/hardkodirane UI tekstove.
