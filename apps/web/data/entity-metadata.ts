export interface Capital {
  name: string
  lon: number
  lat: number
}

export interface EntityMeta {
  peak_year?: number
  peak_label?: string
  capital?: Capital
}

export const ENTITY_META: Record<string, EntityMeta> = {
  'roman-empire':          { peak_year: 117,  peak_label: 'Peak under Trajan — 117 CE',            capital: { name: 'Rome',          lon: 12.49,  lat: 41.89 } },
  'roman-republic':        { peak_year: -100, peak_label: 'Height of Republican expansion',         capital: { name: 'Rome',          lon: 12.49,  lat: 41.89 } },
  'han-dynasty':           { peak_year: -50,  peak_label: 'Peak Western Han period',                capital: { name: "Chang'an",      lon: 108.93, lat: 34.27 } },
  'tang-dynasty':          { peak_year: 730,  peak_label: 'Tang golden age — 8th century',          capital: { name: "Chang'an",      lon: 108.93, lat: 34.27 } },
  'byzantine-empire':      { peak_year: 555,  peak_label: 'Peak under Justinian I',                 capital: { name: 'Constantinople',lon: 28.97,  lat: 41.01 } },
  'abbasid-caliphate':     { peak_year: 850,  peak_label: 'Islamic Golden Age peak',                capital: { name: 'Baghdad',       lon: 44.40,  lat: 33.34 } },
  'mongol-empire':         { peak_year: 1260, peak_label: 'Peak under Kublai Khan',                 capital: { name: 'Karakorum',     lon: 102.83, lat: 47.20 } },
  'ottoman-empire':        { peak_year: 1683, peak_label: 'Peak — gates of Vienna',                 capital: { name: 'Constantinople',lon: 28.97,  lat: 41.01 } },
  'mughal-empire':         { peak_year: 1700, peak_label: 'Peak under Aurangzeb',                   capital: { name: 'Agra',          lon: 78.00,  lat: 27.18 } },
  'mali-empire':           { peak_year: 1337, peak_label: 'Peak under Mansa Musa',                  capital: { name: 'Niani',         lon: -10.50, lat: 11.90 } },
  'achaemenid-persia':     { peak_year: -500, peak_label: 'Peak under Darius I',                    capital: { name: 'Persepolis',    lon: 52.89,  lat: 29.93 } },
  'macedonian-empire':     { peak_year: -323, peak_label: 'Peak under Alexander the Great',         capital: { name: 'Pella',         lon: 22.52,  lat: 40.76 } },
  'qin-dynasty':           { peak_year: -221, peak_label: 'Unification of China',                   capital: { name: 'Xianyang',      lon: 108.68, lat: 34.36 } },
  'maurya-empire':         { peak_year: -250, peak_label: 'Peak under Ashoka',                      capital: { name: 'Pataliputra',   lon: 85.18,  lat: 25.61 } },
  'gupta-empire':          { peak_year: 400,  peak_label: 'Golden age of classical India',          capital: { name: 'Pataliputra',   lon: 85.18,  lat: 25.61 } },
  'umayyad-caliphate':     { peak_year: 720,  peak_label: 'Peak territorial extent',                capital: { name: 'Damascus',      lon: 36.29,  lat: 33.51 } },
  'seleucid-empire':       { peak_year: -280, peak_label: 'Peak under Seleucus I',                  capital: { name: 'Seleucia',      lon: 44.54,  lat: 33.10 } },
  'ptolemaic-egypt':       { peak_year: -250, peak_label: 'Ptolemaic golden age',                   capital: { name: 'Alexandria',    lon: 29.92,  lat: 31.20 } },
  'songhai-empire':        { peak_year: 1500, peak_label: 'Peak under Askia the Great',             capital: { name: 'Gao',           lon: 0.05,   lat: 16.27 } },
  'western-roman-empire':  { peak_year: 100,  peak_label: 'Peak Roman territorial control',         capital: { name: 'Ravenna',       lon: 12.20,  lat: 44.41 } },
  'eastern-roman-empire':  { peak_year: 395,  peak_label: 'Full Eastern Roman extent',              capital: { name: 'Constantinople',lon: 28.97,  lat: 41.01 } },
  'sasanian-empire':       { peak_year: 620,  peak_label: 'Peak under Khosrow II',                  capital: { name: 'Ctesiphon',     lon: 44.58,  lat: 33.09 } },
  'british-empire':        { peak_year: 1920, peak_label: 'Peak — largest empire in history',        capital: { name: 'London',        lon: -0.13,  lat: 51.51 } },
  'united-states':         { peak_year: 1945, peak_label: 'Post-WWII global superpower',             capital: { name: 'Washington, D.C.', lon: -77.04, lat: 38.91 } },
  'qing-dynasty':          { peak_year: 1790, peak_label: "Peak under the Qianlong Emperor",          capital: { name: 'Beijing',       lon: 116.40, lat: 39.90 } },
  'japanese-empire':       { peak_year: 1942, peak_label: 'Peak WWII territorial extent',             capital: { name: 'Tokyo',         lon: 139.69, lat: 35.69 } },
  'russian-empire':        { peak_year: 1895, peak_label: 'Peak territorial extent',                  capital: { name: 'Saint Petersburg', lon: 30.31, lat: 59.94 } },
  'french-empire':         { peak_year: 1920, peak_label: 'Peak — interwar colonial extent',          capital: { name: 'Paris',         lon: 2.35,   lat: 48.86 } },
  'indus-valley-civilization': { peak_year: -2300, peak_label: 'Mature Harappan period',              capital: { name: 'Mohenjo-daro',  lon: 68.14,  lat: 27.33 } },
  'ancient-egypt':         { peak_year: -1279, peak_label: 'New Kingdom under Ramesses II',           capital: { name: 'Thebes',        lon: 32.66,  lat: 25.70 } },
  'akkadian-empire':       { peak_year: -2270, peak_label: 'Peak under Naram-Sin',                    capital: { name: 'Akkad',         lon: 44.10,  lat: 33.06 } },
  'babylonian-empire':     { peak_year: -1750, peak_label: 'Peak under Hammurabi',                    capital: { name: 'Babylon',       lon: 44.42,  lat: 32.54 } },
  'assyrian-empire':       { peak_year: -670,  peak_label: 'Peak under Esarhaddon',                   capital: { name: 'Nineveh',       lon: 43.15,  lat: 36.36 } },
  'shang-dynasty':         { peak_year: -1200, peak_label: 'Late Shang period',                       capital: { name: 'Yin',           lon: 114.30, lat: 36.13 } },
}
