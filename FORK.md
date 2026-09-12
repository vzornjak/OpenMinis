# Minis HR — održavanje forka

Fork: https://github.com/vzornjak/OpenMinis/tree/ios-hr-apple

Izvor: https://github.com/OpenMinis/OpenMinis

Osnova provjerena 13. rujna 2026.: javni `main`, tag `1.13`, commit
`4ef29002e88db1e20e462ec2ff46916e8a7dcb45`. Javni repozitorij je mirror
razvoja autora. `main` u našem forku prati izvornik; naše promjene su u
`ios-hr-apple`. Nije uspostavljeno službeno partnerstvo s autorima.

## Što je dodano

- Hrvatski u izborniku jezika, 18 opisa sistemskih dopuštenja i prijevodi svih
  2.163 ne-praznih prevodivih ključeva izvornog kataloga 1.13.
- Izvorni `Localizable.xcstrings` ostaje nepromijenjen. Hrvatski se sastavlja
  iz odvojenih JSON datoteka pri izgradnji. Novi ključevi i oštećeni formatni
  argumenti, kod ili URL-ovi zaustavljaju provjeru.
- Izvorni odabir modela dobiva Apple Foundation Models bez API ključa.
  Dodavanje: Postavke → pružatelji modela → dodaj → Apple Foundation Models.
  Zatim odabrati `Apple · On Device` u razgovoru.
- Lokalni tekst i slike, streaming, dinamičke sheme alata, provjera dostupnosti
  i jezika, stvarni broj tokena i veličina konteksta iz Appleova API-ja.
- Kraća ugrađena uputa i opisi poznatih alata za mali lokalni kontekst.
  Korisnikov Soul, uključena memorija i vještine ostaju dio izvornog toka.
- PCC adapter za iOS 27: tekst/slike, streaming, usage i razine razmišljanja
  light/moderate/deep, dostupan samo u izričito omogućenoj konfiguraciji.
- Appleov `Tool` predaje naziv i validirane argumente izvornom OpenMinis
  izvršitelju. Ne izvršava naredbe samostalno: postojeći mehanizam dopuštenja,
  terminal, preglednik i pohrana ostaju odgovorni za izvršenje.
- Generirana aplikacija ima vlastiti bundle ID `com.vzornjak.openminis` i naziv
  `Minis HR`; puna konfiguracija dobiva vlastite App Group/iCloud identifikatore.

Hrvatski tekst sučelja nije dokaz da Appleov model podržava hrvatski. Zaslon
Appleova pružatelja provjerava `supportsLocale(hr)` na stvarnom uređaju.
Prevodivi katalog je potpuno pokriven, ali baza prijevoda nastala je lokalnim
strojnim prevođenjem uz ručne ispravke; cjelovita jezična i vizualna provjera
na iPhoneu još nije završena. Izvorni tekstovi pomoći za terminal i logovi
nisu prevedeni ovim UI slojem.

## Besplatni Apple račun

`--personal-team` generira zasebnu razvojnu varijantu. Apple je prihvatio njezin
provisioning profil na ovom Macu. Zadržani su lokalni Apple AI, datoteke,
terminal, lokalni backup/restore te zatražene HealthKit/HomeKit ovlasti.

Bez odgovarajućih ovlasti isključeni su iCloud sync/backup, NFC, WeatherKit,
PCC i proširenja za dijeljenje, widgete i Files. Datoteke i memorija te
varijante žive u trajnom sandbox direktoriju `Library/MinisPersonalStorage`.
Nisu zamijenjeni lažnim App Group spremnikom. Uvoz/mapiranje vanjskih mapa
preko sistemskog odabira datoteka ostaje u izvornom toku.

Puna i besplatna varijanta koriste isti bundle ID; nemoj ih izmjenjivati nad
važnim podacima bez lokalne sigurnosne kopije. Prelazak iz sandbox pohrane
besplatne varijante u pravi App Group zahtijeva izvoz/obnovu ili zasebnu,
provjerenu migraciju. Razvojni profil besplatnog računa kratko vrijedi i
aplikaciju treba ponovno potpisati kada istekne.

## Appleov oblak i iOS 27

Apple ima različite lokalne i cloud modele, ali javni app API ne nudi zaseban
odabir „Cloud Pro”. Pružatelj zato izlaže **On Device** i uvjetno **Private
Cloud Compute**. Razinu razmišljanja u PCC-u ne treba zvati razinom pretplate.

PCC zahtijeva Appleovo odobrenje, odgovarajuće članstvo/programske uvjete i
potpisanu ovlast `com.apple.developer.private-cloud-compute`. Zastavica
`--pcc` to ne dodjeljuje: samo sastavlja već odobrenu aplikaciju i provjerava
ovlast u njezinu potpisu. Bez zastavice adapter ne konstruira PCC model.
Nema automatskog prelaska s lokalnog Apple modela u oblak. Korisnik i dalje
može zasebno konfigurirati izvorne OpenMinis grupe i njihove politike modela.

Izvori:
- https://developer.apple.com/documentation/foundationmodels
- https://developer.apple.com/private-cloud-compute/
- https://developer.apple.com/forums/thread/832555
- https://developer.apple.com/help/account/reference/supported-capabilities-ios

Obuhvat ove nadogradnje su Foundation Models API-ji važni za aplikaciju.
Generiranje slika ADMCloud, svi ostali iOS 27 frameworkovi i proizvoljan izbor
Core Advanced/Cloud Pro nisu implementirane mogućnosti ovog forka.

## Priprema na Macu

Xcode 27 beta s iOS 27 SDK-om. Stvarna verzija provjere: Xcode 27.0
`27A5237l`. iSH biblioteke trenutačno su za fizički iOS ARM64 uređaj;
simulator nije odgovarajuća zamjena za provjeru cijele aplikacije.

```sh
git clone https://github.com/vzornjak/OpenMinis.git
cd OpenMinis
git switch ios-hr-apple
git remote add upstream https://github.com/OpenMinis/OpenMinis.git
git submodule update --init --recursive deps/ish
mkdir -p .build/logs .build/cache/homebrew .build/cache/go .build/go
export HOMEBREW_CACHE="$PWD/.build/cache/homebrew"
export GOPATH="$PWD/.build/go"
export GOCACHE="$PWD/.build/cache/go"
export DEVELOPER_DIR=/Applications/Xcode-beta.app/Contents/Developer
export PATH="/opt/homebrew/bin:/opt/homebrew/opt/lld/bin:$PATH"
brew install ninja meson llvm lld libarchive pkgconf go
bash deps/build_lame.sh
bash deps/build_ffmpeg.sh
bash deps/build_ish.sh
bash deps/prepare_alpine_rootfs.sh
bash deps/build_rclone_ios.sh
```

`lld` je zaseban Homebrew paket. Verzije iSH-a i njegovih podmodula moraju
ostati one iz Git stabla aplikacije. Ako izvorna iSH skripta ostavi
`deps/ish/build-ios/` kao untracked, izuzmi samo `/build-ios/` u lokalnom
`.git/modules/deps/ish/info/exclude`; ne skrivaj promjene izvornog koda.

## Izgradnja i testovi

```sh
python3 scripts/fork/localize.py
python3 scripts/fork/test-provider.py
# Puna varijanta, provjera bez potpisivanja:
python3 scripts/fork/build.py
# Besplatni račun; zamijeniti TEAM_ID svojim timom:
python3 scripts/fork/build.py --personal-team --team TEAM_ID
# Samo priprema za otvaranje u Xcodeu:
python3 scripts/fork/build.py --personal-team --team TEAM_ID --prepare-only
# Testovi adaptera na povezanom iPhoneu:
python3 scripts/fork/build.py --personal-team --team TEAM_ID --device DEVICE_ID --model-smoke
# Tek kada Apple odobri PCC plaćenom timu:
python3 scripts/fork/build.py --team TEAM_ID --pcc
```

Generirani projekti su `.build/ios-source/src/ios/Minis.xcodeproj` i
`.build/ios-source-personal/src/ios/Minis.xcodeproj`. Ne uređivati ih ručno.
CLI DerivedData i aplikacije nalaze se u `.build/fork-derived` odnosno
`.build/fork-derived-personal`, pod `Build/Products/Debug-iphoneos/Minis.app`.
GUI buildovi su u `.build/gui-derived` odnosno `.build/gui-derived-personal`.
Potpisana aplikacija provjerena 13. rujna kopirana je u `.build/signed/Minis.app`.

Mac testovi koriste stvarni produkcijski adapter i njegove izvorne wire
vrste. Samo golemi katalog modela i dohvat lokalizacije imaju malu fixture
zamjenu. To provjerava protokol i predaju alata, a ne cijeli iOS runtime.
Test stvarnog modela treba `RUN_APPLE_MODEL_SMOKE=1` u testnoj okolini i
uključeni Apple Intelligence. Ne šalje podatke u oblak niti izvršava shell.

## Povlačenje novog izvornika

```sh
git switch ios-hr-apple
bash scripts/fork/update.sh
```

Skripta traži čisto radno stablo, osvježava `main` samo kada nema divergencije,
otvara `update/upstream-<sha>`, spaja izvornik i provjerava prijevode.
Nakon pregleda, potrebne obnove native ovisnosti i provjera:

```sh
git switch ios-hr-apple
git merge --ff-only update/upstream-REPLACE_WITH_SHA
git push origin main ios-hr-apple
```

GitHub Actions provjerava katalog, Personal Team prilagodbe i čistoću izvora.
CI ne tvrdi da je izgradio iOS 27 aplikaciju. Bezkonfliktni merge nije dokaz
funkcionalnosti. Minimalna provjera na iPhoneu za svako izdanje:

1. Hladno pokretanje, hrvatski jezik, odabir/dodavanje modela.
2. Lokalni odgovor bez interneta i jasna poruka kad Apple Intelligence nije dostupan.
3. Bezopasni tool poziv, prikaz potvrde gdje je predviđena, stvarni rezultat u razgovoru.
4. Terminal `printf test`, zapis/čitanje datoteke i očuvanje nakon ponovnog pokretanja.
5. Slika, prekid generiranja, duži razgovor i poruka o punom kontekstu.
6. Lokalni izvoz, obnova u testnom profilu i ponovno otvaranje datoteka.
7. Puna varijanta: zasebno Share/Files/widget, iCloud i odobreni PCC.

## Trenutačni dokaz i ograničenja

- Izgradnja pune varijante bez potpisa: **BUILD SUCCEEDED**.
- Izgradnja Personal Team varijante bez potpisa: **BUILD SUCCEEDED**.
- Mac adapter testovi: **9 prošlo, 1 preskočen, 0 grešaka**.
- Katalog: **2163/2163**, bez nedostajućih ili nevaljanih ključeva.
- Potpisivanje kroz Xcode GUI: **BUILD SUCCEEDED**, potpis i entitlementi
  provjereni s `codesign --verify --deep --strict`; instalacija na fizički
  iPhone uspješna (`com.vzornjak.openminis`). Profil vrijedi do 19. rujna 2026.
  CLI pristup ključu vraća `errSecInternalComponent`; GUI potpisivanje radi.
  iOS je zasad blokirao prvo pokretanje uz poruku o povjerenju/profilu;
  korisnik treba provjeriti povjerenje razvojnom računu na iPhoneu.
  Test stvarnog rada na uređaju još nije potvrđen.
- Apple Intelligence nije uključen na korištenom Macu, pa lokalna inferencija
  nije potvrđena. PCC nije odobren i nije pokrenut.
- Originalni build prvo je zapeo na stvarnom deployment targetu 16.0 koji
  ne odgovara korištenim API-jima, a potom na predugom SwiftUI izrazu.
  Fork postavlja iOS 27 i dijeli jedan lanac modifikatora ContentViewa.
- Bundle i podaci odvojeni su od originala. Izvorni `minis://` i `minis-mcp`
  URL protokoli ostaju zajednički: vanjsko otvaranje linka uz obje instalacije
  može završiti u aplikaciji koju odabere sustav. Ugrađeni linkovi koriste
  postojeće unutarnje usmjeravanje. Vanjski launcher/OAuth treba dodatnu
  provjeru prije paralelne svakodnevne uporabe.

Lokalni detaljni logovi su u `.build/logs/`. Izvorno istraživanje svih grana je
u susjednoj mapi `../research/openminis-2026-09-13/REPORT.md`. Buildovi,
prevoditeljski modeli i cache nisu dio javnog repozitorija. GPLv3 i izvorne
licence ostaju sačuvani.
