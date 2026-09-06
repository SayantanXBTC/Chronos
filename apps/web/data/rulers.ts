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
}
