"""All user-facing UI text in one place.

Code asks for text by key: ``t("home.tutvustus")`` or, for messages with
values, ``t("common.progress", percent=42.0)`` (``str.format`` placeholders).

To add a language, copy ``ET`` to a new dict with the same keys, translate the
values and call ``set_language(EN)`` at startup, before the application
modules are imported (a few labels are looked up at import time). Missing keys
fall back to Estonian. See DEVPLAN.md, "Planned: Multi-language support".
"""

from __future__ import annotations

ET: dict[str, str] = {
	# app
	"app.morsekoodi_oppimisprogramm": "Morsekoodi õppeprogramm",
	# audio settings panel (sandbox)
	"audio.heli_ei_saa_esitada": "Heli ei saa esitada.",
	"audio.helikorgus": "Helikõrgus\n",
	"audio.helisatted_ja_salvestus": "Heli ja salvestamine",
	"audio.heliseadet_ei_leitud_esitamine": "Heliseadet pole: esitada ei saa, salvestada saab.",
	"audio.helitugevus": "Valjus\n",
	"audio.kehtivad_koigis_harjutustes_kui": "Kehtib kõigis harjutustes. Väiksem üldkiirus pikendab vahesid,\ntähed jäävad kiireks (Farnsworthi meetod).",
	"audio.peata_heli": "Peata",
	"audio.salvesta_heli": "Salvesta",
	"audio.salvesta_nimega": "Salvesta nimega…",
	"audio.tahtede_kiirus": "Tähtede\nkiirus",
	"audio.uldine_kiirus": "Üld-\nkiirus",
	# common
	"common.esita_heli": "Kuula",
	"common.heli_ei_onnestunud_esitada": "Heli esitamine ebaõnnestus.",
	"common.liigu_edasi": "Järgmine",
	"common.liigu_tagasi": "Eelmine",
	"common.lopeta_treening": "Lõpeta",
	"common.lopp": "Valmis",
	"common.morse_tekst": "Morse → tekst",
	"common.ok": "OK",
	"common.progress": "{percent:.1f}% läbitud",
	"common.question_counter": "Küsimus {number}/{total}",
	"common.tagasi": "Tagasi",
	"common.tagasi_avalehele": "Avalehele",
	"common.tagasi_valikute_juurde": "Valikute juurde",
	"common.tekst_morse": "Tekst → Morse",
	# errors
	"error.andmed_ei_uhti_kontrolli": "Andmed ei klapi. Kontrolli sisendit.",
	"error.generic": "Viga: {details}",
	"error.heli_esitamine_ebaonnestus": "Heli esitamine ebaõnnestus.",
	"error.heli_esitamiseks_puudub_morsekoodi": "Pole morsekoodi, mida esitada.",
	"error.helifaili_loomine_ebaonnestus": "Heli loomine ebaõnnestus.",
	"error.helifaili_salvestamine_ebaonnestus": "Salvestamine ebaõnnestus.",
	"error.oled_joudnud_harjutuse_loppu": "Harjutus on lõppenud.",
	"error.palun_sisesta_tekst_enne": "Sisesta enne tõlkimist tekst.",
	"error.ressursi_laadimine_ebaonnestus": "Ressursi laadimine ebaõnnestus.",
	"error.seadistus_on_vigane": "Vigane seadistus.",
	"error.seanss_on_vigases_olekus": "Harjutus on vigases olekus. Alusta uuesti.",
	"error.seanss_pole_kaivitatud_palun": "Harjutus pole alanud. Alusta uuesti.",
	"error.sisend_sisaldab_morsekoodi_mida": "Sisendis on tundmatu morsekood.",
	"error.sisend_sisaldab_tahemarki_mida": "Sisendis on märk, millel pole morsekoodi.",
	"error.tolkimine_ebaonnestus_kontrolli_sisendit": "Tõlkimine ebaõnnestus. Kontrolli sisendit.",
	"error.unsupported_character": "Märki '{char}' ei toetata.",
	"error.vajalikku_ressurssi_ei_leitud": "Ressurssi ei leitud.",
	"error.valitud_reziim_pole_toetatud": "See režiim pole toetatud.",
	# flashcards
	"flashcards.did_not_know": "Ei teadnud",
	"flashcards.heli": "Heli",
	"flashcards.kirjavahemarkide_andmed_puuduvad": "Kirjavahemärkide kaarte pole.",
	"flashcards.knew_it": "Teadsin",
	"flashcards.kuula_heli": "Kuula",
	"flashcards.numbrikaartide_andmed_puuduvad": "Numbrikaarte pole.",
	"flashcards.opi_kirjavahemarke": "Kirjavahemärgid",
	"flashcards.opi_numbreid": "Numbrid",
	"flashcards.opi_tahti": "Tähed",
	"flashcards.poora_kaarti": "Pööra",
	"flashcards.sumbolitega_tutvumine": "Märkide õpe",
	"flashcards.tahekaartide_andmed_puuduvad": "Tähekaarte pole.",
	"flashcards.tubli_too_koik_kaardid": "Tubli! Kõik kaardid on läbitud. OK viib tagasi valikute juurde.",
	"flashcards.vali_kategooria_mida_soovid": "Vali, mida õppida. Märgid, mida sa ei teadnud, tulevad sagedamini ette.",
	# test grades and feedback
	"grade.a": "A (suurepärane) / {percentage}%",
	"grade.b": "B (väga hea) / {percentage}%",
	"grade.c": "C (hea) / {percentage}%",
	"grade.d": "D (rahuldav) / {percentage}%",
	"grade.e": "E (kasin) / {percentage}%",
	"grade.f": "F (mitterahuldav) / {percentage}%",
	"grade.hakkab_juba_vaikselt_tulema": "Hakkab tulema.\nHarjuta veel paar korda ja tulemus paraneb.",
	"grade.paris_hea_tundub_et": "Väga hea – areng on selgelt näha.",
	"grade.punktisumma_pole_just_koige": "Tulemus on nõrk, kuid arenguruumi on palju. Harjuta ja proovi uuesti.",
	"grade.score": "Õigeid vastuseid: {points} / {max_points}",
	"grade.vaga_super_oled_testi": "Suurepärane!\nVõid end nimetada morsekoodi meistriks.",
	# loading screen
	"splash.audio": "Valmistan heli ette…",
	"splash.data": "Laadin harjutusi ja edenemist…",
	"splash.ready": "Valmis!",
	"splash.screens": "Ehitan ekraane…",
	"splash.starting": "Käivitan…",
	# hubs (two-level home menu)
	"hub.cards_description": "Tähed, numbrid ja märgid kaartidel koos heliga.",
	"hub.keyer_description": "Saada morset tühikuklahviga ja näe, mis välja tuli.",
	"hub.koch_description": "Kuula märgirühmi ja kirjuta kuuldu; 90% avab uue märgi.",
	"hub.learn_subtitle": "Õpi märke silmaga või kõrvaga.",
	"hub.learn_title": "Õpe",
	"hub.practice_subtitle": "Harjuta tõlkimist või saatmist.",
	"hub.practice_title": "Harjutused",
	"hub.translation_description": "Tõlgi mõlemas suunas valmislauseid või juhuslikke sõnu.",
	# home and introduction
	"home.caption_intro": "Kuidas morsekood töötab",
	"home.caption_learn": "Märkide õpe ja kõrvaõpe",
	"home.caption_practice": "Tõlkimine ja võtmeharjutus",
	"home.caption_sandbox": "Vaba tõlkimine ja heliseaded",
	"home.caption_test": "Taimeriga test ja hinne",
	"home.ope_cards": "Märkide õpe",
	"home.translation": "Tõlkeharjutused",
	"intro.modes_heading": "Režiimid",
	"intro.timing_heading": "Ajastus",
	"home.harjutused": "Harjutused",
	"home.keyer": "Võtmeharjutus",
	"home.koch": "Kõrvaõpe",
	"home.morsekood_moodab_aega_uhikutes": (
		"Morsekoodis mõõdetakse aega ühikutes: punkt kestab 1 ühiku, kriips 3. "
		"Märgi sees on signaalide vahel 1 ühik vaikust, märkide vahel 3 ja sõnade vahel 7 ühikut. "
		"Kirjas tähistatakse signaale punkti ja kriipsuga (. ja -); märke eraldab üks tühik, "
		"sõnu kolm tühikut või kaldkriips (/)."
	),
	"home.morsekoodi_rakendus": "Morsekoodi treener",
	"home.ope": "Õpe",
	"home.ope_voimaldab_flashcard_meetodi": (
		"Märkide õpe: tähed, numbrid ja kirjavahemärgid kaartidel koos heliga; märgid, mida ei "
		"teadnud, tulevad sagedamini.\n"
		"Kõrvaõpe: Kochi meetod – kuula märgirühmi ja kirjuta kuuldu; iga 90% tulemus avab uue märgi.\n"
		"Tõlkeharjutused: tõlgi mõlemas suunas valmislauseid või juhuslikke sõnu, vihjete ja kontrolliga.\n"
		"Test: taimeriga töö, hinne ja vastuste ülevaade.\n"
		"Võtmeharjutus: saada morset tühikuklahviga ja näe kohe, mis välja tuli.\n"
		"Sandbox: vaba tõlkimine, heliseaded ja WAV-faili salvestamine."
	),
	"home.programm_morsekoodi_oppimiseks_harjutamiseks": "Õpi, harjuta, testi ja tõlgi morsekoodi.",
	"home.sandbox": "Sandbox",
	"home.test": "Test",
	"home.theme_dark": "Tume",
	"home.theme_dark_emoji": "🌙 Tume",
	"home.theme_light": "Hele",
	"home.theme_light_emoji": "🌞 Hele",
	"home.tutvustus": "Tutvustus",
	"home.valju_programmist": "Välju",
	# keyer practice
	"keyer.check": "Kontrolli",
	"keyer.clear": "Puhasta",
	"keyer.correct": "Õige!",
	"keyer.intro": (
		"Hoia tühikuklahvi või allolevat ala all: lühike vajutus on punkt, pikk on kriips. "
		"Oodatav tempo tuleb Sandboxi tähtede kiirusest."
	),
	"keyer.new_word": "Uus sõna",
	"keyer.pad": "Vajuta siia või hoia tühikut",
	"keyer.speed": "Sihtkiirus {wpm} WPM",
	"keyer.target": "Saada: {word}",
	"keyer.title": "Võtmeharjutus",
	"keyer.wrong": "Ei klapi – proovi uuesti.",
	"keyer.your_speed": "sinu tempo ~{wpm} WPM",
	# Koch listening lessons
	"koch.check": "Kontrolli",
	"koch.correct_answer": "Õige: {text}",
	"koch.entry_placeholder": "Kirjuta kuuldud märgid",
	"koch.intro": (
		"Kuula juhuslikke märgirühmi ja kirjuta kuuldu. Alustad kahe märgiga; "
		"vähemalt 90% tulemus lisab järgmise märgi."
	),
	"koch.level": "Tase {level}/{max_level} – õpitavad märgid:",
	"koch.level_down": "− Tase",
	"koch.level_up": "+ Tase",
	"koch.listen_new": "Kuula uut märki",
	"koch.new_char": "Uusim märk: {char}   {morse}",
	"koch.new_exercise": "Uus harjutus",
	"koch.no_audio": "Heliseadet pole – kõrvaõpe vajab heli.",
	"koch.not_passed": "{percent}% õige. Uue märgi avamiseks on vaja 90%.",
	"koch.passed_all": "{percent}% õige – kõik märgid on avatud.",
	"koch.passed_level_up": "{percent}% õige – tase läbitud! Uus märk: {char}",
	"koch.play_again": "Kuula uuesti",
	"koch.start_hint": "Vajuta „Uus harjutus“, kuula ja kirjuta kuuldu.",
	"koch.title": "Kõrvaõpe (Kochi meetod)",
	# test review
	"review.correct": "Õige: {points} punkti.\n\nÕige vastus:\n{expected}",
	"review.labivaatus": "Ülevaade",
	"review.labivaatus_lopetatud": "Ülevaade lõpetatud",
	"review.lopeta_labivaatus": "Lõpeta ülevaade",
	"review.oled_koik_kusimused_ule": "Kõik küsimused on üle vaadatud.\nKokkuvõtte näed tulemuste lehel.",
	"review.partial": "Osaliselt õige: {points} punkti.\n\nÕige vastus:\n{expected}",
	"review.time_spent": "Aega kulus {seconds} s.",
	"review.wrong": "Vale: {points} punkti.\n\nÕige vastus:\n{expected}",
	"review.your_answer": "Sinu vastus: {answer}",
	# sandbox
	"sandbox.ei_ole_helifaili_salvestamiseks": "Pole midagi salvestada.",
	"sandbox.file_saved": "Salvestatud:\n{path}",
	"sandbox.helifail_salvestatud": "Fail salvestatud",
	"sandbox.helifaili_ei_onnestunud_salvestada": "Salvestamine ebaõnnestus.",
	"sandbox.katseta_erinevaid_tolkesuundi_muuda": "Tõlgi mõlemas suunas, muuda heliseadeid ja salvesta tulemus.",
	"sandbox.kliki_tolgi_et_kuvada": "Tulemus ilmub siia…",
	"sandbox.morse": "Morse",
	"sandbox.puhasta": "Puhasta",
	"sandbox.salvesta_helifail": "Salvesta helifail",
	"sandbox.sandbox_tolkimine": "Sandbox",
	"sandbox.sisesta_algtekst_morsekood_siia": "Sisesta tekst või morsekood…",
	"sandbox.sisesta_tekst_voi_morsekood": "Sisesta tekst või morsekood ja vajuta „Tõlgi“.\n„Puhasta“ tühjendab mõlemad kastid.",
	"sandbox.tekst": "Tekst",
	"sandbox.tolgi": "Tõlgi",
	"sandbox.tolkesuund": "Tõlkesuund",
	"sandbox.wav_helifail": "WAV-helifail",
	# timed test
	"test.alusta": "Alusta",
	"test.ei_soovi_kordamist": "Ei, kordan veel",
	"test.jah_alusta_testi": "Jah, alusta",
	"test.kas_oled_valmis": "Kas oled valmis?",
	"test.katkesta_test": "Katkesta",
	"test.lopeta_test": "Lõpeta test",
	"test.oled_joudnud_testreziimi_juurde": "Taimeriga test näitab, kui hästi morsekoodi oskad.\n\nAlusta testi või mine enne kordama.",
	"test.progress_zero": "0.0% läbitud",
	"test.question_zero": "Küsimus 0/0",
	"test.sentence_speed": "Lausete kiirus: {speed} lauset/min",
	"test.sisesta_vastus_siia": "Sisesta vastus",
	"test.tagasi_menuusse": "Menüüsse",
	"test.testi_alustades_kaivitub_taimer": "Alustamisel käivitub taimer; lahkumine katkestab testi.\nEnne võid veel õppematerjali korrata.",
	"test.testi_andmed_puuduvad": "Testi pole",
	"test.testi_ennast": "Test",
	"test.testreziimi_jaoks_pole_hetkel": "Testiküsimusi pole. Naase avalehele.",
	"test.tulemused": "Tulemused",
	"test.vaata_vastuseid": "Vaata vastuseid",
	"test.word_speed": "Sõnade kiirus: {speed} sõna/min",
	# translation exercises
	"translation.andmeid_pole": "Harjutusi pole",
	"translation.heli_esitatakse": "Esitan heli…",
	"translation.hint": "Vihje: {answer}",
	"translation.kontrolli_vastust": "Kontrolli",
	"translation.naita_vihjet": "Vihje",
	"translation.oige_vastus_tubli_too": "Õige! Tubli.",
	"translation.sellele_kirjele_heli_pole": "Sellel harjutusel heli pole.",
	"translation.sisesta_morsekood_nt": "Morsekood (nt .- -...)",
	"translation.sisesta_tekst": "Tekst",
	"translation.source_fixed": "Valmislaused",
	"translation.source_hint": "Juhuslikes sõnades korduvad sagedamini märgid, mis sul veel ebakindlad on.",
	"translation.source_random": "Juhuslikud sõnad",
	"translation.tolketreeningu_andmed_puuduvad_palun": "Selles suunas harjutusi pole. Vali menüüst teine suund.",
	"translation.tolkimise_harjutamine": "Tõlkeharjutused",
	"translation.tubli_joudsid_loppu_vajuta": "Tubli, jõudsid lõppu! OK viib tagasi.",
	"translation.vale_vastus_proovi_uuesti": "Vale. Proovi uuesti!",
	"translation.vali_suund_milles_soovid": "Vali tõlkesuund. Vihjed ja vastuse kontroll on alati käepärast.",
	"translation.vihje_on_saadaval_kui": "Vihje on nüüd saadaval.",
}

_active: dict[str, str] = ET


def set_language(catalog: dict[str, str]) -> None:
	"""Switch the UI language (call at startup, before importing the views)."""
	global _active
	_active = catalog


def t(key: str, **values: object) -> str:
	"""Look up *key* in the active language and fill in any *values*."""
	text = _active.get(key) or ET[key]
	return text.format(**values) if values else text


__all__ = ["ET", "set_language", "t"]
