"""Versioned CEFR placement bank. Items are grouped by A1, A2 and B1 evidence."""
PLACEMENT_BANK_VERSION = "cefr-v2"

GRAMMAR_VOCAB = [
    # A1 foundation
    {"id":"g_a1_1","band":"A1","q":"Mam na ___ Emil.","options":["imię","imieniem","imiona"],"answer":0,"descriptor":"Can use a basic personal-introduction formula."},
    {"id":"g_a1_2","band":"A1","q":"Mieszkam ___ Krakowie.","options":["do","w","z"],"answer":1,"descriptor":"Can use a basic location expression."},
    {"id":"g_a1_3","band":"A1","q":"Codziennie ___ kawę.","options":["piję","piłem","wypiję"],"answer":0,"descriptor":"Can use a common present-tense verb."},
    {"id":"g_a1_4","band":"A1","q":"To jest ___ koleżanka.","options":["mój","moja","moje"],"answer":1,"descriptor":"Can show basic gender agreement."},
    {"id":"g_a1_5","band":"A1","q":"___ masz na imię?","options":["Gdzie","Jak","Kiedy"],"answer":1,"descriptor":"Can form a familiar personal question."},
    {"id":"g_a1_6","band":"A1","q":"Lubię ___ muzykę.","options":["polska","polską","polskiej"],"answer":1,"descriptor":"Can use a frequent accusative form."},
    # A2 everyday connected language
    {"id":"g_a2_1","band":"A2","q":"Wczoraj ___ do lekarza.","options":["idę","poszedłem/poszłam","pójdę"],"answer":1,"descriptor":"Can refer to a completed past event."},
    {"id":"g_a2_2","band":"A2","q":"Nie mam dziś ___.","options":["czas","czasu","czasem"],"answer":1,"descriptor":"Can use a common genitive after negation."},
    {"id":"g_a2_3","band":"A2","q":"Jutro ___ pracować w domu.","options":["będę","byłem","jestem"],"answer":0,"descriptor":"Can express a future plan."},
    {"id":"g_a2_4","band":"A2","q":"Ten film jest ___ niż książka.","options":["ciekawy","ciekawszy","najciekawszy"],"answer":1,"descriptor":"Can compare familiar things."},
    {"id":"g_a2_5","band":"A2","q":"Proszę powiedzieć, gdzie jest najbliższy ___.","options":["bank","banku","bankiem"],"answer":0,"descriptor":"Can manage a practical service interaction."},
    {"id":"g_a2_6","band":"A2","q":"Kiedy mieszkałem w Warszawie, często ___ metrem.","options":["jechałem raz","jeździłem","pojadę"],"answer":1,"descriptor":"Can distinguish repeated movement in the past."},
    # B1 connected and formal language
    {"id":"g_b1_1","band":"B1","q":"Uczę się polskiego, ___ zdać egzamin.","options":["żeby","chociaż","dlatego"],"answer":0,"descriptor":"Can express purpose."},
    {"id":"g_b1_2","band":"B1","q":"Gdybym miał czas, ___ częściej.","options":["czytam","czytałbym","przeczytam"],"answer":1,"descriptor":"Can express a hypothetical situation."},
    {"id":"g_b1_3","band":"B1","q":"To jest firma, w ___ pracuję od dwóch lat.","options":["której","którą","którym"],"answer":0,"descriptor":"Can use a relative clause."},
    {"id":"g_b1_4","band":"B1","q":"Mimo ___ pogody pojechaliśmy w góry.","options":["zła","złej","złą"],"answer":1,"descriptor":"Can use a concessive prepositional phrase."},
    {"id":"g_b1_5","band":"B1","q":"Uprzejmie proszę ___ potwierdzenie terminu.","options":["o","na","za"],"answer":0,"descriptor":"Can use conventional semi-formal language."},
    {"id":"g_b1_6","band":"B1","q":"Powiedziała, że nie ___ przyjść następnego dnia.","options":["może","mogła","będzie mogła"],"answer":1,"descriptor":"Can report a past statement coherently."},
]

READING_BLOCKS = [
    {"band":"A1","title":"A1: Short personal message","text":"Cześć, mam na imię Ola. Mieszkam w Poznaniu i pracuję w sklepie. Od poniedziałku do piątku zaczynam pracę o dziewiątej. Po pracy często spotykam się z koleżanką albo robię zakupy. W sobotę uczę się polskiego, a w niedzielę odpoczywam w domu.","items":[
        {"id":"r_a1_1","band":"A1","q":"Gdzie mieszka Ola?","options":["W Poznaniu","W Krakowie","W Gdańsku"],"answer":0,"descriptor":"Can identify explicit personal information."},
        {"id":"r_a1_2","band":"A1","q":"O której zaczyna pracę?","options":["O ósmej","O dziewiątej","O dziesiątej"],"answer":1,"descriptor":"Can understand a simple time reference."},
        {"id":"r_a1_3","band":"A1","q":"Co robi w sobotę?","options":["Pracuje","Uczy się polskiego","Jedzie do rodziny"],"answer":1,"descriptor":"Can locate a familiar routine detail."},
        {"id":"r_a1_4","band":"A1","q":"Jaki jest główny temat tekstu?","options":["Plan dnia Oli","Problem w pracy","Podróż do Poznania"],"answer":0,"descriptor":"Can identify the topic of a short simple text."},
    ]},
    {"band":"A2","title":"A2: Practical e-mail","text":"Dzień dobry, piszę w sprawie kursu języka polskiego. Zapisałem się na zajęcia we wtorki i czwartki o 18.00, ale od przyszłego miesiąca będę pracować do późna. Czy mogę przenieść się do grupy sobotniej? Chciałbym także wiedzieć, czy muszę kupić nowy podręcznik. Proszę o informację do końca tygodnia, ponieważ muszę ustalić grafik z pracodawcą.","items":[
        {"id":"r_a2_1","band":"A2","q":"Dlaczego autor chce zmienić grupę?","options":["Nie podoba mu się nauczyciel","Będzie dłużej pracować","Wyjeżdża z miasta"],"answer":1,"descriptor":"Can understand a reason in a practical message."},
        {"id":"r_a2_2","band":"A2","q":"Do jakiej grupy chce się przenieść?","options":["Porannej","Weekendowej","Internetowej"],"answer":1,"descriptor":"Can locate relevant practical information."},
        {"id":"r_a2_3","band":"A2","q":"O co jeszcze pyta autor?","options":["O podręcznik","O cenę mieszkania","O egzamin B2"],"answer":0,"descriptor":"Can identify multiple communicative purposes."},
        {"id":"r_a2_4","band":"A2","q":"Dlaczego odpowiedź jest potrzebna szybko?","options":["Autor musi ustalić grafik","Kurs zaczyna się jutro","Podręcznik jest przeceniony"],"answer":0,"descriptor":"Can connect information across sentences."},
    ]},
    {"band":"B1","title":"B1: Forum opinion","text":"Coraz więcej firm proponuje pracownikom pracę zdalną. Dla wielu osób oznacza to oszczędność czasu, większą elastyczność i możliwość spokojniejszego wykonywania obowiązków. Z drugiej strony brak bezpośredniego kontaktu z zespołem może utrudniać współpracę, szczególnie nowym pracownikom. Moim zdaniem najlepszym rozwiązaniem jest model hybrydowy. Pozwala on skoncentrować się w domu, ale jednocześnie daje okazję do spotkań, wymiany pomysłów i budowania relacji w biurze. Oczywiście taki system wymaga dobrej organizacji i jasnych zasad.","items":[
        {"id":"r_b1_1","band":"B1","q":"Jakie stanowisko przedstawia autor?","options":["Popiera wyłącznie pracę w biurze","Popiera model łączący dom i biuro","Odrzuca pracę zdalną"],"answer":1,"descriptor":"Can identify a viewpoint in connected text."},
        {"id":"r_b1_2","band":"B1","q":"Jaki problem może dotyczyć nowych pracowników?","options":["Brak sprzętu","Trudniejsza współpraca i integracja","Zbyt krótki czas pracy"],"answer":1,"descriptor":"Can understand an implied practical consequence."},
        {"id":"r_b1_3","band":"B1","q":"Co oznacza w tekście „z drugiej strony”?","options":["Przykład","Kontrast","Podsumowanie"],"answer":1,"descriptor":"Can interpret a discourse connector."},
        {"id":"r_b1_4","band":"B1","q":"Od czego zależy powodzenie modelu hybrydowego?","options":["Od wysokiego wynagrodzenia","Od dobrej organizacji i zasad","Od pracy tylko rano"],"answer":1,"descriptor":"Can understand a concluding condition."},
    ]},
]
READING = [item for block in READING_BLOCKS for item in block["items"]]
READING_TEXT = "\n\n".join(f"### {b['title']}\n\n{b['text']}" for b in READING_BLOCKS)

LISTENING_BLOCKS = [
    {"band":"A1","title":"A1: Voice message","text":"Cześć Aniu, tu Marek. Nasze spotkanie jest dziś o siedemnastej w kawiarni obok kina. Przyjdę kilka minut później, bo kończę pracę o szesnastej trzydzieści. Jeśli możesz, zamów mi proszę herbatę.","items":[
        {"id":"l_a1_1","band":"A1","q":"O której jest spotkanie?","options":["16:30","17:00","17:30"],"answer":1,"descriptor":"Can understand a simple time in a message."},
        {"id":"l_a1_2","band":"A1","q":"Gdzie się spotkają?","options":["W kinie","W kawiarni","W pracy"],"answer":1,"descriptor":"Can understand a familiar location."},
        {"id":"l_a1_3","band":"A1","q":"Co Ania ma zamówić?","options":["Kawę","Herbatę","Sok"],"answer":1,"descriptor":"Can understand a basic request."},
    ]},
    {"band":"A2","title":"A2: Appointment change","text":"Dzień dobry, mówi Marta Kowalska z przychodni. Dzwonię w sprawie wizyty u doktor Nowak. Pani doktor będzie jutro nieobecna. Możemy zaproponować wizytę w czwartek o dziewiątej trzydzieści albo w piątek o szesnastej. Proszę oddzwonić do godziny osiemnastej i potwierdzić wybrany termin.","items":[
        {"id":"l_a2_1","band":"A2","q":"Dlaczego termin się zmienia?","options":["Pacjent odwołał wizytę","Lekarka będzie nieobecna","Przychodnia jest zamknięta"],"answer":1,"descriptor":"Can understand a reason in a practical message."},
        {"id":"l_a2_2","band":"A2","q":"Który termin jest po południu?","options":["Czwartek 9:30","Piątek 16:00","Jutro 18:00"],"answer":1,"descriptor":"Can extract alternatives and times."},
        {"id":"l_a2_3","band":"A2","q":"Co powinien zrobić pacjent?","options":["Oddzwonić i potwierdzić","Przyjść jutro","Napisać list"],"answer":0,"descriptor":"Can understand a required action."},
    ]},
    {"band":"B1","title":"B1: Short interview","text":"Prowadzący: Czy transport publiczny może zastąpić samochód w dużym mieście? Ekspertka: W wielu sytuacjach tak, ale mieszkańcy muszą mieć częste połączenia i możliwość łatwej przesiadki. Sam zakaz wjazdu samochodów nie wystarczy. Miasto powinno równocześnie rozwijać tramwaje, autobusy i bezpieczne drogi rowerowe. Prowadzący: A co z osobami mieszkającymi poza centrum? Ekspertka: Dla nich ważne są parkingi przy stacjach, dzięki którym część podróży można odbyć samochodem, a resztę pociągiem lub tramwajem.","items":[
        {"id":"l_b1_1","band":"B1","q":"Jakie jest główne stanowisko ekspertki?","options":["Samochody trzeba natychmiast zakazać","Transport publiczny wymaga kompleksowych inwestycji","Rowery są jedynym rozwiązaniem"],"answer":1,"descriptor":"Can understand a developed viewpoint."},
        {"id":"l_b1_2","band":"B1","q":"Dlaczego sam zakaz samochodów nie wystarczy?","options":["Potrzebne są alternatywne połączenia","Mieszkańcy nie lubią tramwajów","Parkingi są bezpłatne"],"answer":0,"descriptor":"Can follow an argument and its justification."},
        {"id":"l_b1_3","band":"B1","q":"Jakie rozwiązanie proponuje osobom spoza centrum?","options":["Wyłącznie rower","Połączenie samochodu i transportu publicznego","Przeprowadzkę do centrum"],"answer":1,"descriptor":"Can understand a proposed compromise."},
    ]},
]
LISTENING = [item for block in LISTENING_BLOCKS for item in block["items"]]
LISTENING_TEXT = "\n\n".join(block["text"] for block in LISTENING_BLOCKS)

WRITING_PROMPT = {
    "instruction": "Napisz o swoim życiu w Polsce lub w swoim mieście.",
    "points": [
        "Przedstaw się i napisz, gdzie mieszkasz.",
        "Opisz, co zwykle robisz w ciągu tygodnia.",
        "Napisz o jednej rzeczy, którą robiłeś/robiłaś ostatnio.",
        "Napisz o jednym planie na przyszłość.",
        "Wyjaśnij, co jest dla Ciebie łatwe lub trudne i dlaczego.",
    ],
    "guidance": "Write as much as you can without translation tools. Quality and demonstrated ability matter more than length.",
}
SPEAKING_PROMPTS = [
    {"band":"A1","prompt":"Przedstaw się: jak masz na imię, gdzie mieszkasz, co robisz i co lubisz."},
    {"band":"A2","prompt":"Opowiedz o ostatnim weekendzie i o planach na następny weekend."},
    {"band":"B1","prompt":"Czy lepiej mieszkać w dużym mieście czy w małym mieście? Wyraź opinię i podaj powody."},
]
