#!/usr/bin/env python3
"""Add Ge'ez transliteration as a language to widase_mariam.json for the daily prayer chapter."""

import json

# Load the existing data
with open("data/widase_mariam.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Transliteration content keyed by section number (1-9)
transliteration = {
    1: "A'atib getsye wekulu entinaye be-ti'imrte Mesqel beSim Ab weWeld weMenfesQidus Ahadu Amlak Amen. beQidist Silassie inze a'amin we'itmehatsen ikehedike saytan beqidme zati Emye Qidist beteChristian inte-yiite Simye Mariam Tsion le-alem alem amen",
    2: "Niakuteke Egzio wene-siebihake Nibarekeke Egzio wenit-ameneke Nisi'ilke Egzio wenastebequake Nigenileke Egzio wenitqeney leSimike Qidus Nisegid-leke O zeleke, ysegid kulu birk weleke yitqeney kulu lisan Ante wi'itu, Amlak Amalikt, weEgzia Egaist, weNigus negest Amlak ante le'kulu -siga ze wele-kulu ze'nefs Wene-tsewi'ake nihne bekeme meharene Qidus weldike inze yibil: \u201cAntemu se, sobe ti\u2019tseliyu kemezi belu\u2026\u201d",
    3: "Abune zebeSemayat yitQedes simik timtsa Mengistik we-yikun fiqadik bekeme beSemay kemahu bemidi sisayene zelele-ileten habene yo hidig-lene abesane we-gegayen keme nih'neni ni-hidi leze abeselen eta'biane Egzio wist mensut ala-adhinene we-balihane, imkulu iqu isme ziake yiit Mengist, Hayle weSibha le-alem alem amen. be-selam Qidus Gabriel melak O Igzitye Mariam, Selam lechi Dingil be'hilinachi, weDingil be-sigachi Eme Egziabhare Tsebaot, Selam lechi Birukt anti em-anist, we-biruk firi'aykersichi te'fesihi fesiht O Milite Tsega Egziabihare mislechi se'ali we'tseli, mihret be'inti ane habe Fiqur Weldichi Eyesus Christos keme yisray lene haTe we'ine Amen.",
    4: "Tselot haimanot ne-amin be-ahadu Amlak Igziabhare Ab ahazye kulu gebarie Semayat we-midr Zeyaster'ee weze - eeyaster'ee Wene-amin be'ahadu Egzi Eyesus Christos Weld Ab Wahid ze-hulu misleyehu imqidme' yitfeTer alem Birhan ze'imberhan Amlak ze'im Amlak zebe aman zetewelde we'ako zetegebre ze-iruy misle Ab be-melekotu zebotu kulu kone weze-inbeliehuse albo zekone we-imenteni, zebe Semayeni weze-bemidreni zebe'inti ane leseb webeinte Medhanitine werede imsemayat tesebA wetesegewe imMenfes Qidus we'im Mariam imQidist Dingil kone bi'ise wete'seqle be'inte ane bemewa-ile Peelatos Pentenawi hame we mote we teqebre we-tensiA imutan ame salist ilet bekeme tsihuf wuste Qidusat metsahift arge be-sibhat wuste Semayat wenebere be-yemane Abuhu dagime yimetsi bisibhat yikonen hiyawane wemutane we-albo mahileqt le-Mengistu wene amin be-Menfes Qidus Egzi Mahiyawi zeseretse im-Ab nisegd wene-sebiho misle Ab weWeld zenebebe benebiyat wene Amin be-ahati Qidist BeteChristian inte la-ile kulu guba'e zeHawariat wene amin be-ahati Timqet lesiryeTe haTiyat Weni-sefo tinsa'e imutan wehiwete zeyimetsi le-aleme alem Amen",
    5: "Qidus, Qidus, Qidus Egziabhare tseba'ot fitsum mulu Semayat we-midre Qidesat sebhatike Niseged leke Christos misle Abuke hierr semayawi wemenfesike Qidus maheyewi isme metsa'ikeweadhankene",
    6: "Eseged le'Ab weWeld weMenfes Qidus ahate segdet (3 gize) Enze ahadu selestu we-inze selestu ahadu Yesielesu be'akalat, weyiTewahdu bemelekot Eseged leEgitene Mariam Dingil, Weladite Amlak Eseged leMesqel Egzi'ine Eyesus Christos zeteQedese bedemu kibur Mesqel Hailine Mesqel Tsinene Mesqel Beyzane Mesqel Medhanite Nesfine Aihud kihidu, nehnese amene we'ile amene behaile Mesqelu dihine",
    7: "Sibhat leab sbhat leWeld sbhat leMenfes Qidus (3 gize) -ydelwomu leAb leweld weleMenfes Qidus sbhat egzi-etne mariam Dingil Weladite Amlak - ydelwa Egzi-etne Mariam Dengl Weladite Amlak sbhat leMesqele Egzine Eyesus kristos - ydelwo leMesqele Egzine Eyesus Christos Christos bemhretu yzekrene - amen webedagme metsa'itu iyastahafrene - amen lesibhotu Simu yanqhane - amen webe-amlikotu yatsne'ane - amen Egzitne Mariam Dingl Weladite Amlak, a'argi tselotne - amen we-astesri kulo hatiatne - amen qidme menberu le-Egzine - amen lezeable'ane zente hbste - esme lealem mhretu welezeasteyene zente tswa-e - esme lealem mhretu welezeser'alene sisayene we arazene - esme lealem mhretu wlezetageselene kulo hatiatine - esme lealem mhretu welezewhabene Sigahu Qeduse weDemu Kibure - esme lealem mhretu wele ze-abtsehane eske zati se'at - esme lealem mhretu nehab lotu sibhat weako-tiet le-Egziabhier liul weleWeladitu Dingil weleMesqelu Kibur yitakot weysebah smu le-Egziabhier wetre bekulu gzie webe kulu se'at.",
    8: "\u201cSelam we lechi\u201d inze nisegid neblechi Mariam Emene, nastebe'quachi Em-arwie Ne'awi temahatsen bichi Beinte Hannah Emichi, weEyaqem Abuchi Mahberene yom Dingil, barichi",
    9: "Tselot Egzitine Mariam Dingil Weladite Amlak: \u201cTe'abyo Nefsiye leEgziabhare wet'tit-hasey menfesiye BeAmlachiye weMedhaniye Esme re'iye himama leAmetu Nahu emye'zese yastebetsiuni kwulu twlid Esme Gebre leete Hayl abiyate weQidus simu Wesahluni leTwulde twulid Le'lile yiferihiwo weGebre Hayl bemezra'itu wezerewomu le'ele ya'abyu hilina l'bomu we-nesetomu lehayalan emena'brtihomu A'ebeyomu le'tehutan we-atsgebomu embereketu le'rhuban wefenewomu e'raqomu le'beulan we-tewekfo leIsrael Qul'eyhu wetezekere Sahlo zeyibielomu leAbewine leAbraham welezeru iske le-alem\u201d",
}

# Add transliteration to book_name
data["book_name"]["transliteration"] = "Widase Mariam"

# Find the daily chapter and add transliteration to each section
for chapter in data["chapters"]:
    if chapter["chapter"] == "daily":
        # Add transliteration to chapter_name
        chapter["chapter_name"]["transliteration"] = "Tselot zezewetr"

        for section in chapter["sections"]:
            section_num = section["section"]
            if section_num in transliteration:
                section["text"]["transliteration"] = transliteration[section_num]
        break

# Write back
with open("data/widase_mariam.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Also update the minified version
with open("data/widase_mariam.min.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

print("Done! Added Ge'ez transliteration to daily prayer sections 1-9.")
