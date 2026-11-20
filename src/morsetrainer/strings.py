"""All user-facing UI text in one place.

Code asks for text by key: ``t("home.tutvustus")`` or, for messages with
values, ``t("common.progress", percent=42.0)`` (``str.format`` placeholders).

To add a language, copy ``ET`` to a new dict with the same keys, translate the
values and call ``set_language(EN)`` at startup, before the application
modules are imported (a few labels are looked up at import time). Missing keys
fall back to Estonian.
"""

from __future__ import annotations

ET: dict[str, str] = {
	# app
	"app.morsekoodi_oppimisprogramm": "Morsekoodi õppimisprogramm",
	# audio
	"audio.heli_ei_saa_esitada": "Heli ei saa esitada.",
	"audio.helikorgus": "Helikõrgus\n",
	"audio.helisatted_ja_salvestus": "Helisätted ja salvestus",
	"audio.heliseadet_ei_leitud_esitamine": "Heliseadet ei leitud: esitamine pole võimalik, salvestamine töötab.",
	"audio.helitugevus": "Helitugevus\n",
	"audio.kehtivad_koigis_harjutustes_kui": "Kehtivad kõigis harjutustes. Kui üldine kiirus on väiksem, jäävad\ntähed kiireks, aga vahed pikenevad (Farnsworthi meetod).",
	"audio.peata_heli": "Peata heli",
	"audio.salvesta_heli": "Salvesta heli",
	"audio.salvesta_nimega": "Salvesta nimega...",
	"audio.tahtede_kiirus": "Tähtede\nkiirus",
	"audio.uldine_kiirus": "Üldine\nkiirus",
	# common
	"common.esita_heli": "Esita heli",
	"common.heli_ei_onnestunud_esitada": "Heli ei õnnestunud esitada.",
	"common.liigu_edasi": "Liigu edasi",
	"common.liigu_tagasi": "Liigu tagasi",
	"common.lopeta_treening": "Lõpeta treening",
	"common.lopp": "Lõpp",
	"common.morse_tekst": "Morse → tekst",
	"common.ok": "OK",
	"common.progress": "{percent:.1f}% läbitud",
	"common.question_counter": "Küsimus {number}/{total}",
	"common.tagasi": "Tagasi",
	"common.tagasi_avalehele": "Tagasi avalehele",
	"common.tagasi_valikute_juurde": "Tagasi valikute juurde",
	"common.tekst_morse": "Tekst → Morse",
	# error
	"error.andmed_ei_uhti_kontrolli": "Andmed ei ühti. Kontrolli sisendit.",
	"error.generic": "Tekkis viga: {details}",
	"error.heli_esitamine_ebaonnestus": "Heli esitamine ebaõnnestus.",
	"error.heli_esitamiseks_puudub_morsekoodi": "Heli esitamiseks puudub morsekoodi sisu.",
	"error.helifaili_loomine_ebaonnestus": "Helifaili loomine ebaõnnestus.",
	"error.helifaili_salvestamine_ebaonnestus": "Helifaili salvestamine ebaõnnestus.",
	"error.oled_joudnud_harjutuse_loppu": "Oled jõudnud harjutuse lõppu.",
	"error.palun_sisesta_tekst_enne": "Palun sisesta tekst enne tõlkimist.",
	"error.ressursi_laadimine_ebaonnestus": "Ressursi laadimine ebaõnnestus.",
	"error.seadistus_on_vigane": "Seadistus on vigane.",
	"error.seanss_on_vigases_olekus": "Seanss on vigases olekus. Palun alusta uuesti.",
	"error.seanss_pole_kaivitatud_palun": "Seanss pole käivitatud. Palun alusta uuesti.",
	"error.sisend_sisaldab_morsekoodi_mida": "Sisend sisaldab morsekoodi, mida ei tunta.",
	"error.sisend_sisaldab_tahemarki_mida": "Sisend sisaldab tähemärki, mida ei saa morsekoodiks teisendada.",
	"error.tolkimine_ebaonnestus_kontrolli_sisendit": "Tõlkimine ebaõnnestus. Kontrolli sisendit.",
	"error.unsupported_character": "Tähemärk '{char}' pole toetatud.",
	"error.vajalikku_ressurssi_ei_leitud": "Vajalikku ressurssi ei leitud.",
	"error.valitud_reziim_pole_toetatud": "Valitud režiim pole toetatud.",
	# flashcards
	"flashcards.heli": "Heli",
	"flashcards.kirjavahemarkide_andmed_puuduvad": "Kirjavahemärkide andmed puuduvad.",
	"flashcards.kuula_heli": "Kuula heli",
	"flashcards.numbrikaartide_andmed_puuduvad": "Numbrikaartide andmed puuduvad.",
	"flashcards.opi_kirjavahemarke": "Õpi kirjavahemärke",
	"flashcards.opi_numbreid": "Õpi numbreid",
	"flashcards.opi_tahti": "Õpi tähti",
	"flashcards.poora_kaarti": "Pööra kaarti",
	"flashcards.sumbolitega_tutvumine": "Sümbolitega tutvumine",
	"flashcards.tahekaartide_andmed_puuduvad": "Tähekaartide andmed puuduvad.",
	"flashcards.tubli_too_koik_kaardid": "Tubli töö! Kõik kaardid on läbitud. Vajuta 'OK', et naasta valikute juurde.",
	"flashcards.vali_kategooria_mida_soovid": "Vali kategooria, mida soovid õppida.",
	# grade
	"grade.a": "A (suurepärane) / {percentage}%",
	"grade.b": "B (väga hea) / {percentage}%",
	"grade.c": "C (hea) / {percentage}%",
	"grade.d": "D (rahuldav) / {percentage}%",
	"grade.e": "E (kasin) / {percentage}%",
	"grade.f": "F (mitterahuldav) / {percentage}%",
	"grade.hakkab_juba_vaikselt_tulema": "Hakkab juba vaikselt tulema.\nHarjuta veel mõned korrad ning kindlasti saad veelgi parema tulemuse.",
	"grade.paris_hea_tundub_et": "Päris hea. Tundub, et hakkad palju paremaks muutuma.",
	"grade.punktisumma_pole_just_koige": "Punktisumma pole just kõige parem, aga arenguruumi on kõigil piisavalt.",
	"grade.score": "Vastasid {points} / {max_points} õigesti",
	"grade.vaga_super_oled_testi": "Väga super.\nOled testi sooritanud headele punktidele ning võid ennast nimetada morsekoodi meistriks.",
	# home
	"home.harjutused": "Harjutused",
	"home.morsekood_moodab_aega_uhikutes": "Morsekood mõõdab aega 'ühikutes': punkt kestab ühe ühiku, kriips kolm ühikut. Sümboli sees eraldab kahe signaali vahelist pausi ühe ühiku pikkune vaikuse segment. Sümbolite vahel hoitakse kolme ühiku pikkust pausi ja sõnade vahel seitset ühikut. Tekstina kirjutades tähistatakse signaale punktide ja sidekriipsudega (näiteks . ja -). Ühe ühiku pikkune paus pole kuvatud, sümbolite vahe tähistatakse ühe tühiku abil ning sõnade vahel on kolm tühikut tühja ala.",
	"home.morsekoodi_rakendus": "Morsekoodi rakendus",
	"home.ope": "Õpe",
	"home.ope_voimaldab_flashcard_meetodi": "Õpe võimaldab Flashcard meetodi abil süsteemselt läbi käia tähed, numbrid ja kirjavahemärgid ning kuulata nende helinäiteid. Tõlkimises saab harjutada keerulisemaid näiteid mõlemas suunas: tekst → morse ja morse → tekst; lisaks saab vihjeid ja kontrollida vastuseid. Testis käivitatakse taimeriga töö, mille lõpus saab põhjaliku tagasiside ning võimaluse vastused üle vaadata.",
	"home.programm_morsekoodi_oppimiseks_harjutamiseks": "Programm morsekoodi õppimiseks, harjutamiseks ja testimiseks ning tõlkimiseks.",
	"home.sandbox": "Sandbox",
	"home.test": "Test",
	"home.theme_dark": "Tume",
	"home.theme_dark_emoji": "🌙 Tume",
	"home.theme_light": "Hele",
	"home.theme_light_emoji": "🌞 Hele",
	"home.tutvustus": "Tutvustus",
	"home.valju_programmist": "Välju programmist",
	# review
	"review.correct": "See oli täiesti õige. Said küsimuse eest {points} punkti.\n\nÕige vastus oli tõepoolest\n{expected}.",
	"review.labivaatus": "Läbivaatus",
	"review.labivaatus_lopetatud": "Läbivaatus lõpetatud",
	"review.lopeta_labivaatus": "Lõpeta läbivaatus",
	"review.oled_koik_kusimused_ule": "Oled kõik küsimused üle vaadanud.\nNaase tulemuste lehele, et näha kokkuvõtet.",
	"review.partial": "See oli osaliselt õige. Said küsimuse eest {points} punkti.\n\nÕige vastus oli tegelikult\n{expected}.",
	"review.time_spent": "Sul kulus küsimuse tõlkimiseks aega {seconds} sekundit.",
	"review.wrong": "See oli vale. Said küsimuse eest {points} punkti.\n\nÕige vastus oli hoopis\n{expected}.",
	"review.your_answer": "Sinu vastus oli: {answer}",
	# sandbox
	"sandbox.ei_ole_helifaili_salvestamiseks": "Ei ole helifaili salvestamiseks.",
	"sandbox.file_saved": "Fail salvestatud:\n{path}",
	"sandbox.helifail_salvestatud": "Helifail salvestatud",
	"sandbox.helifaili_ei_onnestunud_salvestada": "Helifaili ei õnnestunud salvestada.",
	"sandbox.katseta_erinevaid_tolkesuundi_muuda": "Katseta erinevaid tõlkesuundi, muuda helisätteid ning salvesta tulemused.",
	"sandbox.kliki_tolgi_et_kuvada": "Kliki tõlgi, et kuvada tulemus...",
	"sandbox.morse": "Morse",
	"sandbox.puhasta": "Puhasta",
	"sandbox.salvesta_helifail": "Salvesta helifail",
	"sandbox.sandbox_tolkimine": "Sandbox tõlkimine",
	"sandbox.sisesta_algtekst_morsekood_siia": "Sisesta algtekst/morsekood siia...",
	"sandbox.sisesta_tekst_voi_morsekood": "Sisesta tekst või morsekood ning vajuta 'Tõlgi'. Kasti tühjendamiseks kliki 'Puhasta'.",
	"sandbox.tekst": "Tekst",
	"sandbox.tolgi": "Tõlgi",
	"sandbox.tolkesuund": "Tõlkesuund",
	"sandbox.wav_helifail": "WAV helifail",
	# test
	"test.alusta": "Alusta",
	"test.ei_soovi_kordamist": "Ei, soovi kordamist",
	"test.jah_alusta_testi": "Jah, alusta testi",
	"test.kas_oled_valmis": "Kas oled valmis?",
	"test.katkesta_test": "Katkesta test",
	"test.lopeta_test": "Lõpeta test",
	"test.oled_joudnud_testreziimi_juurde": "Oled jõudnud testrežiimi juurde.\n\nSoorita taimeriga töö, et proovile panna oma morsekoodi oskused.\n\nKui oled valmis, alusta testimist või pöördu tagasi kordama.",
	"test.progress_zero": "0.0% läbitud",
	"test.question_zero": "Küsimus 0/0",
	"test.sentence_speed": "Lausete kiirus: {speed} lauset/min",
	"test.sisesta_vastus_siia": "Sisesta vastus siia",
	"test.tagasi_menuusse": "Tagasi menüüsse",
	"test.testi_alustades_kaivitub_taimer": "Testi alustades käivitub taimer ja lahkumine katkestab katse.\nSoovi korral saad veel kord üle vaadata teised õppemoodulid.",
	"test.testi_andmed_puuduvad": "Testi andmed puuduvad",
	"test.testi_ennast": "Testi ennast",
	"test.testreziimi_jaoks_pole_hetkel": "Testrežiimi jaoks pole hetkel ühtegi küsimust saadaval. Palun naase avalehele.",
	"test.tulemused": "Tulemused",
	"test.vaata_vastuseid": "Vaata vastuseid",
	"test.word_speed": "Sõnade kiirus: {speed} sõna/min",
	# translation
	"translation.andmeid_pole": "Andmeid pole",
	"translation.heli_esitatakse": "Heli esitatakse.",
	"translation.kontrolli_vastust": "Kontrolli vastust",
	"translation.naita_vihjet": "Näita vihjet",
	"translation.oige_vastus_tubli_too": "Õige vastus! Tubli töö.",
	"translation.sellele_kirjele_heli_pole": "Sellele kirjele heli pole.",
	"translation.sisesta_morsekood_nt": "Sisesta morsekood (nt .- -...)",
	"translation.sisesta_tekst": "Sisesta tekst",
	"translation.tolketreeningu_andmed_puuduvad_palun": "Tõlketreeningu andmed puuduvad. Palun naase menüüsse ja vali muu režiim.",
	"translation.tolkimise_harjutamine": "Tõlkimise harjutamine",
	"translation.tubli_joudsid_loppu_vajuta": "Tubli! Jõudsid lõppu. Vajuta nupul 'OK!', et liikuda tagasi eelmisele lehele.",
	"translation.vale_vastus_proovi_uuesti": "Vale vastus. Proovi uuesti!",
	"translation.vali_suund_milles_soovid": "Vali suund, milles soovid tõlkimist harjutada. Saad kasutada vihjeid ning vastuseid kontrollida.",
	"translation.vihje_on_saadaval_kui": "Vihje on saadaval, kui soovid.",
}

_active: dict[str, str] = ET


def set_language(catalog: dict[str, str]) -> None:
	"""Switch the UI language (call before building the views)."""
	global _active
	_active = catalog


def t(key: str, **values: object) -> str:
	"""Look up *key* in the active language and fill in any *values*."""
	text = _active.get(key) or ET[key]
	return text.format(**values) if values else text


__all__ = ["ET", "set_language", "t"]
