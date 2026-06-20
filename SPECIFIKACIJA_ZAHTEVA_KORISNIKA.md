**SPECIFIKACIJA ZAHTEVA KORISNIKA**

Sistem za upravljanje servisom računara (Servis Racunara)

| Verzija: | 1.0 |
| :---- | :---- |
| **Datum:** | Jun 2026 |
| **Autor:** | Veljko Kovacevic SI 17/21 |
| **Predmet:** | Testiranje softvera |

# **SADRŽAJ**

1. Uvod

2. Pregled sistema

3. Funkcionalni zahtevi (REQ_0001 – REQ_0012)

4. Specifikacija korisničkog interfejsa

5. Scenariji korišćenja

6. Plan testiranja

# **1. UVOD**

## **1.1 Svrha dokumenta**

Ovaj dokument opisuje funkcionalne zahteve za sistem **Servis Racunara** — web aplikaciju za upravljanje servisom računara. Dokument je namenjen razvojnom timu, testerima i korisnicima sistema.

## **1.2 Opseg**

* Prijava i odjava zaposlenih u backoffice sistemu

* Kreiranje i praćenje servisnih slučajeva (repair cases)

* Evidencija događaja na slučaju (napomene, dijagnoza, popravka)

* Upravljanje inventarom rezervnih delova

* Evidencija rada i korišćenja delova pri popravci

* Generisanje, plaćanje i povlačenje faktura

* Javna provera statusa popravke za klijente (broj telefona + referentni kod)

* Validacija unosa podataka i prikaz poruka o greškama

## **1.3 Ciljna grupa**

* **Korisnici sistema:** Administratori i tehničari servisa računara koji koriste backoffice aplikaciju

* **Krajnji korisnici:** Klijenti koji prate status popravke putem javne stranice za pretragu

* **Razvojni tim:** Programeri koji implementiraju sistem

* **Testeri:** Osobe koje testiraju sistem (unit, integracioni i sistemski testovi)

# **2. PREGLED SISTEMA**

## **2.1 Opis sistema**

Servis Racunara je full-stack web aplikacija za upravljanje radom servisa računara. Sistem omogućava zaposlenima da vode servisne slučajeve od prijema uređaja do zatvaranja nakon plaćanja, uz praćenje zaliha delova i izdavanje faktura. Klijenti mogu samostalno proveriti status popravke unosom broja telefona i referentnog koda sa prijemnice.

## **2.2 Glavne funkcionalnosti**

* **Autentifikacija:** Prijava zaposlenih, zaštita ruta, odjava

* **Servisni slučajevi:** Kreiranje, pregled, pretraga, filtriranje po statusu, dodavanje događaja

* **Inventar:** Dodavanje delova, izmena podataka, prilagođavanje zaliha, upozorenje o niskim zalihama

* **Popravke:** Evidencija korišćenih delova i rada, automatsko smanjenje zaliha

* **Fakture:** Generisanje iz delova i rada, obračun poreza, plaćanje, povlačenje

* **Javna pretraga:** Pregled javno vidljivih događaja na slučaju nakon verifikacije telefona

## **2.3 Tehnologije**

| Komponenta | Tehnologija |
| ----- | ----- |
| Frontend | Vue 3, TypeScript, Vite, Pinia, Vue Router |
| Backend | Python 3, FastAPI, SQLAlchemy 2, Pydantic |
| Baza podataka | MariaDB |
| Kontejnerizacija | Docker Compose |
| Testiranje (backend) | pytest, httpx, FastAPI TestClient |
| Testiranje (frontend) | Vitest, Vue Test Utils |

# **3. FUNKCIONALNI ZAHTEVI**

## **REQ_0001: Prijava i odjava korisnika**

**Prioritet:** Visok (5)

**Rizik:** Visok (4)

**Metod verifikacije:** Integracioni test — `test_login_me_logout_flow`

### **Opis**

Sistem mora omogućiti zaposlenom da se prijavi korisničkim imenom i lozinkom, pristupi zaštićenim funkcijama, proveri trenutno prijavljenog korisnika i odjavi se.

### **Preduslovi**

* Backend i frontend aplikacije su pokrenuti

* U bazi postoji aktivni korisnik sa validnom lozinkom

* Korisnik nije prijavljen

### **Korisnički koraci**

1. Korisnik otvara stranicu `/login`

2. Unosi korisničko ime i lozinku

3. Klikne na dugme **Sign in**

4. Sistem preusmerava korisnika na stranicu slučajeva (`/cases`)

5. Korisnik klikne **Log out** u bočnoj navigaciji

### **Očekivani rezultati**

* Uspešna prijava postavlja HTTP-only session kolačić

* Endpoint `GET /api/auth/me` vraća podatke o prijavljenom korisniku

* Neispravni kredencijali vraćaju status 401 i poruku *"Invalid username or password"*

* Odjava briše session kolačić i blokira pristup zaštićenim rutama

### **Kriterijumi prihvatanja**

* Samo autentifikovani korisnici pristupaju backoffice rutama

* Neautentifikovani korisnici se preusmeravaju na `/login`

* Prijavljeni korisnici ne mogu ponovo pristupiti `/login`

* Integracioni test prolazi bez greške

### **Poruke o greškama**

*"Invalid username or password"*

*"Not authenticated"*

*"Invalid session"*

---

## **REQ_0002: Kreiranje servisnog slučaja**

**Prioritet:** Visok (5)

**Rizik:** Srednji (3)

**Metod verifikacije:** Integracioni test (deo `test_repair_event_deducts_part_stock`, `test_invoice_generate_then_mark_paid_closes_case`)

### **Opis**

Sistem mora omogućiti tehničaru da otvori novi servisni slučaj sa podacima o klijentu i uređaju.

### **Preduslovi**

* Korisnik je prijavljen

* Otvorena je stranica **Cases**

### **Korisnički koraci**

1. Korisnik klikne **New case**

2. Popunjava polja: ime klijenta, telefon, tip/branding/model uređaja, prijavljeni kvar, prioritet

3. Klikne **Create case**

### **Očekivani rezultati**

* Slučaj se čuva u bazi sa statusom `open`

* Sistem generiše jedinstveni broj tiketa u formatu `REP-XXXX`

* Kreira se početni događaj tipa `note` sa opisom prijavljenog kvara

* Novi slučaj se pojavljuje u listi slučajeva

### **Kriterijumi prihvatanja**

* Sva obavezna polja moraju biti popunjena

* Broj tiketa je jedinstven

* Slučaj je dodeljen prijavljenom korisniku

### **Pravila validacije**

* Ime klijenta, telefon, tip uređaja, brend, model i opis kvara ne smeju biti prazni

* Dužine polja moraju biti u dozvoljenim granicama (Pydantic validacija)

---

## **REQ_0003: Pregled i pretraga slučajeva**

**Prioritet:** Visok (4)

**Rizik:** Nizak (2)

**Metod verifikacije:** Manualno testiranje

### **Opis**

Sistem mora prikazati listu servisnih slučajeva sa mogućnošću filtriranja po statusu i pretrage po ključnim rečima.

### **Preduslovi**

* Korisnik je prijavljen

* U bazi postoje servisni slučajevi

### **Korisnički koraci**

1. Korisnik otvara stranicu **Cases**

2. Biramo tab statusa: All, Open, In Progress, Awaiting Payment, Closed

3. Opciono unosi pojam za pretragu (tiket, ime, telefon, brend, model)

### **Očekivani rezultati**

* Lista prikazuje slučajeve sortirane po datumu kreiranja (najnoviji prvi)

* Filtriranje po statusu vraća samo slučajeve u tom statusu

* Pretraga radi po broju tiketa, imenu klijenta, telefonu, brendu i modelu

* Klik na red otvara detalje slučaja u modalu

### **Kriterijumi prihvatanja**

* Prikazani su svi relevantni podaci (tiket, klijent, uređaj, status, prioritet, dodeljeni tehničar)

* Pretraga se izvršava sa odloženim učitavanjem (debounce ~300 ms)

---

## **REQ_0004: Dodavanje događaja na slučaj**

**Prioritet:** Visok (5)

**Rizik:** Srednji (3)

**Metod verifikacije:** Integracioni test — `test_repair_event_deducts_part_stock`

### **Opis**

Sistem mora omogućiti dodavanje događaja na otvoreni slučaj: napomenu, dijagnozu ili popravku.

### **Preduslovi**

* Korisnik je prijavljen

* Slučaj postoji i nije zaključan (`is_locked = false`)

### **Korisnički koraci**

1. Korisnik otvori detalje slučaja

2. Klikne **Add update**

3. Bira tip događaja: Note, Diagnosis ili Repair

4. Unosi opis i opciono označava **Visible to customer**

5. Za tip Repair dodaje delove i/ili rad

6. Klikne **Save update**

### **Očekivani rezultati**

* Događaj se čuva i prikazuje u hronologiji slučaja

* Javni događaji (`is_public = true`) postaju vidljivi klijentu na stranici za pretragu

* Događaji tipa `repair` mogu sadržati delove i rad; ostali tipovi ne

### **Kriterijumi prihvatanja**

* Zaključani slučajevi ne dozvoljavaju nove događaje

* Delovi i rad mogu se dodati samo na događaj tipa `repair`

* Opis događaja ne sme biti prazan

### **Poruke o greškama**

*"Cannot modify a closed case"*

*"Case is locked while an invoice is pending or paid"*

*"Parts and labor can only be added on repair updates"*

---

## **REQ_0005: Evidencija delova pri popravci i smanjenje zaliha**

**Prioritet:** Visok (5)

**Rizik:** Visok (4)

**Metod verifikacije:** Integracioni test — `test_repair_event_deducts_part_stock`; Unit test — `test_case_edit_blocked_when_closed_or_invoiced`

### **Opis**

Sistem mora pri popravci evidentirati korišćene delove, kreirati zapis o potrošnji i automatski smanjiti količinu na lageru.

### **Preduslovi**

* Korisnik je prijavljen

* Postoji aktivan slučaj i delovi sa dovoljnom zalihom

### **Korisnički koraci**

1. Korisnik kreira događaj tipa **Repair**

2. Dodaje jedan ili više delova sa količinom

3. Čuva događaj

### **Očekivani rezultati**

* Za svaki deo kreira se `PartUsage` zapis sa cenom u trenutku korišćenja

* `quantity_on_hand` dela se smanjuje za unetu količinu

* Ako nema dovoljno zaliha, operacija se odbija

### **Kriterijumi prihvatanja**

* Zalihe se ne mogu spustiti ispod nule

* Neaktivni ili nepostojeći delovi se odbijaju

* Integracioni test potvrđuje smanjenje zaliha (npr. sa 5 na 3 pri korišćenju 2 komada)

### **Poruke o greškama**

*"Not enough stock for {naziv_dela}"*

*"Part {id} not found"*

---

## **REQ_0006: Upravljanje inventarom**

**Prioritet:** Visok (4)

**Rizik:** Srednji (3)

**Metod verifikacije:** Manualno testiranje

### **Opis**

Sistem mora omogućiti upravljanje katalogom rezervnih delova: dodavanje, izmenu, prilagođavanje zaliha i filtriranje.

### **Preduslovi**

* Korisnik je prijavljen

* Otvorena je stranica **Inventory**

### **Korisnički koraci**

1. Korisnik dodaje novi deo preko **New part** (naziv, cena, količina, kategorija, prag niskih zaliha)

2. Selektuje deo iz liste i menja podatke u panelu detalja

3. Prilagođava zalihe unosom delte (+/-) i klikom **Apply**

4. Filtrira po kategoriji, pretražuje po nazivu, opciono prikazuje neaktivne delove

### **Očekivani rezultati**

* Novi delovi se pojavljuju u listi

* Zalihe se ažuriraju bez negativnih vrednosti

* Delovi ispod praga prikazuju indikator niskih zaliha (`is_low_stock`)

* Neaktivni delovi se ne nude pri popravci

### **Kriterijumi prihvatanja**

* Cena i količina su numerički validni

* Prilagođavanje zaliha koje bi rezultovalo negativnom vrednošću se odbija

### **Poruke o greškama**

*"Stock cannot go below zero"*

---

## **REQ_0007: Generisanje fakture iz slučaja**

**Prioritet:** Visok (5)

**Rizik:** Visok (4)

**Metod verifikacije:** Integracioni test — `test_invoice_generate_then_mark_paid_closes_case`; Unit test — `test_invoice_is_active_for_pending_and_paid_only`

### **Opis**

Sistem mora generisati fakturu na osnovu evidentiranih delova i rada na slučaju, sa obračunom poreza prema podešavanjima radnje.

### **Preduslovi**

* Korisnik je prijavljen

* Slučaj ima bar jedan evidentiran deo ili rad

* Slučaj nema aktivnu fakturu (pending/paid)

* Slučaj nije zatvoren

### **Korisnički koraci**

1. Korisnik otvori detalje slučaja

2. Klikne **Generate payment**

### **Očekivani rezultati**

* Kreira se faktura sa brojem `INV-XXXX`

* Stavke fakture obuhvataju materijal (delove) i rad

* Obračunavaju se subtotal, porez i ukupan iznos

* Status slučaja prelazi u `awaiting_payment`

* Slučaj postaje zaključan za izmene (`is_locked = true`)

### **Kriterijumi prihvatanja**

* Faktura se ne može generisati bez delova ili rada

* Ne može se generisati druga aktivna faktura dok postoji pending/paid

* Porez se računa prema `default_tax_rate` iz podešavanja radnje

* Integracioni test potvrđuje tačan obračun (npr. subtotal 3500 + 20% porez = 4200 RSD)

### **Poruke o greškama**

*"Add parts or labor on the case before generating payment"*

*"This case already has an active invoice"*

*"Cannot generate payment for a closed case"*

---

## **REQ_0008: Plaćanje fakture i zatvaranje slučaja**

**Prioritet:** Visok (5)

**Rizik:** Srednji (3)

**Metod verifikacije:** Integracioni test — `test_invoice_generate_then_mark_paid_closes_case`

### **Opis**

Sistem mora omogućiti označavanje fakture kao plaćene i automatsko zatvaranje povezanog slučaja.

### **Preduslovi**

* Postoji faktura u statusu `pending`

* Korisnik je prijavljen

### **Korisnički koraci**

1. Korisnik otvori detalje slučaja sa pending fakturom

2. Klikne **Mark paid**

### **Očekivani rezultati**

* Status fakture prelazi u `paid`

* Postavlja se `paid_at` timestamp

* Status slučaja prelazi u `closed`

* Postavlja se `closed_at` timestamp

* Kreira se interna napomena o plaćanju

### **Kriterijumi prihvatanja**

* Samo pending fakture mogu biti plaćene

* Zatvoreni slučaj ostaje zaključan

* Integracioni test potvrđuje promenu statusa i postojanje `closed_at`

### **Poruke o greškama**

*"Case has no pending invoice"*

---

## **REQ_0009: Povlačenje (retrakcija) fakture**

**Prioritet:** Srednji (3)

**Rizik:** Srednji (3)

**Metod verifikacije:** Manualno testiranje

### **Opis**

Sistem mora omogućiti povlačenje pending fakture uz obavezno navođenje razloga, vraćanjem slučaja u rad.

### **Preduslovi**

* Postoji faktura u statusu `pending`

* Slučaj je u statusu `awaiting_payment`

### **Korisnički koraci**

1. Korisnik otvori detalje slučaja

2. Klikne **Retract invoice**

3. Unosi razlog povlačenja

4. Potvrđuje akciju

### **Očekivani rezultati**

* Status fakture prelazi u `cancelled`

* Čuva se razlog i vreme povlačenja

* Status slučaja vraća se u `in_progress`

* Slučaj ponovo postaje dostupan za izmene

### **Kriterijumi prihvatanja**

* Samo pending fakture mogu biti povučene

* Razlog ne sme biti prazan

### **Poruke o greškama**

*"Only a pending invoice can be retracted"*

---

## **REQ_0010: Javna provera statusa popravke**

**Prioritet:** Visok (4)

**Rizik:** Visok (4)

**Metod verifikacije:** Unit testovi — `test_normalize_phone_strips_non_digits_and_converts_381_prefix`, `test_phones_match_accepts_equivalent_numbers`

### **Opis**

Sistem mora omogućiti klijentu da proveri status popravke unosom broja telefona i referentnog koda (broj tiketa), bez prijave.

### **Preduslovi**

* Aplikacija je dostupna na ruti `/lookup`

* U bazi postoji slučaj sa odgovarajućim tiketom i telefonom

### **Korisnički koraci**

1. Klijent otvara stranicu **Track your repair**

2. Unosi broj telefona i referentni kod (npr. `REP-0002`)

3. Klikne **Look up**

### **Očekivani rezultati**

* Prikazuju se osnovni podaci o slučaju i status

* Prikazuju se samo javni događaji (`is_public = true`)

* Neispravna kombinacija telefona i koda vraća 404

* Upoređivanje telefona podržava različite formate (+381, razmaci, crtice)

### **Kriterijumi prihvatanja**

* Neautentifikovani pristup je dozvoljen samo za ovu rutu

* Podaci o internim napomenama nisu vidljivi klijentu

* Unit testovi potvrđuju normalizaciju i poklapanje telefonskih brojeva

### **Poruke o greškama**

*"No case found matching that phone and reference code."*

---

## **REQ_0011: Bezbednost sesije**

**Prioritet:** Visok (5)

**Rizik:** Visok (5)

**Metod verifikacije:** Unit test — `test_verify_session_token_round_trip_and_rejects_invalid`; Integracioni test — `test_login_me_logout_flow`

### **Opis**

Sistem mora koristiti bezbedne session tokene sa HMAC potpisom i rokom važenja.

### **Preduslovi**

* Korisnik se uspešno prijavio

### **Očekivani rezultati**

* Token sadrži ID korisnika i vreme isteka

* Token je potpisan HMAC-SHA256 ključem aplikacije

* Neispravan, izmenjen ili istekao token se odbija

* Session kolačić je HTTP-only

### **Kriterijumi prihvatanja**

* Rok važenja sesije je 8 sati

* `verify_session_token` vraća `None` za nevalidne tokene

* Unit test pokriva validan token, tampered potpis i istek

---

## **REQ_0012: Pravila zaključavanja slučaja**

**Prioritet:** Visok (4)

**Rizik:** Srednji (3)

**Metod verifikacije:** Unit testovi — `test_invoice_is_active_for_pending_and_paid_only`, `test_case_edit_blocked_when_closed_or_invoiced`

### **Opis**

Sistem mora sprečiti izmene na zatvorenim slučajevima i slučajevima sa aktivnom fakturom.

### **Preduslovi**

* Postoji slučaj u statusu `closed` ili sa pending/paid fakturom

### **Očekivani rezultati**

* Zatvoren slučaj: blokirane izmene sa porukom o zatvorenom slučaju

* Slučaj sa aktivnom fakturom: blokirane izmene sa porukom o zaključanju

* Slučaj u radu bez aktivne fakture: izmene su dozvoljene

* `invoice_is_active` vraća `true` samo za pending i paid statuse

### **Kriterijumi prihvatanja**

* Poslovna pravila su konzistentna na API i UI nivou (`is_locked` flag)

* Unit testovi pokrivaju sve grane logike

### **Poruke o greškama**

*"Cannot modify a closed case"*

*"Case is locked while an invoice is pending or paid"*

# **4. SPECIFIKACIJA KORISNIČKOG INTERFEJSA**

## **4.1 Backoffice aplikacija**

Backoffice koristi layout sa bočnom navigacijom (**DashboardLayout**) i sledećim stranicama:

| Ruta | Komponenta | Opis |
| ----- | ----- | ----- |
| `/login` | LoginView | Forma za prijavu |
| `/cases` | CasesView | Lista servisnih slučajeva |
| `/inventory` | InventoryView | Lista delova i panel detalja |
| `/invoices` | InvoicesView | Lista faktura |

### **4.1.1 Stranica Cases**

| Element | Tip | Opis |
| ----- | ----- | ----- |
| Search input | Text | Pretraga slučajeva |
| Status tabs | Tab dugmad | Filter po statusu |
| New case | Dugme | Otvara NewCaseModal |
| Tabela slučajeva | Tabela | Prikaz liste; klik otvara CaseDetailModal |
| CaseDetailModal | Modal | Detalji, događaji, akcije fakture |

### **4.1.2 Stranica Inventory**

| Element | Tip | Opis |
| ----- | ----- | ----- |
| Search input | Text | Pretraga delova |
| Category filter | Select | Filter po kategoriji |
| Show inactive | Checkbox | Prikaz neaktivnih delova |
| New part | Dugme | Otvara NewPartModal |
| PartDetailPanel | Panel | Izmena dela i prilagođavanje zaliha |

### **4.1.3 Stranica Invoices**

| Element | Tip | Opis |
| ----- | ----- | ----- |
| Status tabs | Tab dugmad | Filter po statusu fakture |
| Tabela faktura | Tabela | Prikaz lista; klik otvara InvoiceDetailModal |

### **4.1.4 Bočna navigacija**

| Element | Funkcija |
| ----- | ----- |
| Cases | Pregled servisnih slučajeva |
| Inventory | Upravljanje zalihama |
| Invoices | Pregled faktura |
| Log out | Odjava korisnika |

## **4.2 Javna stranica za pretragu**

| Ruta | Komponenta | Opis |
| ----- | ----- | ----- |
| `/lookup` | PublicLookupView | Javna pretraga statusa popravke |

| Element | Tip | Opis |
| ----- | ----- | ----- |
| Phone number | Tel input | Broj telefona klijenta |
| Reference code | Text input | Broj tiketa (REP-XXXX) |
| Look up | Dugme | Pokreće pretragu |
| Rezultat | Panel | Status, uređaj, javni događaji |

# **5. SCENARIJI KORIŠĆENJA**

## **Scenario 1: Prijem uređaja i otvaranje slučaja**

**Akter:** Tehničar

1. Tehničar se prijavljuje u sistem

2. Otvara **Cases** i klikne **New case**

3. Unosi podatke o klijentu i laptopu sa prijavljenim kvarom

4. Sistem kreira slučaj `REP-0001` u statusu Open

**Rezultat:** Servisni slučaj je otvoren i vidljiv u listi.

## **Scenario 2: Popravka sa korišćenjem delova**

**Akter:** Tehničar

1. Tehničar otvara detalje slučaja

2. Dodaje događaj tipa **Repair** sa delom „SSD 512GB", količina 2

3. Sistem smanjuje zalihe sa 5 na 3

**Rezultat:** Popravka je evidentirana, zalihe su ažurirane.

## **Scenario 3: Fakturisanje i zatvaranje slučaja**

**Akter:** Administrator / tehničar

1. Nakon završetka rada tehničar generiše fakturu

2. Sistem obračunava iznos sa porezom i zaključava slučaj

3. Po prijemu uplate korisnik označava fakturu kao plaćenu

4. Slučaj prelazi u status Closed

**Rezultat:** Faktura je plaćena, slučaj je zatvoren.

## **Scenario 4: Klijent proverava status popravke**

**Akter:** Klijent

1. Klijent otvara `/lookup`

2. Unosi broj telefona sa prijemnice i kod `REP-0002`

3. Sistem prikazuje status i javne događaje (npr. dijagnozu označenu kao vidljivu klijentu)

**Rezultat:** Klijent je informisan o toku popravke bez pristupa internim podacima.

# **6. PLAN TESTIRANJA**

Sistem se testira na tri nivoa, u skladu sa zahtevima predmeta Testiranje softvera.

## **6.1 Pregled nivoa testiranja**

| Nivo | Broj testova | Cilj | Alat |
| ----- | ----- | ----- | ----- |
| Unit | 5 | Testiranje pojedinačnih funkcija u izolaciji | pytest |
| Integracioni | 3 | Testiranje saradnje više komponenti/klasa | pytest + TestClient |
| Sistemski | 2 | Testiranje kompletnog toka iz perspektive korisnika | Manualno / E2E (planirano) |

## **6.2 Unit testovi (5)**

| ID | Test | Zahtev | Proverava |
| ----- | ----- | ----- | ----- |
| UT-01 | `test_normalize_phone_strips_non_digits_and_converts_381_prefix` | REQ_0010 | `normalize_phone()` — uklanjanje formatiranja i konverzija +381 prefiksa |
| UT-02 | `test_phones_match_accepts_equivalent_numbers` | REQ_0010 | `phones_match()` — poklapanje brojeva u različitim formatima |
| UT-03 | `test_verify_session_token_round_trip_and_rejects_invalid` | REQ_0011 | `verify_session_token()` — validan, izmenjen i istekao token |
| UT-04 | `test_invoice_is_active_for_pending_and_paid_only` | REQ_0007, REQ_0012 | `invoice_is_active()` — aktivni statusi fakture |
| UT-05 | `test_case_edit_blocked_when_closed_or_invoiced` | REQ_0004, REQ_0012 | `case_edit_blocked()` — pravila zaključavanja slučaja |

**Pokretanje:**

```bash
cd BE
source .venv/bin/activate
pytest -m unit -v
```

## **6.3 Integracioni testovi (3)**

| ID | Test | Zahtev | Proverava |
| ----- | ----- | ----- | ----- |
| IT-01 | `test_login_me_logout_flow` | REQ_0001, REQ_0011 | Auth router + session + `get_current_user` — login, `/me`, logout |
| IT-02 | `test_repair_event_deducts_part_stock` | REQ_0002, REQ_0004, REQ_0005 | Cases router + repair service + inventory — smanjenje zaliha |
| IT-03 | `test_invoice_generate_then_mark_paid_closes_case` | REQ_0005, REQ_0007, REQ_0008 | Invoice service + cases — generisanje, porez, plaćanje, zatvaranje |

**Pokretanje:**

```bash
cd BE
source .venv/bin/activate
pytest -m integration -v
```

## **6.4 Sistemski testovi (2) — planirano**

| ID | Scenario | Opis | Zahtevi |
| ----- | ----- | ----- | ----- |
| ST-01 | Kompletan tok servisa | Prijava → novi slučaj → popravka sa delovima → faktura → plaćanje → provera zatvorenog statusa | REQ_0001 – REQ_0008 |
| ST-02 | Tok klijenta | Javna pretraga sa ispravnim i pogrešnim podacima, provera vidljivosti javnih događaja | REQ_0010 |

Sistemski testovi se izvode manualno kroz UI (frontend + backend + baza) ili automatizovano E2E alatom (npr. Playwright) — nisu još implementirani u kodu.

## **6.5 Mapiranje zahtev ↔ test**

| Zahtev | Unit | Integracioni | Sistemski |
| ----- | ----- | ----- | ----- |
| REQ_0001 | — | IT-01 | ST-01 |
| REQ_0002 | — | IT-02, IT-03 | ST-01 |
| REQ_0003 | — | — | ST-01 |
| REQ_0004 | UT-05 | IT-02 | ST-01 |
| REQ_0005 | UT-05 | IT-02 | ST-01 |
| REQ_0006 | — | — | ST-01 |
| REQ_0007 | UT-04 | IT-03 | ST-01 |
| REQ_0008 | — | IT-03 | ST-01 |
| REQ_0009 | — | — | ST-01 |
| REQ_0010 | UT-01, UT-02 | — | ST-02 |
| REQ_0011 | UT-03 | IT-01 | ST-01 |
| REQ_0012 | UT-04, UT-05 | IT-03 | ST-01 |

## **6.6 Struktura test fajlova**

```
BE/
├── pytest.ini
└── tests/
    ├── conftest.py
    ├── unit/
    │   ├── test_phone.py
    │   ├── test_session.py
    │   └── test_invoice_rules.py
    └── integration/
        ├── test_auth_flow.py
        ├── test_repair_inventory.py
        └── test_invoice_lifecycle.py
```
