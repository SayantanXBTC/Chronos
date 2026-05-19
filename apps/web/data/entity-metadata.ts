export interface EntityMeta {
  peak_year?: number
  peak_label?: string
}

export const ENTITY_META: Record<string, EntityMeta> = {
  'roman-empire':        { peak_year: 117,  peak_label: 'Peak under Trajan — 117 CE' },
  'roman-republic':      { peak_year: -100, peak_label: 'Height of Republican expansion' },
  'han-dynasty':         { peak_year: -50,  peak_label: 'Peak Western Han period' },
  'tang-dynasty':        { peak_year: 730,  peak_label: 'Tang golden age — 8th century' },
  'byzantine-empire':    { peak_year: 555,  peak_label: 'Peak under Justinian I' },
  'abbasid-caliphate':   { peak_year: 850,  peak_label: 'Islamic Golden Age peak' },
  'mongol-empire':       { peak_year: 1260, peak_label: 'Peak under Kublai Khan' },
  'ottoman-empire':      { peak_year: 1683, peak_label: 'Peak — gates of Vienna' },
  'mughal-empire':       { peak_year: 1700, peak_label: 'Peak under Aurangzeb' },
  'mali-empire':         { peak_year: 1337, peak_label: 'Peak under Mansa Musa' },
  'achaemenid-persia':   { peak_year: -500, peak_label: 'Peak under Darius I' },
  'macedonian-empire':   { peak_year: -323, peak_label: 'Peak under Alexander the Great' },
  'qin-dynasty':         { peak_year: -221, peak_label: 'Unification of China' },
  'maurya-empire':       { peak_year: -250, peak_label: 'Peak under Ashoka' },
  'gupta-empire':        { peak_year: 400,  peak_label: 'Golden age of classical India' },
  'umayyad-caliphate':   { peak_year: 720,  peak_label: 'Peak territorial extent' },
  'seleucid-empire':     { peak_year: -280, peak_label: 'Peak under Seleucus I' },
  'ptolemaic-egypt':     { peak_year: -250, peak_label: 'Ptolemaic golden age' },
  'songhai-empire':      { peak_year: 1500, peak_label: 'Peak under Askia the Great' },
  'western-roman-empire': { peak_year: 100, peak_label: 'Peak Roman territorial control' },
  'eastern-roman-empire': { peak_year: 395, peak_label: 'Full Eastern Roman extent' },
  'sasanian-empire':     { peak_year: 620,  peak_label: 'Peak under Khosrow II' },
}
