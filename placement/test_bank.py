"""Reviewed placement items. Keep versioned and stable for comparable results."""
GRAMMAR_VOCAB=[
{'id':'g1','band':'A1','q':'Mam na ___ Emil.','options':['imię','imięm','imiona'],'answer':0},
{'id':'g2','band':'A1','q':'Mieszkam ___ Krakowie.','options':['do','w','z'],'answer':1},
{'id':'g3','band':'A1','q':'Codziennie ___ kawę.','options':['piję','piłem','wypiję'],'answer':0},
{'id':'g4','band':'A2','q':'Wczoraj ___ do lekarza.','options':['idę','poszedłem/poszłam','pójdę'],'answer':1},
{'id':'g5','band':'A2','q':'Nie mam dziś ___.','options':['czas','czasu','czasem'],'answer':1},
{'id':'g6','band':'A2','q':'Jutro ___ pracować w domu.','options':['będę','byłem','jestem'],'answer':0},
{'id':'g7','band':'B1','q':'Uczę się polskiego, ___ zdać egzamin.','options':['żeby','chociaż','dlatego'],'answer':0},
{'id':'g8','band':'B1','q':'Gdybym miał czas, ___ częściej.','options':['czytam','czytałbym','przeczytam'],'answer':1},
]
READING_TEXT='''Anna mieszka w Krakowie od trzech lat. Pracuje w małej firmie informatycznej. Do pracy zwykle jedzie tramwajem, ale w piątki pracuje z domu. W zeszłym tygodniu zapisała się na kurs języka polskiego, ponieważ chce swobodniej rozmawiać z sąsiadami i załatwiać sprawy w urzędzie. Zajęcia odbywają się dwa razy w tygodniu wieczorem.'''
READING=[
{'id':'r1','band':'A1','q':'Gdzie mieszka Anna?','options':['W Warszawie','W Krakowie','W Gdańsku'],'answer':1},
{'id':'r2','band':'A1','q':'Jak zwykle jedzie do pracy?','options':['Tramwajem','Samochodem','Pociągiem'],'answer':0},
{'id':'r3','band':'A2','q':'Kiedy pracuje z domu?','options':['W poniedziałki','W środy','W piątki'],'answer':2},
{'id':'r4','band':'A2','q':'Dlaczego zapisała się na kurs?','options':['Chce zmienić pracę','Chce lepiej komunikować się po polsku','Chce studiować informatykę'],'answer':1},
{'id':'r5','band':'B1','q':'Które stwierdzenie najlepiej opisuje cel Anny?','options':['Potrzebuje polskiego głównie do podróży','Chce używać polskiego w życiu społecznym i formalnym','Chce uczyć polskiego innych'],'answer':1},
]
LISTENING_TEXT='''Dzień dobry, mówi Marta Kowalska z przychodni. Dzwonię w sprawie wizyty u doktor Nowak. Niestety pani doktor będzie jutro nieobecna. Możemy zaproponować wizytę w czwartek o dziewiątej trzydzieści albo w piątek o szesnastej. Proszę oddzwonić do godziny osiemnastej i potwierdzić wybrany termin.'''
LISTENING=[
{'id':'l1','band':'A1','q':'Skąd dzwoni Marta?','options':['Z przychodni','Ze szkoły','Z banku'],'answer':0},
{'id':'l2','band':'A1','q':'Kogo dotyczy wizyta?','options':['Doktor Nowak','Doktor Kowalskiej','Dentysty'],'answer':0},
{'id':'l3','band':'A2','q':'Dlaczego termin się zmienia?','options':['Pacjent nie może przyjść','Lekarka będzie nieobecna','Przychodnia jest zamknięta'],'answer':1},
{'id':'l4','band':'A2','q':'Który termin jest po południu?','options':['Czwartek 9:30','Piątek 16:00','Jutro 18:00'],'answer':1},
{'id':'l5','band':'B1','q':'Co powinien zrobić pacjent?','options':['Przyjść bez potwierdzenia','Oddzwonić i wybrać termin','Napisać do lekarki'],'answer':1},
]
