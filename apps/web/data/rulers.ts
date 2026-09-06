// apps/web/data/rulers.ts
// Curated "Entity Intelligence" content — notable rulers and facts for a
// selected set of major civilizations. Not every entity has an entry; the
// EntityPanel simply omits the section when none exists for the slug.

export interface RulerEntry {
  name: string
  years: string
  title: string
}

export interface EntityFacts {
  rulers: RulerEntry[]
  facts: string[]
}

export const ENTITY_FACTS: Record<string, EntityFacts> = {
  'roman-empire': {
    rulers: [
      { name: 'Augustus', years: '27 BCE – 14 CE', title: 'Emperor' },
      { name: 'Trajan', years: '98 – 117 CE', title: 'Emperor' },
      { name: 'Constantine I', years: '306 – 337 CE', title: 'Emperor' },
      { name: 'Theodosius I', years: '379 – 395 CE', title: 'Emperor' },
    ],
    facts: [
      'At its height under Trajan, the empire covered roughly 5 million km².',
      'The Roman road network totaled more than 400,000 km, connecting the empire from Britain to Mesopotamia.',
      'The Colosseum, completed in 80 CE, could hold an estimated 50,000 spectators.',
    ],
  },
  'roman-republic': {
    rulers: [
      { name: 'Scipio Africanus', years: '236 – 183 BCE', title: 'General' },
      { name: 'Sulla', years: '82 – 79 BCE', title: 'Dictator' },
      { name: 'Julius Caesar', years: '49 – 44 BCE', title: 'Dictator' },
    ],
    facts: [
      'The Republic had no monarch — two annually elected Consuls held executive power.',
      'It lasted almost 500 years, from the overthrow of the last king in 509 BCE to Augustus in 27 BCE.',
      'Rome fought three Punic Wars against Carthage over more than a century, ending with Carthage’s destruction in 146 BCE.',
    ],
  },
  'byzantine-empire': {
    rulers: [
      { name: 'Justinian I', years: '527 – 565', title: 'Emperor' },
      { name: 'Basil II', years: '976 – 1025', title: 'Emperor' },
      { name: 'Constantine XI', years: '1449 – 1453', title: 'Emperor' },
    ],
    facts: [
      'The Hagia Sophia was completed in just under six years under Justinian, in 537.',
      'It survived for over a thousand years after Rome itself fell in 476.',
      'Constantine XI died fighting in the streets during the fall of Constantinople in 1453.',
    ],
  },
  'ottoman-empire': {
    rulers: [
      { name: 'Osman I', years: '1299 – 1323/24', title: 'Bey' },
      { name: 'Mehmed II "the Conqueror"', years: '1444–46, 1451–81', title: 'Sultan' },
      { name: 'Suleiman the Magnificent', years: '1520 – 1566', title: 'Sultan' },
      { name: 'Abdulhamid II', years: '1876 – 1909', title: 'Sultan' },
    ],
    facts: [
      'The empire endured for 623 years, one of the longest-lived states in history.',
      'Istanbul was the largest city in Europe for much of the empire’s existence.',
      'Mehmed II captured Constantinople in 1453, ending the Byzantine Empire after 1,123 years.',
    ],
  },
  'mongol-empire': {
    rulers: [
      { name: 'Genghis Khan', years: '1206 – 1227', title: 'Great Khan' },
      { name: 'Ögedei Khan', years: '1229 – 1241', title: 'Great Khan' },
      { name: 'Kublai Khan', years: '1260 – 1294', title: 'Great Khan / Emperor' },
    ],
    facts: [
      'At roughly 24 million km², it remains the largest contiguous land empire in history.',
      'The Pax Mongolica made the Silk Road safer than it had ever been, boosting trade between Europe and Asia.',
      'The Mongol postal relay system (the Yam) could carry messages over 200 miles in a single day.',
    ],
  },
  'mughal-empire': {
    rulers: [
      { name: 'Babur', years: '1526 – 1530', title: 'Emperor' },
      { name: 'Akbar the Great', years: '1556 – 1605', title: 'Emperor' },
      { name: 'Shah Jahan', years: '1628 – 1658', title: 'Emperor' },
      { name: 'Aurangzeb', years: '1658 – 1707', title: 'Emperor' },
    ],
    facts: [
      'Shah Jahan built the Taj Mahal between 1632 and 1653 as a mausoleum for his wife Mumtaz Mahal.',
      'At its peak, the empire is estimated to have accounted for roughly a quarter of world GDP.',
      'Akbar promoted religious tolerance across his Hindu- and Muslim-majority territories.',
    ],
  },
  'macedonian-empire': {
    rulers: [
      { name: 'Philip II', years: '359 – 336 BCE', title: 'King' },
      { name: 'Alexander the Great', years: '336 – 323 BCE', title: 'King' },
    ],
    facts: [
      'Alexander reportedly never lost a battle in over a decade of campaigning.',
      'He founded over twenty cities bearing some form of his own name, most famously Alexandria in Egypt.',
      'His empire stretched from Greece to the Indus Valley — roughly 5.2 million km² at its peak.',
    ],
  },
  'achaemenid-persia': {
    rulers: [
      { name: 'Cyrus the Great', years: '559 – 530 BCE', title: 'King of Kings' },
      { name: 'Darius I', years: '522 – 486 BCE', title: 'King of Kings' },
      { name: 'Xerxes I', years: '486 – 465 BCE', title: 'King of Kings' },
    ],
    facts: [
      'It was the first empire to span three continents: Asia, Africa, and Europe.',
      'The Royal Road built under Darius I stretched roughly 2,700 km from Susa to Sardis.',
      'The Cyrus Cylinder is often cited as an early statement on the treatment of conquered peoples.',
    ],
  },
  'han-dynasty': {
    rulers: [
      { name: 'Emperor Gaozu (Liu Bang)', years: '202 – 195 BCE', title: 'Emperor' },
      { name: 'Emperor Wu', years: '141 – 87 BCE', title: 'Emperor' },
      { name: 'Emperor Guangwu', years: '25 – 57 CE', title: 'Emperor' },
    ],
    facts: [
      'The Silk Road trade network opened during Emperor Wu’s reign.',
      'Paper was invented (or at least first documented) during the Han period.',
      'At its height the population reached roughly 60 million — comparable to the Roman Empire at the same time.',
    ],
  },
  'tang-dynasty': {
    rulers: [
      { name: 'Emperor Taizong', years: '626 – 649', title: 'Emperor' },
      { name: 'Empress Wu Zetian', years: '690 – 705', title: 'Emperor' },
      { name: 'Emperor Xuanzong', years: '712 – 756', title: 'Emperor' },
    ],
    facts: [
      'Wu Zetian remains the only woman to have ruled China in her own name as emperor.',
      'The capital, Chang’an, was likely the largest city in the world at the time, with around a million residents.',
      'Woodblock printing was developed during the Tang period, centuries before Gutenberg.',
    ],
  },
  'qing-dynasty': {
    rulers: [
      { name: 'Shunzhi Emperor', years: '1644 – 1661', title: 'Emperor' },
      { name: 'Kangxi Emperor', years: '1661 – 1722', title: 'Emperor' },
      { name: 'Qianlong Emperor', years: '1735 – 1796', title: 'Emperor' },
      { name: 'Puyi', years: '1908 – 1912', title: 'Emperor' },
    ],
    facts: [
      'The Kangxi Emperor’s 61-year reign is the longest of any Chinese monarch.',
      'China’s population grew from roughly 150 million to over 400 million under Qing rule.',
      'The dynasty ended with the 1911 Xinhai Revolution and Puyi’s abdication in 1912.',
    ],
  },
  'abbasid-caliphate': {
    rulers: [
      { name: 'As-Saffah', years: '750 – 754', title: 'Caliph' },
      { name: 'Al-Mansur', years: '754 – 775', title: 'Caliph' },
      { name: 'Harun al-Rashid', years: '786 – 809', title: 'Caliph' },
    ],
    facts: [
      'Baghdad’s House of Wisdom was a leading center of scholarship during the Islamic Golden Age.',
      'Abbasid scholars preserved and translated a huge body of Greek philosophical and scientific texts.',
      'The caliphate’s political power was effectively ended by the Mongol sack of Baghdad in 1258.',
    ],
  },
  'mali-empire': {
    rulers: [
      { name: 'Sundiata Keita', years: '1235 – 1255', title: 'Mansa (Emperor)' },
      { name: 'Mansa Musa', years: '1312 – 1337', title: 'Mansa (Emperor)' },
    ],
    facts: [
      'Mansa Musa is often cited as the wealthiest individual in recorded history.',
      'His 1324 pilgrimage to Mecca reportedly devalued gold in Cairo for years afterward from the sheer amount he gave away.',
      'Timbuktu grew into a major center of Islamic scholarship and manuscript production under Mali’s rule.',
    ],
  },
  'aztec-empire': {
    rulers: [
      { name: 'Itzcoatl', years: '1427 – 1440', title: 'Tlatoani' },
      { name: 'Moctezuma I', years: '1440 – 1469', title: 'Tlatoani' },
      { name: 'Moctezuma II', years: '1502 – 1520', title: 'Tlatoani' },
    ],
    facts: [
      'The capital, Tenochtitlan, had an estimated 200,000 residents — larger than most European cities of the time.',
      'The city was built on an island in Lake Texcoco, linked to shore by causeways and threaded with canals.',
      'The empire fell to Hernán Cortés and his allies in 1521, just under a century after it began.',
    ],
  },
  'inca-empire': {
    rulers: [
      { name: 'Pachacuti', years: '1438 – 1471', title: 'Sapa Inca' },
      { name: 'Huayna Capac', years: '1493 – 1527', title: 'Sapa Inca' },
      { name: 'Atahualpa', years: '1532 – 1533', title: 'Sapa Inca' },
    ],
    facts: [
      'It was the largest empire in pre-Columbian America.',
      'The road network (Qhapaq Ñan) spanned an estimated 40,000 km through the Andes.',
      'The Inca had no written script, but recorded records and accounts using knotted cords called quipu.',
    ],
  },
  'british-empire': {
    rulers: [
      { name: 'Elizabeth I', years: '1558 – 1603', title: 'Queen' },
      { name: 'Victoria', years: '1837 – 1901', title: 'Queen / Empress of India' },
      { name: 'George V', years: '1910 – 1936', title: 'King' },
      { name: 'Elizabeth II', years: '1952 – 2022', title: 'Queen' },
    ],
    facts: [
      'At its territorial peak around 1920, it covered close to a quarter of the Earth’s land area.',
      'It ruled over an estimated 412 million people at that peak — about a fifth of the world’s population.',
      'The phrase "the empire on which the sun never sets" reflected its holdings spanning every longitude.',
    ],
  },
  'russian-empire': {
    rulers: [
      { name: 'Peter the Great', years: '1682 – 1725', title: 'Tsar / Emperor' },
      { name: 'Catherine the Great', years: '1762 – 1796', title: 'Empress' },
      { name: 'Alexander II', years: '1855 – 1881', title: 'Emperor' },
      { name: 'Nicholas II', years: '1894 – 1917', title: 'Emperor' },
    ],
    facts: [
      'Peter the Great formally proclaimed the Russian Empire in 1721 after victory in the Great Northern War.',
      'At its height it spanned 11 time zones’ worth of longitude across Europe, Asia, and briefly North America (Alaska).',
      'It ended with the 1917 Revolution; Nicholas II and his family were executed the following year.',
    ],
  },
  'french-empire': {
    rulers: [
      { name: 'Cardinal Richelieu', years: '1620s – 1642', title: 'Chief Minister' },
      { name: 'Napoleon III', years: '1852 – 1870', title: 'Emperor' },
      { name: 'Jules Ferry', years: '1880 – 1885 (PM)', title: 'Prime Minister' },
    ],
    facts: [
      'It became the second-largest colonial empire in history after the British Empire.',
      'At its interwar peak in the 1920s it covered roughly 13 million km².',
      'Algeria was governed as an integral part of France itself, not administered as a separate colony.',
    ],
  },
  'ancient-egypt': {
    rulers: [
      { name: 'Narmer', years: 'c. 3100 BCE', title: 'Pharaoh' },
      { name: 'Khufu', years: 'c. 2589 – 2566 BCE', title: 'Pharaoh' },
      { name: 'Hatshepsut', years: '1479 – 1458 BCE', title: 'Pharaoh' },
      { name: 'Ramesses II', years: '1279 – 1213 BCE', title: 'Pharaoh' },
      { name: 'Tutankhamun', years: '1332 – 1323 BCE', title: 'Pharaoh' },
    ],
    facts: [
      'The civilization endured for well over 3,000 years — longer than the gap between us and Cleopatra.',
      'The Great Pyramid of Giza was the tallest human-made structure on Earth for roughly 3,800 years.',
      'Hieroglyphic writing was in continuous use for over three millennia.',
    ],
  },
  'kingdom-of-england': {
    rulers: [
      { name: 'Æthelstan', years: '927 – 939', title: 'King' },
      { name: 'William the Conqueror', years: '1066 – 1087', title: 'King' },
      { name: 'Henry VIII', years: '1509 – 1547', title: 'King' },
      { name: 'Elizabeth I', years: '1558 – 1603', title: 'Queen' },
      { name: 'Anne', years: '1702 – 1707', title: 'Queen' },
    ],
    facts: [
      'Æthelstan is generally regarded as the first king to rule a unified England, from 927.',
      'The Norman Conquest of 1066 reshaped English language, law, and the aristocracy.',
      'Queen Anne was the kingdom’s last monarch — the 1707 Acts of Union merged England and Scotland into Great Britain.',
    ],
  },
  'united-states': {
    rulers: [
      { name: 'George Washington', years: '1789 – 1797', title: 'President' },
      { name: 'Abraham Lincoln', years: '1861 – 1865', title: 'President' },
      { name: 'Franklin D. Roosevelt', years: '1933 – 1945', title: 'President' },
    ],
    facts: [
      'It grew from 13 original states along the Atlantic coast to 50 states spanning the continent and the Pacific.',
      'It became the world’s largest economy by the late 19th century.',
      'The 1787 Constitution is the oldest still-functioning written national constitution in the world.',
    ],
  },
  'japanese-empire': {
    rulers: [
      { name: 'Emperor Meiji', years: '1867 – 1912', title: 'Emperor' },
      { name: 'Emperor Taishō', years: '1912 – 1926', title: 'Emperor' },
      { name: 'Emperor Shōwa (Hirohito)', years: '1926 – 1989', title: 'Emperor' },
    ],
    facts: [
      'Japan rapidly industrialized after the 1868 Meiji Restoration, transforming from an isolated feudal state in decades.',
      'Its 1905 victory over Russia was the first time an Asian power had defeated a European one in the modern era.',
      'The empire was formally dissolved after Japan’s surrender in 1945, during Emperor Shōwa’s reign.',
    ],
  },
  'akkadian-empire': {
    rulers: [
      { name: 'Sargon of Akkad', years: 'c. 2334 – 2279 BCE', title: 'King' },
      { name: 'Naram-Sin', years: 'c. 2254 – 2218 BCE', title: 'King' },
    ],
    facts: [
      'It is generally considered the first empire in world history to unite multiple city-states under one central ruler.',
      'Sargon’s dynasty lasted roughly 180 years before collapsing under invasion and possibly climate-driven drought.',
      'Naram-Sin, Sargon’s grandson, was the first Mesopotamian king to declare himself a living god.',
    ],
  },
  'assyrian-empire': {
    rulers: [
      { name: 'Tiglath-Pileser III', years: '745 – 727 BCE', title: 'King' },
      { name: 'Sargon II', years: '722 – 705 BCE', title: 'King' },
      { name: 'Esarhaddon', years: '681 – 669 BCE', title: 'King' },
      { name: 'Ashurbanipal', years: '669 – 631 BCE', title: 'King' },
    ],
    facts: [
      'Ashurbanipal’s library at Nineveh held an estimated 30,000 clay tablets — one of the first great libraries in history.',
      'Assyria pioneered an organized road and postal relay system centuries before the Persian Royal Road.',
      'Esarhaddon briefly conquered Egypt in 671 BCE, extending Assyrian control across the entire Fertile Crescent.',
    ],
  },
  'babylonian-empire': {
    rulers: [
      { name: 'Hammurabi', years: '1792 – 1750 BCE', title: 'King' },
      { name: 'Nebuchadnezzar II', years: '605 – 562 BCE', title: 'King' },
    ],
    facts: [
      'Hammurabi’s Code, roughly 282 laws carved on a stone stele, is one of the earliest deciphered legal texts.',
      'Nebuchadnezzar II conquered Jerusalem in 587 BCE and exiled much of its population to Babylon.',
      'The empire fell to Cyrus the Great of Persia in 539 BCE, reportedly without a major battle.',
    ],
  },
  'carthage': {
    rulers: [
      { name: 'Hamilcar Barca', years: '247 – 228 BCE', title: 'General' },
      { name: 'Hannibal Barca', years: '221 – 202 BCE', title: 'General' },
    ],
    facts: [
      'Founded by Phoenician settlers from Tyre around 814 BCE.',
      'Hannibal famously marched an army — elephants included — across the Alps to invade Italy in 218 BCE.',
      'Rome destroyed Carthage utterly in 146 BCE at the end of the Third Punic War.',
    ],
  },
  'delhi-sultanate': {
    rulers: [
      { name: 'Qutb al-Din Aibak', years: '1206 – 1210', title: 'Sultan' },
      { name: 'Iltutmish', years: '1211 – 1236', title: 'Sultan' },
      { name: 'Muhammad bin Tughluq', years: '1325 – 1351', title: 'Sultan' },
    ],
    facts: [
      'Began construction of the Qutb Minar, still the tallest brick minaret in the world.',
      'Repelled repeated Mongol invasions of northern India in the 13th and 14th centuries.',
      'Ended in 1526 when Babur defeated the last Sultan at the First Battle of Panipat, founding the Mughal Empire.',
    ],
  },
  'eastern-roman-empire': {
    rulers: [
      { name: 'Constantine I', years: '324 – 337', title: 'Emperor' },
      { name: 'Theodosius I', years: '379 – 395', title: 'Emperor' },
      { name: 'Justinian I', years: '527 – 565', title: 'Emperor' },
    ],
    facts: [
      'This is the same Roman state usually called the "Byzantine Empire" in later scholarship — its people always called themselves Romans.',
      'Constantinople, its capital from 330, controlled the only land route between Europe and Asia at the Bosphorus.',
      'It outlasted the Western Roman Empire by nearly a thousand years, falling to the Ottomans only in 1453.',
    ],
  },
  'germanic-tribes': {
    rulers: [
      { name: 'Arminius', years: 'd. 21 CE', title: 'Chieftain' },
      { name: 'Alaric I', years: '395 – 410', title: 'King of the Visigoths' },
      { name: 'Clovis I', years: '481 – 511', title: 'King of the Franks' },
    ],
    facts: [
      'Arminius destroyed three entire Roman legions at the Battle of the Teutoburg Forest in 9 CE, halting Rome’s expansion into Germania.',
      'Alaric’s Visigoths sacked Rome in 410 — the first time the city had fallen to a foreign enemy in nearly 800 years.',
      'Clovis’s conversion to Christianity in 496 shaped the religious future of Western Europe.',
    ],
  },
  'ghana-empire': {
    rulers: [
      { name: 'Tunka Manin', years: 'c. 1068 (attested reign)', title: 'King' },
    ],
    facts: [
      'Grew wealthy by controlling and taxing trans-Saharan trade in gold and salt.',
      'Its capital, Koumbi Saleh, reportedly had separate quarters for the royal court and for Muslim merchants.',
      'Declined under pressure from Almoravid incursions and prolonged drought in the 11th-12th centuries.',
    ],
  },
  'golden-horde': {
    rulers: [
      { name: 'Batu Khan', years: '1227 – 1255', title: 'Khan' },
      { name: 'Uzbeg Khan', years: '1313 – 1341', title: 'Khan' },
    ],
    facts: [
      'Dominated the Russian principalities for over two centuries, exacting tribute in what Russian history calls the "Mongol Yoke."',
      'Uzbeg Khan made Islam the khanate’s state religion in the early 14th century.',
      'Fragmented in the 15th century into smaller khanates — Kazan, Crimea, Astrakhan — eventually absorbed by Russia.',
    ],
  },
  'greek-city-states': {
    rulers: [
      { name: 'Pericles', years: '461 – 429 BCE', title: 'Statesman (Athens)' },
      { name: 'Leonidas I', years: 'd. 480 BCE', title: 'King (Sparta)' },
      { name: 'Themistocles', years: 'fl. 480 BCE', title: 'General (Athens)' },
    ],
    facts: [
      'Athens pioneered direct democracy, where citizens voted directly on laws rather than through representatives.',
      'Spartan society was organized almost entirely around military training from childhood (the agoge).',
      'The Peloponnesian War between Athens and Sparta (431-404 BCE) lasted 27 years and exhausted both city-states.',
    ],
  },
  'gupta-empire': {
    rulers: [
      { name: 'Chandragupta I', years: '320 – 335', title: 'Emperor' },
      { name: 'Samudragupta', years: '335 – 375', title: 'Emperor' },
      { name: 'Chandragupta II', years: '375 – 415', title: 'Emperor' },
    ],
    facts: [
      'Often called classical India’s "Golden Age" for advances in mathematics, astronomy, and Sanskrit literature.',
      'Indian mathematicians of this era developed the decimal place-value system and the concept of zero.',
      'Declined under repeated invasions by the Huna (Hunnic) peoples in the late 5th century.',
    ],
  },
  'holy-roman-empire': {
    rulers: [
      { name: 'Otto I', years: '962 – 973', title: 'Emperor' },
      { name: 'Frederick Barbarossa', years: '1155 – 1190', title: 'Emperor' },
      { name: 'Charles V', years: '1519 – 1556', title: 'Emperor' },
    ],
    facts: [
      'Voltaire’s famous quip: it was "neither Holy, nor Roman, nor an Empire" — a loose patchwork of hundreds of semi-independent states.',
      'Charles V ruled it alongside the Spanish Empire, briefly making him one of the most powerful men in history.',
      'Dissolved in 1806 after Napoleon’s victories forced Emperor Francis II to abdicate the title.',
    ],
  },
  'ilkhanate': {
    rulers: [
      { name: 'Hulagu Khan', years: '1256 – 1265', title: 'Ilkhan' },
      { name: 'Ghazan Khan', years: '1295 – 1304', title: 'Ilkhan' },
    ],
    facts: [
      'Hulagu’s sack of Baghdad in 1258 ended the Abbasid Caliphate and killed the last reigning caliph.',
      'Ghazan Khan’s conversion to Islam in 1295 marked a major cultural turning point for the khanate.',
      'Fostered a rich Perso-Mongol artistic and administrative tradition that influenced later Persianate empires.',
    ],
  },
  'indus-valley-civilization': {
    rulers: [],
    facts: [
      'No king lists or named rulers are known — unusually for a Bronze Age civilization, no palaces or clear seats of monarchy have been found.',
      'Cities like Mohenjo-daro featured advanced urban planning: grid-pattern streets and covered drainage systems.',
      'Its script has never been deciphered, so its language, government, and beliefs remain largely a mystery.',
    ],
  },
  'khmer-empire': {
    rulers: [
      { name: 'Jayavarman II', years: '802 – 850', title: 'King' },
      { name: 'Suryavarman II', years: '1113 – 1150', title: 'King' },
      { name: 'Jayavarman VII', years: '1181 – 1218', title: 'King' },
    ],
    facts: [
      'Suryavarman II built Angkor Wat, still the largest religious monument in the world.',
      'The capital Angkor may have been the largest pre-industrial city on Earth, with up to a million residents.',
      'Tree-ring and hydrological evidence suggests the empire’s collapse was hastened by severe drought and flooding.',
    ],
  },
  'maurya-empire': {
    rulers: [
      { name: 'Chandragupta Maurya', years: '322 – 298 BCE', title: 'Emperor' },
      { name: 'Ashoka the Great', years: '268 – 232 BCE', title: 'Emperor' },
    ],
    facts: [
      'Ashoka’s edicts, carved into pillars and rock faces across the empire, are among the earliest deciphered Indian inscriptions.',
      'After the bloody conquest of Kalinga, Ashoka renounced further military conquest and promoted Buddhism.',
      'Its civil service and espionage network were described in the Arthashastra, an ancient treatise on statecraft.',
    ],
  },
  'ming-dynasty': {
    rulers: [
      { name: 'Hongwu Emperor', years: '1368 – 1398', title: 'Emperor' },
      { name: 'Yongle Emperor', years: '1402 – 1424', title: 'Emperor' },
      { name: 'Wanli Emperor', years: '1572 – 1620', title: 'Emperor' },
    ],
    facts: [
      'Admiral Zheng He led seven massive naval expeditions (1405-1433) reaching East Africa, decades before European exploration.',
      'The Yongle Emperor built the Forbidden City in Beijing, completed in 1420.',
      'Fell in 1644 to a combination of peasant rebellion and the invading Manchu armies that founded the Qing.',
    ],
  },
  'numidia': {
    rulers: [
      { name: 'Masinissa', years: '202 – 148 BCE', title: 'King' },
      { name: 'Jugurtha', years: '118 – 105 BCE', title: 'King' },
    ],
    facts: [
      'Numidian cavalry was prized throughout the ancient Mediterranean, serving in armies on both sides of the Punic Wars.',
      'Masinissa’s alliance with Rome against Carthage helped decide the outcome of the Second Punic War.',
      'Annexed by Rome after Jugurtha’s defeat and betrayal in the Jugurthine War.',
    ],
  },
  'parthian-empire': {
    rulers: [
      { name: 'Mithridates I', years: '171 – 132 BCE', title: 'King' },
      { name: 'Orodes II', years: '57 – 37 BCE', title: 'King' },
    ],
    facts: [
      'Crushed a Roman army under Crassus at the Battle of Carrhae in 53 BCE, one of Rome’s worst military disasters.',
      'Famous for the "Parthian shot" — mounted archers firing backward while feigning retreat.',
      'Controlled a key stretch of the Silk Road between the Roman and Chinese/Indian worlds.',
    ],
  },
  'portuguese-empire': {
    rulers: [
      { name: 'Prince Henry the Navigator', years: 'd. 1460', title: 'Patron of Exploration' },
      { name: 'Vasco da Gama', years: 'fl. 1498', title: 'Explorer' },
      { name: 'Afonso de Albuquerque', years: '1509 – 1515', title: 'Governor of India' },
    ],
    facts: [
      'The first global colonial empire, existing in some form for almost 600 years.',
      'Vasco da Gama’s 1498 voyage opened the first European sea route to India, breaking the overland spice monopoly.',
      'Its last colonial possession, Macau, wasn’t handed over until 1999.',
    ],
  },
  'ptolemaic-egypt': {
    rulers: [
      { name: 'Ptolemy I Soter', years: '305 – 282 BCE', title: 'Pharaoh' },
      { name: 'Cleopatra VII', years: '51 – 30 BCE', title: 'Pharaoh' },
    ],
    facts: [
      'Founded the Library of Alexandria, the largest library of the ancient world.',
      'The ruling dynasty was ethnically Greek/Macedonian — Cleopatra VII was reportedly the first Ptolemy to learn Egyptian.',
      'Ended with Cleopatra’s death in 30 BCE, after which Egypt became a province of Rome.',
    ],
  },
  'qin-dynasty': {
    rulers: [
      { name: 'Qin Shi Huang', years: '221 – 210 BCE', title: 'First Emperor' },
    ],
    facts: [
      'Standardized writing, currency, and even cart-axle widths across a newly unified China.',
      'Began connecting earlier defensive walls into what became the Great Wall of China.',
      'Buried with the Terracotta Army — thousands of life-sized clay soldiers — discovered only in 1974.',
    ],
  },
  'safavid-empire': {
    rulers: [
      { name: 'Ismail I', years: '1501 – 1524', title: 'Shah' },
      { name: 'Abbas the Great', years: '1588 – 1629', title: 'Shah' },
    ],
    facts: [
      'Established Twelver Shia Islam as Iran’s state religion, a legacy that continues today.',
      'Abbas’s capital Isfahan was celebrated in a Persian saying as "half the world" for its beauty.',
      'Fought near-constant wars with the Ottoman Empire over Mesopotamia and the Caucasus.',
    ],
  },
  'sasanian-empire': {
    rulers: [
      { name: 'Ardashir I', years: '224 – 242', title: 'Shahanshah' },
      { name: 'Khosrow I', years: '531 – 579', title: 'Shahanshah' },
    ],
    facts: [
      'Revived Persian imperial traditions after centuries of Parthian rule.',
      'Fought Rome and then Byzantium in a series of wars spanning over 400 years.',
      'Both Sasanian Persia and Byzantium were left exhausted just before the Arab Muslim conquests of the 7th century.',
    ],
  },
  'seleucid-empire': {
    rulers: [
      { name: 'Seleucus I Nicator', years: '305 – 281 BCE', title: 'King' },
      { name: 'Antiochus III "the Great"', years: '222 – 187 BCE', title: 'King' },
    ],
    facts: [
      'At its height stretched from Thrace in Europe to the borders of India.',
      'Founded dozens of Greek-style cities across the Near East, many named Antioch or Seleucia.',
      'Gradually lost territory to a rising Parthia in the east and an expanding Rome in the west.',
    ],
  },
  'shang-dynasty': {
    rulers: [
      { name: 'Wu Ding', years: 'c. 1250 – 1192 BCE', title: 'King' },
    ],
    facts: [
      'The earliest Chinese dynasty confirmed by archaeological and written evidence.',
      'Oracle bone inscriptions from this period are the earliest known form of Chinese writing.',
      'Renowned for elaborate bronze ritual vessels used in ancestor worship.',
    ],
  },
  'song-dynasty': {
    rulers: [
      { name: 'Emperor Taizu', years: '960 – 976', title: 'Emperor' },
      { name: 'Emperor Huizong', years: '1100 – 1126', title: 'Emperor' },
    ],
    facts: [
      'Bi Sheng invented movable-type printing around the 1040s, centuries before Gutenberg.',
      'Developed the world’s first government-issued paper currency.',
      'Gunpowder weapons saw their first documented military use during this period.',
    ],
  },
  'songhai-empire': {
    rulers: [
      { name: 'Sonni Ali', years: '1464 – 1492', title: 'King' },
      { name: 'Askia Muhammad I', years: '1493 – 1528', title: 'King' },
    ],
    facts: [
      'At its height, the largest empire in West African history.',
      'Timbuktu’s Sankore institution was a major center of Islamic scholarship, attracting scholars from across the region.',
      'Collapsed after a 1591 Moroccan invasion that used firearms against traditional Songhai cavalry and infantry.',
    ],
  },
  'spanish-empire': {
    rulers: [
      { name: 'Isabella I & Ferdinand II', years: '1479 – 1516', title: 'Catholic Monarchs' },
      { name: 'Charles V', years: '1516 – 1556', title: 'King' },
      { name: 'Philip II', years: '1556 – 1598', title: 'King' },
    ],
    facts: [
      'At its 16th-century peak it was described as "the empire on which the sun never sets" — a phrase later reused for Britain.',
      'Silver from Potosí, in modern Bolivia, funded Spain’s wars across Europe for over a century.',
      'Lost most of its American colonies to independence movements in the early 19th century.',
    ],
  },
  'timurid-empire': {
    rulers: [
      { name: 'Timur (Tamerlane)', years: '1370 – 1405', title: 'Emir' },
      { name: 'Ulugh Beg', years: '1409 – 1449', title: 'Sultan' },
    ],
    facts: [
      'Timur’s campaigns were extraordinarily destructive — some estimates attribute up to 17 million deaths to his conquests.',
      'His grandson Ulugh Beg built a major astronomical observatory in Samarkand and compiled a star catalog.',
      'Considered an ancestor dynasty of the Mughals — founder Babur was Timur’s direct descendant.',
    ],
  },
  'umayyad-caliphate': {
    rulers: [
      { name: 'Muawiya I', years: '661 – 680', title: 'Caliph' },
      { name: 'Abd al-Malik', years: '685 – 705', title: 'Caliph' },
    ],
    facts: [
      'At its peak, the largest empire the world had yet seen, stretching from Spain to Central Asia.',
      'Abd al-Malik built the Dome of the Rock in Jerusalem in 691, one of Islam’s oldest surviving monuments.',
      'Overthrown by the Abbasid Revolution in 750; one surviving prince fled to found a new emirate in Spain.',
    ],
  },
  'western-roman-empire': {
    rulers: [
      { name: 'Honorius', years: '395 – 423', title: 'Emperor' },
      { name: 'Romulus Augustulus', years: '475 – 476', title: 'Emperor' },
    ],
    facts: [
      'The 395 CE split from the Eastern Empire was meant to be administrative, not permanent.',
      'Sacked by the Visigoths under Alaric in 410 — the first time Rome had fallen to a foreign enemy in nearly 800 years.',
      'Traditionally considered to have ended in 476 CE, when Odoacer deposed the boy-emperor Romulus Augustulus.',
    ],
  },
  'zulu-kingdom': {
    rulers: [
      { name: 'Shaka Zulu', years: '1816 – 1828', title: 'King' },
      { name: 'Cetshwayo', years: '1873 – 1879', title: 'King' },
    ],
    facts: [
      'Shaka revolutionized southern African warfare with the short stabbing spear (iklwa) and new regimental tactics.',
      'Decisively defeated a British invasion force at the Battle of Isandlwana in 1879 — one of the worst defeats of a modern army by a pre-industrial one.',
      'Fell to superior British numbers and firepower later the same year, ending independent Zulu rule.',
    ],
  },
}
