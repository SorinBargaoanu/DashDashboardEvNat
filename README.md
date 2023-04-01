# Dashboard pentru Evaluarea Națională

Acest proiect conține un dashboard interactiv realizat cu ajutorul Dash, care analizează și prezintă evoluția notelor elevilor la Evaluarea Națională din România. Datele provin de la https://data.gov.ro/en/dataset?q=evaluare+nationala și sunt încărcate în format CSV.

## Funcționalități

Utilizatorii pot selecta diferite opțiuni pentru a vizualiza evoluția notelor în funcție de următoarele criterii:

- Nota finală la limba română
- Nota finală la matematică
- Media finală
- Media generală pe clasele V-VIII

De asemenea, utilizatorii pot grupa rezultatele în funcție de:

- Genul elevului
- Mediul în care elevul provine (urban sau rural)

## Instalare

1. Clonează acest repository pe mașina ta locală.
2. Instalează Python 3.7 sau o versiune ulterioară.
3. (Opțional) Creează un mediu virtual Python pentru a instala pachetele necesare.
4. Rulează `pip install -r requirements.txt` pentru a instala dependențele necesare.

## Rularea proiectului

După ce ai instalat dependențele, poți rula proiectul cu următoarea comandă:

`python app.py`


Apoi, deschide un browser și accesează http://127.0.0.1:8050 pentru a vizualiza dashboard-ul.
