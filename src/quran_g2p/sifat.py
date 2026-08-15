"""P14 — sifat projection (SPEC-214b).

Static articulatory sifat are letter-intrinsic (classical tables: hams letters
فحثه شخص سكت; shidda أجد قط بكت with بينية letters لن عمر; safeer ص ز س;
qalqalah ق ط ب ج د; tikrar ر; tafashshi ش; istitala ض; itbaq ص ض ط ظ;
inhiraf ل ر; idhlaq فر من لب — the Jazariyya's full seventeen).
Dynamic sifat (tafkheem, qalqalah realization, ghunna) are read off the
phone's attributes, which the rule phases already resolved — nothing here
re-derives context.
"""
from __future__ import annotations

from .ir import Base, Phone

_HAMS = {Base.FEH, Base.HAH, Base.THEH, Base.HEH, Base.SHEEN, Base.KHAH,
         Base.SAD, Base.SEEN, Base.KAF, Base.TEH}
_SHADEED = {Base.HAMZA, Base.JEEM, Base.DAL, Base.QAF, Base.TAH, Base.BEH,
            Base.KAF, Base.TEH}
_BAYNIYYA = {Base.LAM, Base.NOON, Base.AIN, Base.MEEM, Base.REH}
_ITBAQ = {Base.SAD, Base.DAD, Base.TAH, Base.ZAH}
_SAFEER = {Base.SAD, Base.ZAIN, Base.SEEN}
_QALQALAH = {Base.QAF, Base.TAH, Base.BEH, Base.JEEM, Base.DAL}
_INHIRAF = {Base.LAM, Base.REH}
_IDHLAQ = {Base.FEH, Base.REH, Base.MEEM, Base.NOON, Base.LAM, Base.BEH}
_GHUNNA_BASES = {Base.NOON, Base.MEEM, Base.NOON_MUKHFAH, Base.MEEM_MUKHFAH}

_CONS_ALIASES = {
    Base.NOON_MUKHFAH: Base.NOON,
    Base.MEEM_MUKHFAH: Base.MEEM,
    Base.HAMZA_MUSAHHALA: Base.HAMZA,
    Base.TEH_MARBUTA: Base.TEH,
}


def sifat_of(p: Phone) -> dict[str, str]:
    base = _CONS_ALIASES.get(p.base, p.base)
    if base in _SHADEED:
        shidda = "shadeed"
    elif base in _BAYNIYYA:
        shidda = "between"
    else:
        shidda = "rikhw"
    ghunna_active = (p.ghunna is not None and p.ghunna != "asl"
                     and p.base in _GHUNNA_BASES) or (
        p.geminated and p.base in (Base.NOON, Base.MEEM))
    return {
        "hams_or_jahr": "hams" if base in _HAMS else "jahr",
        "shidda_or_rakhawa": shidda,
        "tafkheem_or_taqeeq": p.tafkheem,
        "itbaq": "motbaq" if base in _ITBAQ else "monfateh",
        "safeer": "safeer" if base in _SAFEER else "no_safeer",
        "qalqla": "moqalqal" if p.qalqalah is not None else (
            "not_moqalqal"),
        "tikraar": "mokarar" if base is Base.REH else "not_mokarar",
        "tafashie": "motafashie" if base is Base.SHEEN else "not_motafashie",
        "istitala": "mostateel" if base is Base.DAD else "not_mostateel",
        "inhiraf": "monharif" if base in _INHIRAF else "not_monharif",
        "idhlaq": "mothlaq" if base in _IDHLAQ else "mosmat",
        "ghonna": "maghnoon" if ghunna_active else "not_maghnoon",
    }
