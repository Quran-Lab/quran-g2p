"""The canonical rulings register.

Every rule id the engine can cite in a RuleApp trace appears here, mapped
to the golden-YAML rows that put that ruling in front of the expert
reviewer. `tests/test_registry_complete.py` enforces, permanently:

  * every rule id used in src/ is registered (no unregistered rules),
  * every registered id is still used in src/ (no stale entries),
  * every id maps to at least one EXISTING golden row (no uncovered
    rulings, no dangling row ids).

So "are all rulings in the review sheet?" is a green test, not an audit.
A new RuleApp id fails the suite until its ruling is added to the
reviewable set and mapped here.
"""

#: rule id -> golden row ids that state this ruling for the reviewer.
#: A ruling may be covered by a site row, a statement/taxonomy row, or
#: both; several mechanical ids share one reviewable statement (noted).
COVERAGE: dict[str, tuple[str, ...]] = {
    # P1 orthography
    "R011_MUQATTAAT": ("muq-taha", "muq-yaseen-seen", "muq-hameem",
                       "madd-harfi-ha-two", "izhar-yaseen",
                       "izhar-noon-qalam"),
    "R012_SEEN_SAD": ("oneoff-yabsut-seen", "oneoff-bastatan-seen",
                      "oneoff-musaytirun-sad", "oneoff-bimusaytir-sad"),
    "R012B_DAAF_DAMM": ("oneoff-daaf-fath",),
    "R013_ELIDED_WAW_LIYASUU": ("sup-17-7-waw-restored",),
    "R014B_ISTIFHAM_TASHEEL": ("sup2-istifham-tasheel",),
    # P3 ibtida'
    "R110_WASL_START": ("wasl-article-fath", "wasl-noun-ibn",
                        "wasl-noun-imraat", "wasl-noun-ithnayn",
                        "wasl-verb-unzur-damm", "wasl-verb-idhab-kasr",
                        "wasl-verb-udu-damm", "wasl-verb-iqra-kasr"),
    "R110_BADAL_IBTIDA": ("sup2-wasl-badal-hamza",),
    "R112_STRIP_INITIAL_SHADDA": ("sup2-ibtida-shadda",),
    # P4 pausal
    "R120_ISKAN": ("pausal-iskan-alamin",),
    "R121_MADD_EWAD": ("madd-iwad", "pausal-iwad-fath-alif"),
    # wasl-silence of the tanween-fath seat alif is the complement of the
    # waqf-ibdal ruling stated on these rows
    "R121_EWAD_SEAT_SILENT": ("pausal-iwad-fath-alif", "pausal-iwad-khusr"),
    "R122_TAA_MARBUTA_WAQF": ("pausal-marbuta-qaria",
                              "pausal-marbuta-mid-wasl-teh"),
    "R123_RAWM": ("sup-rawm-general", "sup-rawm-exclusions",
                  "sup-rawm-haa-damir"),
    "R123_ISHMAM": ("sup-rawm-general",),
    # P5 junction
    "R130_WASL_ELISION": ("wiqaya-khayran", "junction-madd-shortening",
                          "sup-naql-49-11", "lam-shamsi-shams"),
    "R131_MADD_SHORTENING": ("junction-madd-shortening",),
    "R131_NOON_WIQAYA": ("wiqaya-khayran",),
    "R132_SAKT": ("sup-sakt-class", "sup-sakt-75-27"),
    "R132_MALIYAH_SAKT": ("sup2-maliyah-wasl",),
    "R133_R160_IDGHAM_KAMIL": ("lam-shamsi-shams", "lam-shamsi-nnas",
                               "mutamathil-yudrikkum"),
    "R134_LAM_JALALA_ALIF": ("jalala-tarqeeq-after-kasr",
                             "jalala-tafkheem-after-fath"),
    "R135_MEEM_ALLAH": ("sup-alm-allah",),
    # P6 noon sakinah / tanween
    "R140_IZHAR": ("izhar-hamza", "izhar-heh", "izhar-ain", "izhar-hah",
                   "izhar-ghain", "izhar-khah"),
    "R140_IZHAR_HALQI": ("izhar-hamza", "izhar-tanween-hah",
                         "izhar-tanween-ain"),
    "R141_IDGHAM_GHUNNA": ("idgham-noon-kamil", "idgham-meem-kamil",
                           "idgham-tanween-meem",
                           "tawkeed-layakoonan-idgham"),
    "R141_IDGHAM_GHUNNA_NAQIS": ("idgham-yeh-naqis", "idgham-waw-naqis",
                                 "idgham-tanween-waw"),
    "R141_IZHAR_MUTLAQ": ("izhar-mutlaq-dunya", "izhar-mutlaq-bunyan",
                          "izhar-mutlaq-qinwan", "izhar-mutlaq-sinwan"),
    "R142_IDGHAM_BILA_GHUNNA": ("idgham-lam", "idgham-reh"),
    "R143_IQLAB": ("iqlab-min-badi", "iqlab-anbihum", "iqlab-baqliha",
                   "iqlab-burika", "iqlab-alim-bithat",
                   "tawkeed-lanasfaan-iqlab"),
    "R144_IKHFA": ("ikhfa-teh", "ikhfa-theh", "ikhfa-jeem", "ikhfa-dal",
                   "ikhfa-thal", "ikhfa-zain", "ikhfa-seen", "ikhfa-sheen",
                   "ikhfa-sad-mofakham", "ikhfa-dad", "ikhfa-tah-mofakham",
                   "ikhfa-zah", "ikhfa-feh", "ikhfa-qaf-mofakham",
                   "ikhfa-kaf"),
    # P7 meem sakinah
    "R150_IKHFA_SHAFAWI": ("meem-ikhfa-tarmihim", "meem-ikhfa-yatasim"),
    # P8 general idgham
    "R160_MUTAMATHILAYN": ("mutamathil-yudrikkum", "meem-idgham-lahum-ma"),
    "R161_NAQIS_TA_NO_QALQALAH": ("naqis-tah-basatta", "naqis-tah-ahatt",
                                  "naqis-tah-farrattum"),
    # P9 ghunna
    "R170_GHUNNA_MUSHADDADAH": ("ghunna-noon-mushaddad", "ghunna-meem-amma",
                                "ghunna-inna", "ghunna-thumma"),
    # P10 madd
    "R180_TABEEI": ("madd-tabeei-qala",),
    "R180_PAUSAL_GLIDE": ("madd-leen-quraysh", "madd-leen-khawf"),
    "R181_BADAL": ("madd-badal",),
    "R183_SILAH_WAQF_DROP": ("madd-silah-sughra", "pausal-iskan-alamin"),
    "R184_SILAH_KUBRA": ("madd-silah-kubra",),
    "R185_MUTTASIL": ("madd-muttasil-jaa", "madd-muttasil-samaa"),
    "R185_MUTTASIL_WAQF": ("sup-madd-amounts",),
    "R186_MUNFASIL": ("madd-munfasil-bima-unzila",),
    "R187_LAZIM_MUTHAQQAL": ("madd-lazim-daalleen", "madd-lazim-haaqqah",
                             "madd-lazim-taammah",
                             "madd-lazim-mukhaffaf-aalaan"),
    "R187_R188_LAZIM": ("madd-harfi-laam", "madd-harfi-meem",
                        "madd-harfi-kaf-19-1", "madd-harfi-sad-19-1"),
    "R188_AIN_LEEN_LAZIM": ("madd-ain-19-1",),
    "R189_AARED": ("madd-aared-nastaeen",),
    "R190_LEEN": ("madd-leen-quraysh", "madd-leen-khawf"),
    "R190B_SALASILA_ITHBAT": ("alif7-salasila-wasl",),
    "R190C_AATAANI_HADHF": ("sup-aataani-wajh",),
    # P11 qalqalah
    "R200_QALQALAH_SUGHRA": ("qlq-sughra-qaf", "qlq-sughra-tah",
                             "qlq-sughra-beh", "qlq-sughra-jeem",
                             "qlq-sughra-dal"),
    "R201_QALQALAH_KUBRA": ("qlq-kubra-falaq", "qlq-kubra-ahad",
                            "qlq-kubra-muheet", "qlq-kubra-bahij"),
    "R202_QALQALAH_AKBAR": ("qlq-kubra-tabb", "sup2-qalqalah-akbar"),
    # P12 tafkheem
    "R210_ISTILA": ("sup-sifat-sets", "sup2-tafkheem-maratib"),
    "R211_REH": ("ra-fath-tafkheem", "ra-damm-tafkheem", "ra-kasr-tarqeeq",
                 "ra-sakin-after-fath", "ra-sakin-after-damm",
                 "ra-sakin-after-kasr-tarqeeq", "ra-sakin-kasr-istila-mirsad",
                 "ra-firq-wasl-tarqeeq", "ra-nudhur-waqf-tarqeeq",
                 "ra-yasr-waqf-tarqeeq", "ra-fajr-waqf-tafkheem",
                 "ra-khabir-waqf-tarqeeq"),
    "R211_WAQF_KHILAF": ("sup-misr-qitr-asr",),
    "R212_LAM_JALALA": ("jalala-tarqeeq-after-kasr",
                        "jalala-tafkheem-after-fath"),
    "R214_IKHFA_TAFKHEEM": ("sup-ghunna-tabiyya", "ikhfa-sad-mofakham",
                            "ikhfa-tah-mofakham", "ikhfa-qaf-mofakham"),
    # P13 one-offs
    "R220_ISHMAM": ("sup-taamanna-ishmam",),
    "R220B_TAAMANNA_IKHTILAS": ("sup-taamanna-ishmam",),
    "R221_IMALA": ("oneoff-imala",),
    "R222_TASHEEL": ("oneoff-tasheel",),
}
