# StratyPowodziowe
projekt studencki - wtyczka programu QGIS do obliczania sumy strat powodziowych

Obliczenia przeprowadzane są zgodnie z informacjami umieszczonymi w załączniku do rozporządzenia w sprawie opracowywania map zagrożenia powodziowego oraz map ryzyka powodziowego (http://isap.sejm.gov.pl/DetailsServlet?id=WDU20130000104).

![zrut ekranu - uruchomiona wtyczka](/Obrazki/wtyczkaWAkcji1.png?raw=true)
![okienko dialogowe z potwierdzeniem zakończenia obliczeń](/Obrazki/wynikObliczenCLC.png?raw=true)

## Konfiguracja
Wartości potrzebne do obliczenia wartości strat o których mowa w załączniku do rozporządzenia, przechowywane są w plikach tekstowych:
* Majatek.txt
* Funkcja_strat.txt

## Sposób użycia wtyczki
QGIS szuka wtyczek w folderze ~/.qgis2/python/plugins, gdzie "~" oznacza katalog domowy użytkownika
(np. "/home/Mateusz" w systemie Linux lub "C:\Users\Mateusz" w systemie Windows).

Należy utworzyć folder 'plugins' np.
```bash
mkdir ~/.qgis2/python/plugins
```
i skopiować do niego zawartość tego repozytorium (np. do folderu ~/.qgis2/python/plugins/Straty).

Następnie w ustawieniach programu QGIS należy włączyć wtyczkę:
![uruchamianie wtyczki](/Obrazki/QGISwtyczkaJakUruchomić.png?raw=true)

## Ograniczenia

Mimo, że udało się przeprowadzić obliczenia z wykorzystaniem wtyczki, należy pamiętać o tym, że była ona wyłącznie projektem studenckim. Wymaga ona gruntownego dopracowania i dokładniejszych testów.
Poczyniono wiele założeń, między innymi zakłada się, że niektóre dane wejściowe są rastrami, a niektóre wektorami.
Wtyczka działa poprawnie **tylko** z wykorzystaniem warstwy rastrowej z bazy Corine Land Cover - nie próbowano testować ani przygotować jej do współpracy z innymi warstwami zapewniającymi informację o klasach użytkowania terenu
