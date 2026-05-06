#!/usr/bin/env python3
"""Fix Slovenian diacritic loss in a generated HTML report.

The subagent that authors review-sentiment HTML routinely strips č/š/ž
from common Slovenian words. This is a comprehensive in-place fixer that
covers every diacritic loss observed across the Bled Rose, NEU Residences,
Habakuk, and Sava runs.

Usage:
    python3 fix_diacritics.py <path/to/report.html>

It rewrites the file in place and prints a summary. Run it as the final
step of every booking-review-report build.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


# Each entry: (regex pattern, replacement). Replacement may be a string OR a
# lambda(re.Match) -> str for stem-preserving substitutions.
#
# Coverage strategy:
#   1) Common Slovenian word stems that lose č/š/ž to ASCII rendering.
#   2) Country names with diacritics.
#   3) Section titles and report-specific phrases that recurred across runs.
#
# Order matters: more specific patterns should come BEFORE general stem rules
# so a longer match wins. Each pattern uses \b word boundaries to avoid
# breaking surrounding HTML/CSS.

FIXES: list[tuple[str, object]] = [
    # ====== exact-word fixes (highest priority) ======
    (r'\bvsec\b', 'všeč'), (r'\bVsec\b', 'Všeč'),
    (r'\bvšec\b', 'všeč'), (r'\bVšec\b', 'Všeč'),
    (r'\bvec\b', 'več'), (r'\bVec\b', 'Več'),
    (r'\bcas\b', 'čas'), (r'\bCas\b', 'Čas'),
    (r'\bnoc\b', 'noč'), (r'\bNoc\b', 'Noč'),
    (r'\bze\b', 'že'), (r'\bZe\b', 'Že'),
    (r'\bsele\b', 'šele'), (r'\bSele\b', 'Šele'),
    (r'\bsest\b', 'šest'), (r'\bSest\b', 'Šest'),
    (r'\bsola\b', 'šola'), (r'\bSola\b', 'Šola'),
    (r'\bdrzi\b', 'drži'), (r'\bDrzi\b', 'Drži'),
    (r'\bzeli\b', 'želi'), (r'\bZeli\b', 'Želi'),
    (r'\bzelis\b', 'želiš'), (r'\bZelis\b', 'Želiš'),
    (r'\bzene\b', 'žene'), (r'\bZene\b', 'Žene'),
    (r'\bzena\b', 'žena'), (r'\bZena\b', 'Žena'),
    (r'\bdalec\b', 'daleč'), (r'\bDalec\b', 'Daleč'),
    (r'\btisoc\b', 'tisoč'), (r'\bTisoc\b', 'Tisoč'),
    (r'\bsodec\b', 'sodeč'), (r'\bSodec\b', 'Sodeč'),
    (r'\bskoda\b', 'škoda'), (r'\bSkoda\b', 'Škoda'),
    (r'\bvazno\b', 'važno'), (r'\bVazno\b', 'Važno'),
    (r'\bmozno\b', 'možno'), (r'\bMozno\b', 'Možno'),
    (r'\bmocna\b', 'močna'), (r'\bmocno\b', 'močno'),
    (r'\bmocan\b', 'močan'), (r'\bMocno\b', 'Močno'),
    (r'\bmogoce\b', 'mogoče'), (r'\bMogoce\b', 'Mogoče'),
    (r'\bplaca\b', 'plača'), (r'\bplaco\b', 'plačo'),
    (r'\bpijaca\b', 'pijača'), (r'\bPijaca\b', 'Pijača'),
    (r'\bvecina\b', 'večina'), (r'\bVecina\b', 'Večina'),
    (r'\breseno\b', 'rešeno'), (r'\bReseno\b', 'Rešeno'),
    (r'\bresena\b', 'rešena'), (r'\bresene\b', 'rešene'),
    (r'\bresen(\w*)', lambda m: 'rešen' + m.group(1)),
    (r'\bvsi\b', 'vsi'),  # safe (vsi is correct in Slovenian)

    # ====== diacritic-preserving stem patterns ======

    # ---- č ----
    (r'\bMesecn(\w*)', lambda m: 'Mesečn' + m.group(1)),
    (r'\bmesecn(\w*)', lambda m: 'mesečn' + m.group(1)),
    (r'\bKljucn(\w*)', lambda m: 'Ključn' + m.group(1)),
    (r'\bkljucn(\w*)', lambda m: 'ključn' + m.group(1)),
    (r'\bPovprecn(\w*)', lambda m: 'Povprečn' + m.group(1)),
    (r'\bpovprecn(\w*)', lambda m: 'povprečn' + m.group(1)),
    (r'\bpovprecje\b', 'povprečje'), (r'\bPovprecje\b', 'Povprečje'),
    (r'\bpovprecju\b', 'povprečju'),
    (r'\bNacrt(\w*)', lambda m: 'Načrt' + m.group(1)),
    (r'\bnacrt(\w*)', lambda m: 'načrt' + m.group(1)),
    (r'\bNacin(\w*)', lambda m: 'Način' + m.group(1)),
    (r'\bnacin(\w*)', lambda m: 'način' + m.group(1)),
    (r'\bnacelom\b', 'načelom'), (r'\bnacelno\b', 'načelno'),
    (r'\bZnacil(\w*)', lambda m: 'Značil' + m.group(1)),
    (r'\bznacil(\w*)', lambda m: 'značil' + m.group(1)),
    (r'\bZnacaj(\w*)', lambda m: 'Značaj' + m.group(1)),
    (r'\bznacaj(\w*)', lambda m: 'značaj' + m.group(1)),
    (r'\bznacka\b', 'značka'), (r'\bznacke\b', 'značke'),
    (r'\bspecifin(\w*)', lambda m: 'specifičn' + m.group(1)),
    (r'\bspecificn(\w*)', lambda m: 'specifičn' + m.group(1)),
    (r'\bSpecifin(\w*)', lambda m: 'Specifičn' + m.group(1)),
    (r'\bSpecificn(\w*)', lambda m: 'Specifičn' + m.group(1)),
    (r'\bSestev(\w*)', lambda m: 'Seštev' + m.group(1)),
    (r'\bsestev(\w*)', lambda m: 'seštev' + m.group(1)),
    (r'\bTezav(\w*)', lambda m: 'Težav' + m.group(1)),
    (r'\btezav(\w*)', lambda m: 'težav' + m.group(1)),
    (r'\bTezk(\w*)', lambda m: 'Težk' + m.group(1)),
    (r'\btezk(\w*)', lambda m: 'težk' + m.group(1)),
    (r'\bcasov(\w*)', lambda m: 'časov' + m.group(1)),
    (r'\bCasov(\w*)', lambda m: 'Časov' + m.group(1)),
    (r'\bcasa\b', 'časa'), (r'\bcasu\b', 'času'), (r'\bcasi\b', 'časi'),
    (r'\bvecj(\w*)', lambda m: 'večj' + m.group(1)),
    (r'\bVecj(\w*)', lambda m: 'Večj' + m.group(1)),
    (r'\bvecino\b', 'večino'), (r'\bvecini\b', 'večini'),
    (r'\bvecinoma\b', 'večinoma'),
    (r'\bnajvec(\w*)', lambda m: 'največ' + m.group(1)),
    (r'\bNajvec(\w*)', lambda m: 'Največ' + m.group(1)),
    (r'\bnajvecja\b', 'največja'), (r'\bNajvecja\b', 'Največja'),
    (r'\bnoci\b', 'noči'), (r'\bNoci\b', 'Noči'),
    (r'\bnocn(\w*)', lambda m: 'nočn' + m.group(1)),
    (r'\btocke\b', 'točke'), (r'\btocka\b', 'točka'),
    (r'\bTocka\b', 'Točka'), (r'\btocko\b', 'točko'),
    (r'\btisoce\b', 'tisoče'),
    (r'\brazlicn(\w*)', lambda m: 'različn' + m.group(1)),
    (r'\bRazlicn(\w*)', lambda m: 'Različn' + m.group(1)),
    (r'\bnatancn(\w*)', lambda m: 'natančn' + m.group(1)),
    (r'\bNatancn(\w*)', lambda m: 'Natančn' + m.group(1)),
    (r'\bvkljuc(\w*)', lambda m: 'vključ' + m.group(1)),
    (r'\bVkljuc(\w*)', lambda m: 'Vključ' + m.group(1)),
    (r'\bizkljuc(\w*)', lambda m: 'izključ' + m.group(1)),
    (r'\bIzkljuc(\w*)', lambda m: 'Izključ' + m.group(1)),
    (r'\bvecjezicn(\w*)', lambda m: 'večjezičn' + m.group(1)),
    (r'\bpricakuj(\w*)', lambda m: 'pričakuj' + m.group(1)),
    (r'\bPricakuj(\w*)', lambda m: 'Pričakuj' + m.group(1)),
    (r'\bpricakov(\w*)', lambda m: 'pričakov' + m.group(1)),
    (r'\bPricakov(\w*)', lambda m: 'Pričakov' + m.group(1)),
    (r'\bpovzroca\b', 'povzroča'), (r'\bpovzroci\b', 'povzroči'),
    (r'\bpovzrocaj(\w*)', lambda m: 'povzročaj' + m.group(1)),
    (r'\bpovzrocij(\w*)', lambda m: 'povzročij' + m.group(1)),
    (r'\boznacit(\w*)', lambda m: 'označit' + m.group(1)),
    (r'\bOznacit(\w*)', lambda m: 'Označit' + m.group(1)),
    (r'\boznacen(\w*)', lambda m: 'označen' + m.group(1)),
    (r'\bOznacen(\w*)', lambda m: 'Označen' + m.group(1)),
    (r'\boznaceval(\w*)', lambda m: 'označeval' + m.group(1)),
    (r'\boznacuj(\w*)', lambda m: 'označuj' + m.group(1)),
    (r'\bplace\b', 'plače'),
    (r'\bplacljiv(\w*)', lambda m: 'plačljiv' + m.group(1)),
    (r'\bPlacljiv(\w*)', lambda m: 'Plačljiv' + m.group(1)),
    (r'\bdoplacil(\w*)', lambda m: 'doplačil' + m.group(1)),
    (r'\bDoplacil(\w*)', lambda m: 'Doplačil' + m.group(1)),
    (r'\bdoplaca\b', 'doplača'),
    (r'\bzacet(\w*)', lambda m: 'začet' + m.group(1)),
    (r'\bZacet(\w*)', lambda m: 'Začet' + m.group(1)),
    (r'\bzacasn(\w*)', lambda m: 'začasn' + m.group(1)),
    (r'\bZacasn(\w*)', lambda m: 'Začasn' + m.group(1)),
    (r'\bzacne(\w*)', lambda m: 'začne' + m.group(1)),
    (r'\bzascit(\w*)', lambda m: 'zaščit' + m.group(1)),
    (r'\bZascit(\w*)', lambda m: 'Zaščit' + m.group(1)),
    (r'\bzakljucek\b', 'zaključek'),
    (r'\bZakljucek\b', 'Zaključek'),
    (r'\bzakljuck(\w*)', lambda m: 'zaključk' + m.group(1)),
    (r'\bsodelujoc(\w*)', lambda m: 'sodelujoč' + m.group(1)),
    (r'\bvplivajoc(\w*)', lambda m: 'vplivajoč' + m.group(1)),
    (r'\bizstopajoc(\w*)', lambda m: 'izstopajoč' + m.group(1)),
    (r'\bIzstopajoc(\w*)', lambda m: 'Izstopajoč' + m.group(1)),
    (r'\bdolocen(\w*)', lambda m: 'določen' + m.group(1)),
    (r'\bDolocen(\w*)', lambda m: 'Določen' + m.group(1)),
    (r'\bdolocit(\w*)', lambda m: 'določit' + m.group(1)),
    (r'\bDolocit(\w*)', lambda m: 'Določit' + m.group(1)),
    (r'\budolocenost\b', 'določenost'),
    (r'\bucinkovit(\w*)', lambda m: 'učinkovit' + m.group(1)),
    (r'\bUcinkovit(\w*)', lambda m: 'Učinkovit' + m.group(1)),
    (r'\bneucinkov(\w*)', lambda m: 'neučinkov' + m.group(1)),
    (r'\bNeucinkov(\w*)', lambda m: 'Neučinkov' + m.group(1)),
    (r'\bizrecn(\w*)', lambda m: 'izrečn' + m.group(1)),
    (r'\bizracun(\w*)', lambda m: 'izračun' + m.group(1)),
    (r'\bIzracun(\w*)', lambda m: 'Izračun' + m.group(1)),
    (r'\bnajmocnejs(\w*)', lambda m: 'najmočnejš' + m.group(1)),
    (r'\bNajmocnejs(\w*)', lambda m: 'Najmočnejš' + m.group(1)),
    (r'\bmocn(?=[aeiou])\w*', lambda m: 'močn' + m.group()[4:]),
    (r'\bMocn(?=[aeiou])\w*', lambda m: 'Močn' + m.group()[4:]),
    (r'\bpodrocn(\w*)', lambda m: 'področn' + m.group(1)),
    (r'\bPodrocn(\w*)', lambda m: 'Področn' + m.group(1)),
    (r'\bpodrocj(\w*)', lambda m: 'področj' + m.group(1)),
    (r'\bPodrocj(\w*)', lambda m: 'Področj' + m.group(1)),
    (r'\bpodrocij\b', 'področij'),
    (r'\bpocasen\b', 'počasen'),
    (r'\bpocasn(\w*)', lambda m: 'počasn' + m.group(1)),
    (r'\bPocasn(\w*)', lambda m: 'Počasn' + m.group(1)),
    (r'\bpravocasn(\w*)', lambda m: 'pravočasn' + m.group(1)),
    (r'\bPravocasn(\w*)', lambda m: 'Pravočasn' + m.group(1)),
    (r'\bvecerj(\w*)', lambda m: 'večerj' + m.group(1)),
    (r'\bVecerj(\w*)', lambda m: 'Večerj' + m.group(1)),
    (r'\bcakal(\w*)', lambda m: 'čakal' + m.group(1)),
    (r'\bCakal(\w*)', lambda m: 'Čakal' + m.group(1)),
    (r'\bcakaln(\w*)', lambda m: 'čakaln' + m.group(1)),
    (r'\bcakat(\w*)', lambda m: 'čakat' + m.group(1)),
    (r'\bneobicajno\b', 'neobičajno'),
    (r'\bNeobicajno\b', 'Neobičajno'),
    (r'\bneobicajn(\w*)', lambda m: 'neobičajn' + m.group(1)),
    (r'\bneocisc(\w*)', lambda m: 'neočišč' + m.group(1)),
    (r'\bNeocisc(\w*)', lambda m: 'Neočišč' + m.group(1)),
    (r'\bcisc(\w*)', lambda m: 'čišč' + m.group(1)),
    (r'\bCisc(\w*)', lambda m: 'Čišč' + m.group(1)),
    (r'\bljubljenc(\w*)', lambda m: 'ljubljenč' + m.group(1)),
    (r'\bsporoc(\w*)', lambda m: 'sporoč' + m.group(1)),
    (r'\bSporoc(\w*)', lambda m: 'Sporoč' + m.group(1)),
    (r'\bodloc(?=[aeiouv])\w*', lambda m: 'odloč' + m.group()[5:]),
    (r'\bOdloc(?=[aeiouv])\w*', lambda m: 'Odloč' + m.group()[5:]),
    (r'\bnaroc(?=[aeiou])\w*', lambda m: 'naroč' + m.group()[5:]),
    (r'\bNaroc(?=[aeiou])\w*', lambda m: 'Naroč' + m.group()[5:]),
    (r'\bneupravicen(\w*)', lambda m: 'neupravičen' + m.group(1)),
    (r'\bobcutk(\w*)', lambda m: 'občutk' + m.group(1)),
    (r'\bObcutk(\w*)', lambda m: 'Občutk' + m.group(1)),
    (r'\bobcutek\b', 'občutek'),
    (r'\bObcutek\b', 'Občutek'),
    (r'\bobcutljivost(\w*)', lambda m: 'občutljivost' + m.group(1)),
    (r'\bobcutimo\b', 'občutimo'),
    (r'\bobcuti\b', 'občuti'),
    (r'\bsvetlec(\w*)', lambda m: 'svetleč' + m.group(1)),
    (r'\bSvetlec(\w*)', lambda m: 'Svetleč' + m.group(1)),
    (r'\bomogocil(\w*)', lambda m: 'omogočil' + m.group(1)),
    (r'\bomogoca\b', 'omogoča'),
    (r'\bomogocaj(\w*)', lambda m: 'omogočaj' + m.group(1)),
    (r'\bomogocij(\w*)', lambda m: 'omogočij' + m.group(1)),
    (r'\bporocaj(\w*)', lambda m: 'poročaj' + m.group(1)),
    (r'\bporocali\b', 'poročali'),
    (r'\bporocilo\b', 'poročilo'),
    (r'\bPorocilo\b', 'Poročilo'),
    (r'\bporocil(\w*)', lambda m: 'poročil' + m.group(1)),
    (r'\bPorocil(\w*)', lambda m: 'Poročil' + m.group(1)),
    (r'\bpomocj(\w*)', lambda m: 'pomočj' + m.group(1)),
    (r'\bpomoc\b', 'pomoč'),
    (r'\bPomoc\b', 'Pomoč'),
    (r'\bcezmern(\w*)', lambda m: 'čezmern' + m.group(1)),
    (r'\bCezmern(\w*)', lambda m: 'Čezmern' + m.group(1)),
    (r'\bpremocen\b', 'premočen'),
    (r'\bPremocen\b', 'Premočen'),
    (r'\bpremocno\b', 'premočno'),
    (r'\bpriporoc(?=il|en|am|aj)\w*', lambda m: 'priporoč' + m.group()[8:]),
    (r'\bPriporoc(?=il|en|am|aj)\w*', lambda m: 'Priporoč' + m.group()[8:]),
    (r'\bposamicn(\w*)', lambda m: 'posamičn' + m.group(1)),
    (r'\bPosamicn(\w*)', lambda m: 'Posamičn' + m.group(1)),
    (r'\bneobstojec(\w*)', lambda m: 'neobstoječ' + m.group(1)),
    (r'\bNeobstojec(\w*)', lambda m: 'Neobstoječ' + m.group(1)),

    # ---- š ----
    (r'\bsibk(\w*)', lambda m: 'šibk' + m.group(1)),
    (r'\bSibk(\w*)', lambda m: 'Šibk' + m.group(1)),
    (r'\bnajsibkejs(\w*)', lambda m: 'najšibkejš' + m.group(1)),
    (r'\bsirok(\w*)', lambda m: 'širok' + m.group(1)),
    (r'\bSirok(\w*)', lambda m: 'Širok' + m.group(1)),
    (r'\bsiri\b', 'širi'),
    (r'\bsirj(\w*)', lambda m: 'širj' + m.group(1)),
    (r'\bsole\b', 'šole'),
    (r'\bSteviln(\w*)', lambda m: 'Številn' + m.group(1)),
    (r'\bsteviln(\w*)', lambda m: 'številn' + m.group(1)),
    (r'\bstevilo\b', 'število'),
    (r'\bStevilo\b', 'Število'),
    (r'\bstevilom\b', 'številom'),
    (r'\bstevilu\b', 'številu'),
    (r'\bstevila\b', 'števila'),
    (r'\bskode\b', 'škode'),
    (r'\bskodljiv(\w*)', lambda m: 'škodljiv' + m.group(1)),
    (r'\bsplosn(\w*)', lambda m: 'splošn' + m.group(1)),
    (r'\bSplosn(\w*)', lambda m: 'Splošn' + m.group(1)),
    (r'\bnasteti\b', 'našteti'),
    (r'\bnastetih\b', 'naštetih'),
    (r'\bnasteva(\w*)', lambda m: 'našteva' + m.group(1)),
    (r'\bizboljsa(\w*)', lambda m: 'izboljša' + m.group(1)),
    (r'\bIzboljsa(\w*)', lambda m: 'Izboljša' + m.group(1)),
    (r'\bizboljs(?=a|e|i|u)\w*', lambda m: 'izboljš' + m.group()[7:]),
    (r'\bIzboljs(?=a|e|i|u)\w*', lambda m: 'Izboljš' + m.group()[7:]),
    (r'\bnajboljs(\w*)', lambda m: 'najboljš' + m.group(1)),
    (r'\bNajboljs(\w*)', lambda m: 'Najboljš' + m.group(1)),
    (r'\bsmetisce\b', 'smetišče'),
    (r'\btezisce\b', 'težišče'),

    # ---- ž ----
    (r'\bzelez(\w*)', lambda m: 'želez' + m.group(1)),
    (r'\bZelez(\w*)', lambda m: 'Želez' + m.group(1)),
    (r'\bdrzav(\w*)', lambda m: 'držav' + m.group(1)),
    (r'\bDrzav(\w*)', lambda m: 'Držav' + m.group(1)),
    (r'\bdrzava\b', 'država'),
    (r'\bDrzava\b', 'Država'),
    (r'\btrzn(\w*)', lambda m: 'tržn' + m.group(1)),
    (r'\bTrzn(\w*)', lambda m: 'Tržn' + m.group(1)),
    (r'\btrzi(\w*)', lambda m: 'trži' + m.group(1)),
    (r'\bzdruzen(\w*)', lambda m: 'združen' + m.group(1)),
    (r'\bZdruzen(\w*)', lambda m: 'Združen' + m.group(1)),
    (r'\bdrzati\b', 'držati'),
    (r'\bjuzn(\w*)', lambda m: 'južn' + m.group(1)),
    (r'\bJuzn(\w*)', lambda m: 'Južn' + m.group(1)),
    (r'\bsnezn(\w*)', lambda m: 'snežn' + m.group(1)),
    (r'\bSnezn(\w*)', lambda m: 'Snežn' + m.group(1)),
    (r'\bdolzin(\w*)', lambda m: 'dolžin' + m.group(1)),
    (r'\bDolzin(\w*)', lambda m: 'Dolžin' + m.group(1)),
    (r'\bdosezk(\w*)', lambda m: 'dosežk' + m.group(1)),
    (r'\bDosezk(\w*)', lambda m: 'Dosežk' + m.group(1)),
    (r'\bdoseze\b', 'doseže'),
    (r'\bDoseze\b', 'Doseže'),
    (r'\bmoznost(\w*)', lambda m: 'možnost' + m.group(1)),
    (r'\bMoznost(\w*)', lambda m: 'Možnost' + m.group(1)),

    # ====== Country names ======
    (r'\bNemcija\b', 'Nemčija'),
    (r'\bnemcija\b', 'Nemčija'),
    (r'\bHrvaska\b', 'Hrvaška'),
    (r'\bhrvaska\b', 'Hrvaška'),
    (r'\bMadzarska\b', 'Madžarska'),
    (r'\bCeska\b', 'Češka'),
    (r'\bSlovaska\b', 'Slovaška'),
    (r'\bSpanija\b', 'Španija'),
    (r'\bSvica\b', 'Švica'),
    (r'\bSvedska\b', 'Švedska'),
    (r'\bGrcija\b', 'Grčija'),
]


# Patterns to verify nothing remains. Each is a stem regex; if any matches
# after fixes are applied, the file is still dirty and the script exits 1.
VERIFY_PATTERNS = [
    'mesecn', 'kljucn', 'povprecn', 'nacrt', 'nacin', 'znacil', 'specifin',
    'specificn', 'sestev', 'tezav', 'oznacen', 'oznacit', 'tezk', 'cas\\b',
    'vecj', 'vec\\b', 'izboljsa', 'drzav', 'izrecn', 'oznacen', 'nujn[oa]\\b',
    'nastet', 'splosn', 'placljiv', 'doplacil', 'Nemcija', 'Hrvaska',
    'Madzarska', 'Ceska', 'trzn', 'Zakljucek', 'tocke', 'vsec', 'noc\\b',
    'noci\\b', 'razlicn', 'natancn', 'vkljuc', 'izkljuc', 'tisoc', 'mozno',
    'moznost', 'dolzin', 'dosezk', 'vazno', 'sele\\b', 'ucinkovit', 'zacet',
    'zacasn', 'zascit', 'sirok', 'sibk', 'pricakuj', 'povzroca', 'povzroci',
    'najvec', 'izracun', 'dalec', 'mocno', 'mocn', 'podroc', 'pocasn',
    'pravocasn', 'neucinkov', 'vecerj', 'vecin', 'cisc', 'priporoc', 'reseno',
    'premoc', 'posamicn', 'cakal', 'mogoce', 'neobicajn', 'ljubljenc',
    'pijaca', 'sporoc', 'odloc[ae]', 'naroc[ae]', 'neupravicen', 'obcut',
    'svetlec', 'omogoc', 'porocil', 'porocaj', 'pomoc\\b', 'cezmern',
    'izstopajoc',
]


def _verify(text: str) -> list[tuple[str, int, list[str]]]:
    no_style = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
    no_script = re.sub(r'<script[^>]*>.*?</script>', '', no_style, flags=re.DOTALL)
    no_attrs = re.sub(r'\s+\w+="[^"]*"', '', no_script)
    visible = re.sub(r'<[^>]+>', ' ', no_attrs)

    misses: list[tuple[str, int, list[str]]] = []
    for stem in VERIFY_PATTERNS:
        matches = re.findall(r'\b' + stem, visible)
        if matches:
            misses.append((stem, len(matches), sorted(set(matches))[:3]))
    return misses


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"file not found: {path}", file=sys.stderr)
        return 1
    text = path.read_text(encoding="utf-8")
    n_total = 0
    summary: list[tuple[str, int]] = []
    for pattern, repl in FIXES:
        new_text, n = re.subn(pattern, repl, text)
        if n > 0:
            summary.append((pattern, n))
            text = new_text
            n_total += n
    path.write_text(text, encoding="utf-8")

    if summary:
        for p, n in summary:
            print(f"  {p:35s} -> {n}x")
        print(f"\ntotal fixes: {n_total}")
    else:
        print("(no diacritic fixes needed)")

    misses = _verify(text)
    if misses:
        print("\nWARNING: remaining ASCII Slovenian patterns detected:")
        for stem, n, examples in misses:
            print(f"  {stem:25s} {n}x  e.g. {examples}")
        print("\nAdd these stems to FIXES in fix_diacritics.py and re-run.")
        return 1
    if n_total > 0:
        print("\nverify: clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
