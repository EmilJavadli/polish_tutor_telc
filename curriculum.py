"""9-month (39 weeks x 7 days = 273 lessons) TELC Polski B1 preparation plan.

Week structure: days 1-6 are lessons, day 7 is a weekly review.
Every lesson trains all four TELC skills: reading, listening, writing and speaking,
plus vocabulary and grammar ("Elementy języka").
"""
from dataclasses import dataclass, field

DAYS_PER_WEEK = 7
TOTAL_WEEKS = 39
TOTAL_DAYS = DAYS_PER_WEEK * TOTAL_WEEKS  # 273

# ---------------------------------------------------------------------------
# Grammar syllabus (ordered). TELC does not publish a separate grammar list;
# this follows CEFR A1 -> B1 progression and the forms tested in the TELC
# "Elementy języka" module (expressions in conversations and semi-formal e-mails).
# ---------------------------------------------------------------------------
GRAMMAR: dict[str, tuple[str, str]] = {
    # id: (title, short hint with examples)
    # --- A1 ---
    "G01": ("Polish sounds and spelling", "sz, cz, rz/ż, ś/si, ć/ci, ą, ę, ł; stress on the penultimate syllable"),
    "G02": ("Personal pronouns and the verb 'być'", "ja jestem, ty jesteś, on/ona/ono jest, my jesteśmy..."),
    "G03": ("Noun gender", "masculine (dom), feminine (kawa), neuter (okno, mieszkanie)"),
    "G04": ("Present tense: -m/-sz verbs", "mieć: mam, masz; czytać: czytam, czytasz; znać"),
    "G05": ("Present tense: -ę/-isz/-ysz verbs", "mówić: mówię, mówisz; robić, lubić, uczyć się"),
    "G06": ("Present tense: -ę/-esz verbs", "pisać: piszę, piszesz; chcieć, iść, jechać, pić"),
    "G07": ("Questions and negation", "czy...?, kto, co, gdzie, jak; nie + verb"),
    "G08": ("Adjective agreement (nominative singular)", "dobry dom, dobra kawa, dobre okno"),
    "G09": ("Accusative singular", "mam brata, lubię kawę, widzę nowy dom / nowego kolegę"),
    "G10": ("Numbers, age and prices", "jeden, dwa...; mam trzydzieści lat; to kosztuje 12 złotych"),
    "G11": ("Possessive pronouns", "mój, moja, moje; twój, jego, jej, nasz, wasz, ich"),
    "G12": ("Instrumental singular", "jestem programistą; z mężem; interesuję się sportem"),
    "G13": ("Locative singular", "w Krakowie, na poczcie, o pracy, w sklepie"),
    "G14": ("Genitive singular", "nie mam czasu; filiżanka kawy; dom mojej mamy; do pracy"),
    "G15": ("Modal verbs + infinitive", "muszę, mogę, chcę, wolę, lubię + iść/pracować"),
    "G16": ("Time expressions", "o której? o ósmej; w poniedziałek; w maju; rano, wieczorem"),
    "G17": ("Verbs of motion: iść/jechać vs chodzić/jeździć", "idę teraz vs chodzę codziennie"),
    "G18": ("Where to / where: prepositions of place and direction", "do + gen, na + acc, w/na + loc"),
    # --- A2 ---
    "G19": ("Past tense (regular)", "byłem/byłam, robiłem/robiłam, mieli/miały"),
    "G20": ("Past tense (irregular forms)", "poszedł/poszła, mógł, jadł, wziął/wzięła"),
    "G21": ("Verb aspect: introduction", "imperfective (process/habit) vs perfective (result)"),
    "G22": ("Aspect pairs", "robić-zrobić, kupować-kupić, brać-wziąć, mówić-powiedzieć"),
    "G23": ("Future tense: imperfective", "będę pracować / będę pracował(a)"),
    "G24": ("Future tense: perfective", "zrobię, kupię, zadzwonię, napiszę"),
    "G25": ("Plural: nominative (non-masculine-personal)", "nowe domy, ładne kobiety, duże okna"),
    "G26": ("Plural: masculine-personal", "studenci, nowi koledzy; byli vs były"),
    "G27": ("Genitive plural", "dużo ludzi, kilogram jabłek, nie ma biletów"),
    "G28": ("Numerals with nouns", "dwa/trzy/cztery koty vs pięć kotów; 2 złote vs 5 złotych"),
    "G29": ("Dative of pronouns; 'podobać się', 'smakować'", "mi, ci, mu, jej; podoba mi się; smakuje ci?"),
    "G30": ("Dative singular of nouns", "dać mamie prezent, pomagać koledze, dziękuję panu"),
    "G31": ("Imperative", "zrób, zadzwoń, proszę + infinitive, niech pan usiądzie"),
    "G32": ("Reflexive verbs and 'się'", "uczyć się, spotkać się, nazywać się, wydaje się"),
    "G33": ("Comparison of adjectives", "tańszy, lepszy, najtańszy, najlepszy, bardziej interesujący"),
    "G34": ("Comparison of adverbs", "szybciej, lepiej, najczęściej, bardziej"),
    "G35": ("Personal pronouns in other cases", "mnie, cię, go, ją; ze mną, o nim, dla niej"),
    "G36": ("Formal address: Pan/Pani/Państwo", "Czy może Pan...? Proszę Pani...; Państwo mogą..."),
    # --- B1 ---
    "G37": ("Conditional mood (polite requests)", "chciałbym/chciałabym, czy mógłby Pan...?, byłbym wdzięczny"),
    "G38": ("Conditional sentences with 'gdyby'", "gdybym miał czas, pojechałbym..."),
    "G39": ("Connectors", "ponieważ, bo, więc, dlatego, chociaż, jednak, natomiast"),
    "G40": ("Relative clauses with 'który'", "kobieta, która..., dom, w którym..., kolega, z którym..."),
    "G41": ("Reported speech and indirect questions", "powiedział, że...; zapytała, czy / kiedy..."),
    "G42": ("'Żeby' (purpose, wishes)", "uczę się, żeby zdać; chcę, żebyś przyszedł"),
    "G43": ("Prefixed verbs of motion", "wyjść, przyjść, wejść, przejść, dojechać, wyjechać"),
    "G44": ("Spatial prepositions: location vs direction", "przed/za/nad/pod/między + instr vs + acc"),
    "G45": ("Locative and instrumental plural", "w sklepach, o dzieciach, z kolegami"),
    "G46": ("Dative plural and plural review", "dzieciom, rodzicom, pomagać sąsiadom"),
    "G47": ("Impersonal constructions", "można, trzeba, warto, wolno, nie należy; mówi się"),
    "G48": ("Impersonal past forms -no/-to", "zamknięto sklep, otwarto nową linię"),
    "G49": ("Passive voice", "jest/został zbudowany, będzie otwarta"),
    "G50": ("Adverbial participles", "czytając (while reading), zrobiwszy (having done) - recognition"),
    "G51": ("Adjectival participles", "pracujący, zamknięty, napisany list"),
    "G52": ("Verbal nouns", "czytanie, gotowanie, picie, zwiedzanie"),
    "G53": ("Ordinal numbers and dates", "piątego maja dwa tysiące dwudziestego szóstego roku"),
    "G54": ("Numerals with masculine-personal and collective numerals", "pięciu studentów, dwoje dzieci"),
    "G55": ("Indefinite and negative pronouns", "ktoś, coś, gdzieś; nikt nie..., nic nie... (double negation)"),
    "G56": ("Expressing opinion and arguing", "moim zdaniem, uważam, że; zgadzam się / nie zgadzam się"),
    "G57": ("Semi-formal e-mail language", "Szanowni Państwo, uprzejmie proszę, w związku z, Z poważaniem"),
    "G58": ("Prepositional phrases of cause and concession", "z powodu, dzięki, mimo, w związku z, zamiast"),
    "G59": ("Word formation", "nouns of profession (-arz, -ista, -ka), diminutives (-ek, -ka)"),
    "G60": ("Aspect in imperatives and negation", "zrób to vs nie rób tego; proszę zadzwonić"),
    "G61": ("Time prepositions", "od...do, przez tydzień, za godzinę, dwa dni temu, po pracy"),
    "G62": ("Verb + case government", "szukać + gen, pomagać + dat, interesować się + instr, myśleć o + loc"),
    "G63": ("Vocative", "Panie Tomaszu, Pani Anno, Kasiu, mamo"),
    "G64": ("Reported requests: 'prosić', 'kazać', 'żeby'", "szef prosi, żebyś zadzwonił"),
}


@dataclass(frozen=True)
class Week:
    number: int
    month: int
    phase: str
    level: str
    theme_en: str
    theme_pl: str
    situations: tuple[str, str, str, str, str, str]
    grammar: tuple[str, ...]
    writing_focus: str


PHASES = {
    1: "Foundations (A1)",
    2: "Elementary (A2)",
    3: "Intermediate (B1)",
    4: "B1 consolidation",
    5: "TELC exam training",
}

_W_A1 = "short informal message (SMS, note or e-mail to a friend)"
_W_A2 = "informal or semi-formal e-mail"
_W_B1 = "semi-formal e-mail (TELC type) answering all guiding points"

WEEKS: list[Week] = [
    # ---------------- Phase 1: A1 (months 1-2) ----------------
    Week(1, 1, PHASES[1], "A1", "Introductions", "Poznajmy się",
         ("greeting a neighbour in the stairwell", "introducing yourself to a new colleague",
          "ordering coffee in a café", "spelling your name at a reception desk",
          "exchanging phone numbers and e-mails", "saying where you come from"),
         ("G01", "G02", "G03"), _W_A1),
    Week(2, 1, PHASES[1], "A1", "Family and people", "Rodzina i ludzie",
         ("talking about your family", "describing a friend", "looking at a family photo",
          "a child's day at the nursery", "visiting grandparents", "the neighbours' family"),
         ("G04", "G05", "G07"), _W_A1),
    Week(3, 1, PHASES[1], "A1", "Home and flat", "Dom i mieszkanie",
         ("my flat in Kraków", "rooms and furniture", "viewing a flat to rent",
          "no hot water in the flat", "moving in", "what is in the kitchen"),
         ("G06", "G08", "G10"), _W_A1),
    Week(4, 1, PHASES[1], "A1", "Food and shopping", "Jedzenie i zakupy",
         ("at the bakery", "at the market", "in the supermarket",
          "prices and paying", "a shopping list", "cooking dinner at home"),
         ("G09", "G11"), _W_A1),
    Week(5, 2, PHASES[1], "A1", "Work and professions", "Praca i zawody",
         ("my job", "a day at the office", "colleagues and the boss",
          "different professions", "lunch break at work", "working from home"),
         ("G12", "G13"), _W_A1),
    Week(6, 2, PHASES[1], "A1", "Daily routine and time", "Dzień i czas",
         ("my morning", "what time is it?", "plans for the week",
          "the weekend", "appointments in the calendar", "an evening at home"),
         ("G14", "G16"), _W_A1),
    Week(7, 2, PHASES[1], "A1", "City and transport", "Miasto i transport",
         ("buying a tram ticket", "asking for directions", "taking a taxi",
          "at the railway station", "rush hour", "cycling in the city"),
         ("G15", "G17"), _W_A1),
    Week(8, 2, PHASES[1], "A1", "Free time (A1 review)", "Czas wolny",
         ("hobbies", "sport", "going to the cinema",
          "meeting friends", "a walk in the park", "a nice weekend"),
         ("G18", "G09", "G13", "G14"), _W_A1),
    # ---------------- Phase 2: A2 (months 3-4) ----------------
    Week(9, 3, PHASES[2], "A2", "What happened? (past events)", "Co się stało?",
         ("last weekend", "a trip to Zakopane", "a birthday party",
          "a visit to the doctor last week", "what I did yesterday", "a lost wallet"),
         ("G19", "G20"), _W_A2),
    Week(10, 3, PHASES[2], "A2", "Health", "Zdrowie",
         ("at the family doctor", "at the pharmacy", "booking an appointment by phone",
          "at the dentist", "a healthy lifestyle", "sick leave (L4) and calling work"),
         ("G21", "G22"), _W_A2),
    Week(11, 3, PHASES[2], "A2", "Plans and the future", "Plany na przyszłość",
         ("holiday plans", "weekend plans", "New Year's resolutions",
          "planning a child's birthday", "learning plans", "career plans"),
         ("G23", "G24"), _W_A2),
    Week(12, 3, PHASES[2], "A2", "People and relationships", "Ludzie i relacje",
         ("describing appearance", "describing character", "new colleagues",
          "neighbours", "friends from abroad", "a wedding invitation"),
         ("G25", "G26"), _W_A2),
    Week(13, 3, PHASES[2], "A2", "Shopping and services", "Zakupy i usługi",
         ("clothes and sizes", "returning a product", "online shopping and delivery",
          "post office and parcel lockers", "at the hairdresser", "shoe repair and dry cleaning"),
         ("G27", "G28"), _W_A2),
    Week(14, 4, PHASES[2], "A2", "Eating out and cooking", "Restauracja i kuchnia",
         ("booking a table", "ordering in a restaurant", "Polish cuisine",
          "a recipe", "a food delivery app", "dietary preferences"),
         ("G29", "G30"), _W_A2),
    Week(15, 4, PHASES[2], "A2", "Home life and repairs", "Sprawy domowe",
         ("a plumber's visit", "a housing community meeting", "paying the bills",
          "the building administrator", "sorting rubbish", "noisy neighbours"),
         ("G31", "G32"), _W_A2),
    Week(16, 4, PHASES[2], "A2", "Travel", "Podróże",
         ("booking a hotel", "at the hotel reception", "a train journey to Gdańsk",
          "at the airport", "renting a car", "holidays by the Baltic Sea"),
         ("G33", "G34"), _W_A2),
    Week(17, 4, PHASES[2], "A2", "Formal situations", "Sprawy urzędowe",
         ("at the bank", "opening a bank account", "at a municipal office",
          "registering your address", "phoning an institution", "filling in a form"),
         ("G35", "G36"), _W_A2),
    # ---------------- Phase 3: B1 (months 5-7) ----------------
    Week(18, 5, PHASES[3], "B1", "Looking for a job", "Szukanie pracy",
         ("job advertisements", "writing a CV", "a job interview",
          "phoning about a job offer", "types of work contracts", "the first day at a new job"),
         ("G37", "G39"), _W_B1),
    Week(19, 5, PHASES[3], "B1", "At work", "W pracy",
         ("a team meeting", "an e-mail to a colleague", "a conflict at work",
          "asking for a day off", "a business trip", "work-life balance"),
         ("G38", "G42"), _W_B1),
    Week(20, 5, PHASES[3], "B1", "Education and courses", "Edukacja i kursy",
         ("a language course", "signing up for a course", "studying in Poland",
          "online learning", "kindergarten and school", "learning as an adult"),
         ("G40", "G41"), _W_B1),
    Week(21, 5, PHASES[3], "B1", "Housing in detail", "Mieszkanie - sprawy praktyczne",
         ("renting vs buying", "a rental agreement", "complaining to the landlord",
          "a renovation", "searching for a flat online", "moving out and the deposit"),
         ("G43", "G44"), _W_B1),
    Week(22, 5, PHASES[3], "B1", "Health and lifestyle", "Zdrowie i styl życia",
         ("healthy eating", "a fitness club", "stress",
          "sleep", "public vs private healthcare", "at the hospital"),
         ("G45", "G46"), _W_B1),
    Week(23, 6, PHASES[3], "B1", "Media and technology", "Media i technologia",
         ("smartphones", "social media", "online news",
          "problems with the internet provider", "online privacy", "technology at work"),
         ("G47", "G48"), _W_B1),
    Week(24, 6, PHASES[3], "B1", "Consumer life and complaints", "Reklamacje i prawa konsumenta",
         ("a complaint about a product", "a delayed delivery", "bad service",
          "a warranty", "a customer service call", "consumer rights"),
         ("G49", "G51"), _W_B1),
    Week(25, 6, PHASES[3], "B1", "Environment and the city", "Ekologia i miasto",
         ("smog in Kraków", "public transport vs the car", "green spaces in the city",
          "recycling", "climate and weather", "a local city initiative"),
         ("G50", "G52"), _W_B1),
    Week(26, 6, PHASES[3], "B1", "Culture and traditions", "Kultura i tradycje",
         ("Christmas Eve and Easter", "name days", "a concert",
          "a museum visit", "Polish cinema", "a book I read"),
         ("G53", "G54"), _W_B1),
    Week(27, 7, PHASES[3], "B1", "Free time and travel", "Wolny czas i wyjazdy",
         ("hiking in the mountains", "travelling with a child", "a package tour vs travelling alone",
          "camping", "a city break", "problems when travelling"),
         ("G55", "G62"), _W_B1),
    Week(28, 7, PHASES[3], "B1", "Society and opinions", "Społeczeństwo i opinie",
         ("living abroad", "volunteering", "generations",
          "family models", "working parents", "foreigners in Poland"),
         ("G56", "G57"), _W_B1),
    Week(29, 7, PHASES[3], "B1", "Money and finances", "Pieniądze i finanse",
         ("a household budget", "a bank loan", "saving money",
          "taxes", "prices and inflation", "insurance"),
         ("G58", "G61"), _W_B1),
    Week(30, 7, PHASES[3], "B1", "Everyday problems", "Problemy codzienne",
         ("a lost document", "a car breakdown and the mechanic", "a misunderstanding",
          "asking for help", "an accident at home", "the emergency number 112"),
         ("G59", "G60", "G63", "G64"), _W_B1),
    # ---------------- Phase 4: consolidation (month 8) ----------------
    Week(31, 8, PHASES[4], "B1", "Offices and administration", "Urzędy i formalności",
         ("a residence card appointment", "collecting documents", "at the voivodeship office",
          "changing your address", "sworn translation of documents", "social insurance and benefits"),
         ("G09", "G14", "G27", "G28"), _W_B1),
    Week(32, 8, PHASES[4], "B1", "Children and family life", "Dzieci i życie rodzinne",
         ("kindergarten enrolment", "a sick child", "at the playground",
          "parental leave", "a family weekend", "a children's party"),
         ("G21", "G22", "G24", "G60"), _W_B1),
    Week(33, 8, PHASES[4], "B1", "Career and development", "Kariera i rozwój",
         ("a promotion", "a training course", "a presentation at work",
          "remote vs office work", "negotiating", "retirement"),
         ("G37", "G38", "G42", "G64"), _W_B1),
    Week(34, 8, PHASES[4], "B1", "Services and appointments", "Usługi i rezerwacje",
         ("a car service", "a phone repair", "booking a beautician",
          "a dance course for adults", "a gym membership", "cancelling a contract"),
         ("G40", "G41", "G39", "G58"), _W_B1),
    Week(35, 8, PHASES[4], "B1", "Current issues", "Aktualne tematy",
         ("car-free city centres", "working hours", "children's screen time",
          "tourism in Kraków", "healthy food in schools", "Sunday shopping ban"),
         ("G62", "G47", "G49", "G51"), _W_B1),
    # ---------------- Phase 5: TELC training (month 9) ----------------
    Week(36, 9, PHASES[5], "B1", "TELC writing: semi-formal e-mails", "Pisanie: e-maile półoficjalne",
         ("asking about a course", "a complaint to a hotel", "changing a booking",
          "a request to the landlord", "asking a school for information", "applying for voluntary work"),
         ("G57", "G36", "G37"), _W_B1),
    Week(37, 9, PHASES[5], "B1", "TELC speaking: experiences, presentations, discussions",
         "Mówienie: doświadczenia, prezentacja, dyskusja",
         ("talking about a past experience", "presenting a topic", "describing pictures",
          "giving your opinion", "pros and cons", "answering follow-up questions"),
         ("G56", "G39", "G41"), _W_B1),
    Week(38, 9, PHASES[5], "B1", "TELC listening and reading strategies", "Strategie: słuchanie i czytanie",
         ("voice messages", "everyday dialogues", "a radio interview",
          "internet forum posts", "advertisements and notices", "official information"),
         ("G43", "G62", "G58"), _W_B1),
    Week(39, 9, PHASES[5], "B1", "Final review", "Powtórka końcowa",
         ("everyday life", "work", "health", "travel", "services", "society"),
         ("G57", "G56", "G28"), _W_B1),
]

# Rotations for lesson days 1-6 (day 7 = weekly review)
TEXT_TYPES = (
    "e-mail",
    "internet forum: a question and 2-3 answers",
    "short advertisements and notices (3-4 texts)",
    "narrative story",
    "official information text (rules, regulations, announcement)",
    "magazine article or blog post",
)
LISTENING_TYPES = (
    "voice messages (TELC Listening part 1: 2-3 short phone messages)",
    "everyday dialogue (TELC Listening part 2)",
    "interview (TELC Listening part 3)",
    "different opinions on one topic (TELC Listening part 4: 3 speakers)",
    "everyday dialogue (TELC Listening part 2)",
    "voice messages (TELC Listening part 1: 2-3 short phone messages)",
)
SPEAKING_PARTS = (1, 2, 3, 1, 2, 3)

SPEAKING_PART_NAMES = {
    1: "Part 1: talking about your experiences and opinions",
    2: "Part 2: short presentation",
    3: "Part 3: discussion on a controversial topic",
}

READING_LENGTH = {"A1": (110, 170), "A2": (170, 250), "B1": (250, 350)}
LISTENING_LENGTH = {"A1": (60, 110), "A2": (100, 170), "B1": (150, 250)}
WRITING_LENGTH = {"A1": (30, 60), "A2": (60, 100), "B1": (100, 150)}


@dataclass(frozen=True)
class PlanDay:
    day: int
    week: int
    day_of_week: int
    month: int
    phase: str
    level: str
    theme_en: str
    theme_pl: str
    situation: str
    lesson_type: str            # "lesson" | "review"
    grammar_ids: tuple[str, str, str]
    text_type: str
    listening_type: str
    speaking_part: int
    writing_focus: str
    reading_length: tuple[int, int] = field(default=(0, 0))
    listening_length: tuple[int, int] = field(default=(0, 0))
    writing_length: tuple[int, int] = field(default=(0, 0))

    @property
    def grammar_titles(self) -> list[str]:
        return [GRAMMAR[g][0] for g in self.grammar_ids]


def _earlier_grammar(week_number: int) -> list[str]:
    seen: list[str] = []
    for w in WEEKS[: week_number - 1]:
        for g in w.grammar:
            if g not in seen:
                seen.append(g)
    return seen


def _grammar_for_day(week: Week, dow: int, day: int) -> tuple[str, str, str]:
    """3 grammar points: the day's focus point from the week's list, then other
    week points, then spaced review of earlier weeks."""
    own = list(week.grammar)
    if dow == DAYS_PER_WEEK:          # review day: the week's own points first
        chosen = own[:3]
    else:
        start = (dow - 1) % len(own)
        rotated = own[start:] + own[:start]
        chosen = rotated[:2] if len(rotated) >= 2 else rotated[:]
    pool = [g for g in _earlier_grammar(week.number) if g not in chosen]
    i = day
    while len(chosen) < 3 and pool:
        candidate = pool[i % len(pool)]
        chosen.append(candidate)
        pool.remove(candidate)
        i += 7
    for g in own:                      # week 1 fallback
        if len(chosen) >= 3:
            break
        if g not in chosen:
            chosen.append(g)
    return tuple(chosen[:3])  # type: ignore[return-value]


def get_plan_day(day: int) -> PlanDay:
    """Return the plan for lesson `day` (1..273). Days beyond the plan repeat the final week."""
    if day < 1:
        raise ValueError("day must be >= 1")
    capped = min(day, TOTAL_DAYS)
    week = WEEKS[(capped - 1) // DAYS_PER_WEEK]
    dow = (capped - 1) % DAYS_PER_WEEK + 1
    is_review = dow == DAYS_PER_WEEK
    idx = dow - 1
    return PlanDay(
        day=day,
        week=week.number,
        day_of_week=dow,
        month=week.month,
        phase=week.phase,
        level=week.level,
        theme_en=week.theme_en,
        theme_pl=week.theme_pl,
        situation=f"weekly review: {week.theme_en}" if is_review else week.situations[idx],
        lesson_type="review" if is_review else "lesson",
        grammar_ids=_grammar_for_day(week, dow, day),
        text_type="e-mail with a reply" if is_review else TEXT_TYPES[idx],
        listening_type=LISTENING_TYPES[1] if is_review else LISTENING_TYPES[idx],
        speaking_part=2 if is_review else SPEAKING_PARTS[idx],
        writing_focus=week.writing_focus,
        reading_length=READING_LENGTH[week.level],
        listening_length=LISTENING_LENGTH[week.level],
        writing_length=WRITING_LENGTH[week.level],
    )


def plan_markdown() -> str:
    """The whole plan as Markdown (used for PLAN.md and the in-app download)."""
    lines = [
        "# 9-month TELC Polski B1 plan (1 hour a day)",
        "",
        "39 weeks x 7 days = 273 lessons. Days 1-6: new lesson; day 7: weekly review.",
        "Every lesson trains reading, listening, vocabulary, grammar (Elementy języka), "
        "writing and speaking.",
        "",
        "| Month | Week | Phase | Level | Theme | Grammar focus | Writing |",
        "|---|---|---|---|---|---|---|",
    ]
    for w in WEEKS:
        grammar = "; ".join(GRAMMAR[g][0] for g in w.grammar)
        lines.append(f"| {w.month} | {w.number} | {w.phase} | {w.level} | "
                     f"{w.theme_en} ({w.theme_pl}) | {grammar} | {w.writing_focus} |")
    lines += ["", "## Daily situations", ""]
    for w in WEEKS:
        lines.append(f"**Week {w.number}: {w.theme_en}**: " + "; ".join(w.situations))
        lines.append("")
    return "\n".join(lines)
