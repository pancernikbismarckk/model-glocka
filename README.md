# Glock 17 Gen4 – model 3D (Blender)

![Podgląd modelu](preview.png)

Model 3D pistoletu **Glock 17 Gen4** wykonany w Blenderze 4.5 (render: Cycles).
Proporcje odwzorowano według oficjalnej karty wymiarów GLOCK i zdjęcia
produktowego. To model zewnętrzny, wizualny: nie zawiera mechanizmu
wewnętrznego.

Wszystkie widoki na jednym arkuszu: [`renders/preview_sheet.png`](renders/preview_sheet.png)

## Parametry

| | |
|---|---|
| Trójkąty | **19 044** (limit 30 000) |
| Poligony w pliku `.blend` | 9 535 (quady i n-gony) |
| Wymiary modelu | 201,4 × 30,4 × 138,0 mm |
| Wymiary wg specyfikacji GLOCK | długość 202 mm, zamek 186 × 25,5 mm, wysokość z magazynkiem 139 mm |
| Jednostki | metry, skala 1:1 |
| Orientacja | lufa w kierunku −X, góra +Z; lewa strona pistoletu jest po stronie −Y, więc widok *Front* w Blenderze pokazuje lewy profil |

Szerokość modelu (30,4 mm) odpowiada chwytowi zmierzonemu na rzucie z tyłu
na karcie wymiarów. Wartość 32 mm ze specyfikacji to szerokość całkowita.

## Pliki

| Plik | Zawartość |
|---|---|
| `glock17_gen4.blend` | scena z modelem, materiałami, spakowanymi teksturami, kamerą i studyjnym oświetleniem (F12 renderuje podgląd) |
| `glock17_gen4.glb` | glTF 2.0 z teksturami (Unity, Unreal, Godot, three.js, przeglądarki) |
| `glock17_gen4.fbx` | FBX z osadzonymi teksturami; siatka striangulowana, zapisane styczne |
| `preview.png` | główny obraz podglądowy (1920 × 1200) |
| `renders/` | pozostałe widoki, zbliżenia detali, render siatki i arkusz zbiorczy |
| `textures/` | mapa normalnych tekstury chwytu, grawery zamka (normal, kolor, szorstkość) |
| `scripts/` | skrypty, które odtwarzają wszystko od zera |

## Struktura modelu

Części są osobnymi obiektami podpiętymi pod pusty obiekt `Glock17_Gen4`,
więc można je animować (ruch zamka, ściągnięcie spustu, wyjęcie magazynka).

| Obiekt | Trójkąty | Zawartość |
|---|---:|---|
| `Slide` | 3 330 | zamek z fazowaną górą, 7 tylnych nacięć Gen4, okno wyrzutnika, wyciąg, muszka z białą kropką, szczerbinka z białym obrysem „U”, tylna pokrywa, grawery GLOCK / 17 Gen4 / AUSTRIA / 9x19 |
| `Barrel` | 648 | lufa z sześciokątnym (poligonalnym) przewodem, komora widoczna w oknie wyrzutnika |
| `RecoilSpringGuide` | 158 | końcówka prowadnicy sprężyny powrotnej pod lufą |
| `Frame` | 10 516 | rama polimerowa: osłona z szyną montażową (rowki i poprzeczne gniazdo), osłona spustu z karbowaniem z przodu, chwyt Gen4 z wgłębieniami na palce i teksturą RTF, „bobrzy ogon”, zatrzask rozkładania po obu stronach, kołki, osłona zatrzasku zamka, tabliczka numeru seryjnego |
| `Trigger` | 672 | spust z bezpiecznikiem (Safe Action) |
| `SlideStop` | 1 260 | zatrzask zamka z karbowaniem |
| `MagazineCatch` | 1 788 | powiększony, żebrowany zaczep magazynka Gen4 |
| `Magazine` | 672 | stopka i korpus magazynka |

## Materiały i tekstury

- **Zamek, lufa, części stalowe**: ciemny, satynowy metal (PBR, metallic).
- **Rama**: matowy czarny polimer. W Blenderze dochodzi do tego drobna
  proceduralna struktura; do glTF i FBX trafiają same wartości PBR.
- **Tekstura RTF chwytu** (`textures/grip_normal.png`, 0,1 mm/px): kwadratowe
  wypustki ułożone wzdłuż osi chwytu, żeberka we wgłębieniach na palce
  i wytłoczone logo GLOCK po obu stronach. Mapowanie UV chwytu: U to długość
  łuku przekroju mierzona od środka przedniej ścianki, V to wysokość.
- **Grawery zamka** (`textures/slide_markings_*.png`, 0,05 mm/px): rzut
  płaski lewej strony zamka.

## Jak odtworzyć model

Wymagany jest Python 3.11 i moduł Blendera z PyPI:

```bash
pip install "bpy==4.5.*" numpy pillow
python scripts/make_textures.py            # tekstury -> textures/
python scripts/build_glock17.py            # model, .blend/.glb/.fbx, rendery -> renders/
python scripts/make_sheet.py               # preview.png i renders/preview_sheet.png
```

Opcje `build_glock17.py`: `--no-render` (tylko model i eksport), `--quick`
(szybkie podglądy w niskiej rozdzielczości), `--views=hero,left,...`.
Skrypt działa też w samym Blenderze 4.2+: `blender -b -P scripts/build_glock17.py`.

- `scripts/glock_data.py`: wszystkie wymiary i profile w mm, zmierzone z karty
  wymiarów (skala 0,354 mm/px), oraz geometria przekrojów chwytu.
- `scripts/build_glock17.py`: budowa części, materiały, scena, rendery, eksport.
- `scripts/make_textures.py`: generuje tekstury (numpy + Pillow).
- `scripts/make_sheet.py`: składa obrazy podglądowe.

## Źródła

- Oficjalna karta wymiarów GLOCK 17 Gen4: długość 202 mm, zamek 186 mm,
  szerokość zamka 25,5 mm, wysokość z magazynkiem 139 mm, linia celownicza
  165 mm. Rzut boczny posłużył do zmierzenia profili zamka, ramy, osłony
  spustu, spustu, chwytu i stopki magazynka.
- Zdjęcie produktowe: rozmieszczenie i wygląd detali (nacięcia, oznaczenia,
  tekstura, zatrzaski).
