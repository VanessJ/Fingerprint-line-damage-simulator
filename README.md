
## Line Damage Simulator - simulátor čiarového poškodenia

Aplikácia je schopná vygenerovať tri typy čiarového poškodenia do syntetických odtlačkov prstov, a to konkrétne:
- Vrásky a iné ryhy
- Vlas alebo chlp na snímači
- Jazvy

Pred spustením programu je potrevné nainštalovať potrebné závislosti cez:
```sh
 pip install -r requirements.txt
```
Vypísať nápovedu programu je možné cez:
```sh
 python3 main.py --help
```
Pred generovaním poškodenia je nutné zvoliť syntetický odtlačok prsta. To je možné urobiť cez parameter 
```sh
  --image synthetic_fingerprint.PNG
```
ktorý zvolí konkrétny obrázok, do ktorého sa budú generovať všetky poškodenia, alebo cez parameter
```sh
  --directory ./path_to_synthetic_fingerprint_directory
```
ktorý načíta zložku so syntetickými odtlačkami a z valídnych obrázkov náhodne vyberie odtlačky, do ktorých sa bude každé poškodenie generovať. K programu je priložená zložka ./synteticke, ktorá obsahuje 100 odtlačkov prsta vygenerovaných pomocou generátora SFinGe. Medzi ďalšie parametre patria: 

```sh
  --save ./directory_to_save_images
```
ktorá nastaví zložku, do ktorej sa budú ukladať vygenerované poškodené odtlačky. V prípade neuvedenia tohto parametru sa vytvorí či zvolí zložka ./Generated, do ktorej sa budú odtlačky generovať. 

```sh
  --name name_of_images
```
nastaví špecifický názov generovaným obrázkom. 

```sh
  --amount 100
```
upresní počet generovaných obrázkov. To je možné pomocou parametrov
```sh
  --creases
  --hair 
  --scar
```
pričom v prípade vrások je možné špecifikovať úroveň zvársnenia cez parameter --level 1/2/3, napr.
```sh
  --creases --level 1
```
pričom uvedením úrovne 1-3 sa nastaví úroveň zvrásnenia. V prípade neuvedenia úrovne je volená náhodne.

Vlasy je možné bližšie špecifikovať pomocou parametru --type (možnosti short/long pre krátky/dlhý vlas), napr. 
```sh
  --hair --type long
```
pričom long/short určí dĺžku vlasu. 

Tvar jazvy je možné bližšie špecifikovať cez parametre --length (možnosti short, medium a long pre krátku, strednú a dlhú jazvu), --orientation (možnosti horizontal, vertical a diagonal pre horizontálnu, vertikálnu alebo šikmú jazvu) a --width (možnosti thin, medium, thick pre tenkú, strednú a hrubú jazvu). Napr. príkaz

```sh
  --scar --orientation vertical --length medium --width thin
```
vygeneruje stredne dlhú, vertikálnu a tenkú jazvu. K jazvá je možné pridať ešte prídavné poškodenia: 
```sh
  --distortion
  --patches 
  --outline
```
pričom distortion skriví papilárne línie v okolí jazvy (táto možnosť je ale dostupná len pre tenké jazvy), patches vykreslí do jazvy čierne artefakty a outline vytvorí jazve čierne zrnité okraje.

V prípade neuvedenia špecifikácie sa konkrétne parametre poškodenia vyberú náhodne. 
## Príklady spustenia
```sh
  python3 main.py --directory synteticke --amount 100 --creases --level 3 --name vrasky
```
Vygeneruje sa 100 odtlačkov poškodených zvrásnením tretej úrovne, pričom jednotlivé syntetické odtlačky sa vyberú zo zložky ./synteticke a názvy súborov budú vrasky1/vrasky2 atď.

```sh
  python3 main.py --directory synteticke --amount 20 --scar --length long --width medium --patches --outline
```
Vygeneruje sa 20 odtlačkov poškodených jazvami dlhej dĺžky, strednej hrúbky a s prídavnými znakmi čiernych artefaktov a čiernych okrajov. Orientácia jazvy je nešpecifikovaná, vyberú sa teda v rámci jednotlivých obrázkov náhodne.    



