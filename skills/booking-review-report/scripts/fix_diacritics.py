#!/usr/bin/env python3
"""Fix common Slovenian diacritic loss in a generated HTML report.

The subagent that authors review-sentiment HTML routinely strips č/š/ž
from common Slovenian words. This script runs as the final step of the
booking-review-report skill to fix those losses across the whole file.

Usage:
    python3 fix_diacritics.py <path/to/report.html>

It rewrites the file in place and prints a summary of replacements.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


# Each entry: (regex pattern, replacement). Replacement may be a string or a
# lambda(re.Match) -> str for stem-preserving substitutions.
FIXES: list[tuple[str, object]] = [
    # ====== č ======
    (r'\bMesecn(\w*)', lambda m: 'Mesečn' + m.group(1)),
    (r'\bmesecn(\w*)', lambda m: 'mesečn' + m.group(1)),
    (r'\bkljucn(\w*)', lambda m: 'ključn' + m.group(1)),
    (r'\bKljucn(\w*)', lambda m: 'Ključn' + m.group(1)),
    (r'\bpovprecn(\w*)', lambda m: 'povprečn' + m.group(1)),
    (r'\bPovprecn(\w*)', lambda m: 'Povprečn' + m.group(1)),
    (r'\bpovprecje\b', 'povprečje'),
    (r'\bPovprecje\b', 'Povprečje'),
    (r'\bnacrt(\w*)', lambda m: 'načrt' + m.group(1)),
    (r'\bNacrt(\w*)', lambda m: 'Načrt' + m.group(1)),
    (r'\bnacin(\w*)', lambda m: 'način' + m.group(1)),
    (r'\bNacin(\w*)', lambda m: 'Način' + m.group(1)),
    (r'\bznacil(\w*)', lambda m: 'značil' + m.group(1)),
    (r'\bZnacil(\w*)', lambda m: 'Značil' + m.group(1)),
    (r'\bznacaj(\w*)', lambda m: 'značaj' + m.group(1)),
    (r'\bZnacaj(\w*)', lambda m: 'Značaj' + m.group(1)),
    (r'\bznacka\b', 'značka'),
    (r'\bznacke\b', 'značke'),
    (r'\bspecifin(\w*)', lambda m: 'specifičn' + m.group(1)),
    (r'\bspecificn(\w*)', lambda m: 'specifičn' + m.group(1)),
    (r'\bsestev(\w*)', lambda m: 'seštev' + m.group(1)),
    (r'\bSestev(\w*)', lambda m: 'Seštev' + m.group(1)),
    (r'\btezav(\w*)', lambda m: 'težav' + m.group(1)),
    (r'\bTezav(\w*)', lambda m: 'Težav' + m.group(1)),
    (r'\btezk(\w*)', lambda m: 'težk' + m.group(1)),
    (r'\bTezk(\w*)', lambda m: 'Težk' + m.group(1)),
    (r'\bcas\b', 'čas'),
    (r'\bCas\b', 'Čas'),
    (r'\bcasa\b', 'časa'),
    (r'\bcasu\b', 'času'),
    (r'\bcasi\b', 'časi'),
    (r'\bcasov(\w*)', lambda m: 'časov' + m.group(1)),
    (r'\bCasov(\w*)', lambda m: 'Časov' + m.group(1)),
    (r'\bvecj(\w*)', lambda m: 'večj' + m.group(1)),
    (r'\bVecj(\w*)', lambda m: 'Večj' + m.group(1)),
    (r'\bvec\b', 'več'),
    (r'\bVec\b', 'Več'),
    (r'\bvecino\b', 'večino'),
    (r'\bvecini\b', 'večini'),
    (r'\bvecinoma\b', 'večinoma'),
    (r'\bnajvec(\w*)', lambda m: 'največ' + m.group(1)),
    (r'\bNajvec(\w*)', lambda m: 'Največ' + m.group(1)),
    (r'\bnajvecja\b', 'največja'),
    (r'\bNajvecja\b', 'Največja'),
    (r'\bnajvecje\b', 'največje'),
    (r'\bnajvecji\b', 'največji'),
    (r'\bnoc\b', 'noč'),
    (r'\bNoc\b', 'Noč'),
    (r'\bnoci\b', 'noči'),
    (r'\bNoci\b', 'Noči'),
    (r'\bnocn(\w*)', lambda m: 'nočn' + m.group(1)),
    (r'\btocke\b', 'točke'),
    (r'\btocka\b', 'točka'),
    (r'\bTocka\b', 'Točka'),
    (r'\btocko\b', 'točko'),
    (r'\btisoc\b', 'tisoč'),
    (r'\bTisoc\b', 'Tisoč'),
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
    (r'\bpovzroca\b', 'povzroča'),
    (r'\bpovzroci\b', 'povzroči'),
    (r'\bpovzrocaj(\w*)', lambda m: 'povzročaj' + m.group(1)),
    (r'\bpovzrocij(\w*)', lambda m: 'povzročij' + m.group(1)),
    (r'\boznacit(\w*)', lambda m: 'označit' + m.group(1)),
    (r'\bOznacit(\w*)', lambda m: 'Označit' + m.group(1)),
    (r'\boznacen(\w*)', lambda m: 'označen' + m.group(1)),
    (r'\bOznacen(\w*)', lambda m: 'Označen' + m.group(1)),
    (r'\boznaceval(\w*)', lambda m: 'označeval' + m.group(1)),
    (r'\boznacuj(\w*)', lambda m: 'označuj' + m.group(1)),
    (r'\bplaca\b', 'plača'),
    (r'\bplace\b', 'plače'),
    (r'\bplaco\b', 'plačo'),
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
    (r'\bdolocen(\w*)', lambda m: 'določen' + m.group(1)),
    (r'\bDolocen(\w*)', lambda m: 'Določen' + m.group(1)),
    (r'\bdolocit(\w*)', lambda m: 'določit' + m.group(1)),
    (r'\bucinkovit(\w*)', lambda m: 'učinkovit' + m.group(1)),
    (r'\bUcinkovit(\w*)', lambda m: 'Učinkovit' + m.group(1)),
    (r'\bvsec\b', 'všeč'),
    (r'\bVsec\b', 'Všeč'),
    (r'\bvšec\b', 'všeč'),
    (r'\bVšec\b', 'Všeč'),
    (r'\bizrecn(\w*)', lambda m: 'izrečn' + m.group(1)),

    # ====== š ======
    (r'\bsibk(\w*)', lambda m: 'šibk' + m.group(1)),
    (r'\bSibk(\w*)', lambda m: 'Šibk' + m.group(1)),
    (r'\bsirok(\w*)', lambda m: 'širok' + m.group(1)),
    (r'\bSirok(\w*)', lambda m: 'Širok' + m.group(1)),
    (r'\bsiri\b', 'širi'),
    (r'\bsirj(\w*)', lambda m: 'širj' + m.group(1)),
    (r'\bsele\b', 'šele'),
    (r'\bSele\b', 'Šele'),
    (r'\bsola\b', 'šola'),
    (r'\bSola\b', 'Šola'),
    (r'\bsole\b', 'šole'),
    (r'\bsest\b', 'šest'),
    (r'\bSest\b', 'Šest'),
    (r'\bsteviln(\w*)', lambda m: 'številn' + m.group(1)),
    (r'\bSteviln(\w*)', lambda m: 'Številn' + m.group(1)),
    (r'\bstevilo\b', 'število'),
    (r'\bStevilo\b', 'Število'),
    (r'\bstevilom\b', 'številom'),
    (r'\bstevilu\b', 'številu'),
    (r'\bstevila\b', 'števila'),
    (r'\bskoda\b', 'škoda'),
    (r'\bskode\b', 'škode'),
    (r'\bSkoda\b', 'Škoda'),
    (r'\bskodljiv(\w*)', lambda m: 'škodljiv' + m.group(1)),
    (r'\bsplosn(\w*)', lambda m: 'splošn' + m.group(1)),
    (r'\bSplosn(\w*)', lambda m: 'Splošn' + m.group(1)),
    (r'\bnasteti\b', 'našteti'),
    (r'\bnastetih\b', 'naštetih'),
    (r'\bnasteva(\w*)', lambda m: 'našteva' + m.group(1)),
    (r'\bvsi(\w*)', None),  # safe (vsi/vsa/vse OK)
    (r'\bizboljsa(\w*)', lambda m: 'izboljša' + m.group(1)),
    (r'\bIzboljsa(\w*)', lambda m: 'Izboljša' + m.group(1)),
    (r'\bizboljs(\w*)', lambda m: 'izboljš' + m.group(1)),  # secondary
    (r'\bIzboljs(\w*)', lambda m: 'Izboljš' + m.group(1)),
    (r'\bnajboljs(\w*)', lambda m: 'najboljš' + m.group(1)),
    (r'\bNajboljs(\w*)', lambda m: 'Najboljš' + m.group(1)),
    (r'\bsmetisce\b', 'smetišče'),
    (r'\btezisce\b', 'težišče'),
    (r'\bzelis\b', 'želiš'),
    (r'\bZelis\b', 'Želiš'),

    # ====== ž ======
    (r'\bze\b', 'že'),
    (r'\bZe\b', 'Že'),
    (r'\bzel(?:i|im|imo|ijo|el|ela|eli)\b', lambda m: 'žel' + m.group(0)[3:]),
    (r'\bZel(?:i|im|imo|ijo|el|ela|eli)\b', lambda m: 'Žel' + m.group(0)[3:]),
    (r'\bzelez(\w*)', lambda m: 'želez' + m.group(1)),
    (r'\bZelez(\w*)', lambda m: 'Želez' + m.group(1)),
    (r'\bzene\b', 'žene'),
    (r'\bZene\b', 'Žene'),
    (r'\bzena\b', 'žena'),
    (r'\bZena\b', 'Žena'),
    (r'\bdrzav(\w*)', lambda m: 'držav' + m.group(1)),
    (r'\bDrzav(\w*)', lambda m: 'Držav' + m.group(1)),
    (r'\bdrzava\b', 'država'),
    (r'\bDrzava\b', 'Država'),
    (r'\btrzn(\w*)', lambda m: 'tržn' + m.group(1)),
    (r'\bTrzn(\w*)', lambda m: 'Tržn' + m.group(1)),
    (r'\btrzi(\w*)', lambda m: 'trži' + m.group(1)),
    (r'\bzdruzen(\w*)', lambda m: 'združen' + m.group(1)),
    (r'\bZdruzen(\w*)', lambda m: 'Združen' + m.group(1)),
    (r'\bdrzi\b', 'drži'),
    (r'\bDrzi\b', 'Drži'),
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
    (r'\bvazno\b', 'važno'),
    (r'\bVazno\b', 'Važno'),
    (r'\bmozno\b', 'možno'),
    (r'\bMozno\b', 'Možno'),
    (r'\bmoznost(\w*)', lambda m: 'možnost' + m.group(1)),
    (r'\bMoznost(\w*)', lambda m: 'Možnost' + m.group(1)),
    (r'\bnajsibkejs(\w*)', lambda m: 'najšibkejš' + m.group(1)),

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
        if repl is None:
            continue
        new_text, n = re.subn(pattern, repl, text)
        if n > 0:
            summary.append((pattern, n))
            text = new_text
            n_total += n
    path.write_text(text, encoding="utf-8")
    if not summary:
        print("clean (no diacritic fixes needed)")
        return 0
    for p, n in summary:
        print(f"  {p:35s} -> {n}x")
    print(f"\ntotal fixes: {n_total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
