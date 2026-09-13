# Hrvatski odgovori Appleova modela

Provjera 13. rujna 2026., iPhone 15 Pro, iOS 27, lokalni
`SystemLanguageModel.default`. Produkcijski adapter OpenMinisa, bez cloud
modela i bez izvršavanja naredbi u jezičnom pokusu.

## Što je popravljeno

Izvorni Soul izbornik i `minis-config` shema nudili su samo `auto`, `zh` i
`en`. `lang` se spremao u SOUL.md, ali se nije prenosio u sistemsku uputu.
Dodan je `hr`, zajednički popis vrijednosti i prijenos odabranog jezika u
`SystemPromptBuilder.identitySection()`. Apple dobiva istu jezičnu uputu,
uključujući izričit zahtjev za standardnim hrvatskim i latiničnim pismom.

## Stvarni izlazi prvog pokusa

Tri svježe sesije: hrvatsko pitanje o plavom nebu; englesko pitanje o istom
uz zahtjev za hrvatskim odgovorom; hrvatsko pitanje o korijenima biljke
nakon kratkog primjera hrvatskog pozdrava. Odgovor nije zadan u primjeru.

```text
supportsLocale(hr): false
Attempt 1: Nebo je plavo zbog raznolikih svjetlosnih promjena tijekom trajanja svjetlosti s Zemlje.
Attempt 2: Bilo je što svjetlo se odbija u atmosferi, što čini svijetlo što je više u području crvenog svjetla.
Attempt 3: Korijeni biljke zaštitavaju trajno sadržan u njima nutrični elementi.
```

Model prihvaća pokušaj hrvatskog iako ga `supportsLocale(hr)` ne oglašava.
Izlazi imaju gramatičke i činjenične pogreške. Ovo potvrđuje mogućnost
usmjeravanja jezika, ne pouzdanu jezičnu ili stručnu kvalitetu. Probe test
bilježi i normalizira eventualnu grešku nepodržanog jezika; njegova prolaznost
sama po sebi nije mjera kvalitete odgovora.

Ne blokiramo poziv na temelju `supportsLocale(hr)`. Ako Apple ipak vrati
`unsupportedLanguageOrLocale`, aplikacija prikazuje razumljivu poruku.
Nema automatskog cloud fallbacka ni dodatnog prevoditeljskog servisa.

[Appleova dokumentacija greške jezika](https://developer.apple.com/documentation/foundationmodels/languagemodelerror/unsupportedlanguageorlocale)

Sirovi rezultati, logovi i potpisi buildova nalaze se lokalno u `.build/`.

## Provjere i prekidi na uređaju

- Mac: 10 prošlo, 2 stvarna model testa preskočena, bez grešaka.
- Prvi novi skup na iPhoneu: 12 prošlo, jedan test prekinut signalom KILL.
  Provjera spremanja/učitavanja hrvatskog i sva tri jezična pokušaja prošli su.
- Prekinuti test stvarnog poziva alata zatim je zasebno prošao za 6,575 sekundi.
- Ponovljeni puni skup ponovno je prekinut: log bilježi da je aplikacija
  prelazila u pozadinu tijekom inferencije, zatim KILL i problem ponovnog
  pokretanja testnog procesa. Točan uzrok KILL-a nije potvrđen; ne prikazujemo
  novu skupinu kao potpuno prolaznu. Nije pronađen odgovarajući Minis crash
  zapis ili Jetsam zapis za vrijeme testa. To samo po sebi ne isključuje
  sistemski prekid.

Artefakti: `.build/device-tests-language.xcresult`,
`.build/device-tests-language-tool-retry.xcresult`,
`.build/device-tests-language-confirmation.xcresult`,
`.build/logs/provider-tests-language.log`.
