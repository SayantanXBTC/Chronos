// apps/web/data/stories.ts
// Hand-crafted "journey" narratives for entities whose history deserves more
// than the generic founding/peak/end chapters generateJourneyStory() produces.
import type { CivStory } from '@/store/story'

export const STORIES: CivStory[] = [
  {
    slug: 'roman-empire',
    name: 'Roman Empire',
    color: '#e74c3c',
    chapters: [
      {
        year: -27,
        title: 'Birth of the Empire',
        description: 'Octavian takes the title Augustus, ending a century of civil war and turning the Roman Republic into an empire.',
        focusSlug: 'roman-empire',
      },
      {
        year: 117,
        title: 'Peak Under Trajan',
        description: 'Rome reaches its greatest territorial extent, stretching from Britain to Mesopotamia.',
        focusSlug: 'roman-empire',
      },
      {
        year: 284,
        title: 'The Empire Divided',
        description: "Diocletian splits the empire's administration in two to manage its overwhelming size.",
        focusSlug: 'roman-empire',
      },
      {
        year: 395,
        title: 'East and West Split for Good',
        description: 'On the death of Theodosius I, the empire permanently divides into Western and Eastern halves.',
        focusSlug: 'roman-empire',
      },
    ],
  },
  {
    slug: 'macedonian-empire',
    name: 'Macedonian Empire',
    color: '#3498db',
    chapters: [
      {
        year: -359,
        title: 'Philip II Unites Macedon',
        description: 'Philip II reforms the Macedonian army and brings the fractious Greek city-states under his control.',
        focusSlug: 'macedonian-empire',
      },
      {
        year: -334,
        title: 'Alexander Crosses into Asia',
        description: 'A 22-year-old Alexander the Great leads his army across the Hellespont to challenge the Persian Empire.',
        focusSlug: 'macedonian-empire',
      },
      {
        year: -323,
        title: 'Peak Under Alexander the Great',
        description: "Alexander's conquests stretch from Greece to the Indus Valley, the largest empire the ancient world had seen.",
        focusSlug: 'macedonian-empire',
      },
      {
        year: -301,
        title: 'The Wars of the Successors',
        description: "Alexander's generals carve his empire into rival kingdoms at the Battle of Ipsus.",
        focusSlug: 'macedonian-empire',
      },
    ],
  },
  {
    slug: 'han-dynasty',
    name: 'Han Dynasty',
    color: '#2980b9',
    chapters: [
      {
        year: -206,
        title: 'Liu Bang Founds the Han',
        description: 'After the collapse of the short-lived Qin, Liu Bang establishes the Han Dynasty, setting the template for Chinese imperial rule.',
        focusSlug: 'han-dynasty',
      },
      {
        year: -138,
        title: 'The Silk Road Opens',
        description: 'Emperor Wu sends the envoy Zhang Qian west, opening trade routes that would connect China to Central Asia and beyond.',
        focusSlug: 'han-dynasty',
      },
      {
        year: -50,
        title: 'Peak of Western Han',
        description: "China's population, bureaucracy, and territory reach their height under the Western Han.",
        focusSlug: 'han-dynasty',
      },
      {
        year: 220,
        title: 'Collapse into the Three Kingdoms',
        description: 'Weakened by court intrigue and rebellion, the Han fractures into the warring states of Wei, Shu, and Wu.',
        focusSlug: 'han-dynasty',
      },
    ],
  },
  {
    slug: 'byzantine-empire',
    name: 'Byzantine Empire',
    color: '#6c3483',
    chapters: [
      {
        year: 330,
        title: 'Constantinople Founded',
        description: 'Constantine I dedicates his new capital on the Bosphorus, the seat from which the Eastern Roman Empire would rule for over a thousand years.',
        focusSlug: 'byzantine-empire',
      },
      {
        year: 537,
        title: 'The Hagia Sophia Rises',
        description: "Justinian I completes the Hagia Sophia and reconquers much of the old Western Empire's territory.",
        focusSlug: 'byzantine-empire',
      },
      {
        year: 1054,
        title: 'The Great Schism',
        description: 'The Christian church splits between Rome and Constantinople, a rift that still divides Catholicism and Orthodoxy today.',
        focusSlug: 'byzantine-empire',
      },
      {
        year: 1453,
        title: 'The Fall of Constantinople',
        description: 'Ottoman forces under Mehmed II breach the city walls, ending the last remnant of the Roman Empire after 1,123 years.',
        focusSlug: 'byzantine-empire',
      },
    ],
  },
  {
    slug: 'mongol-empire',
    name: 'Mongol Empire',
    color: '#7d6608',
    chapters: [
      {
        year: 1206,
        title: 'Genghis Khan Unites the Steppe',
        description: 'Temujin is proclaimed Genghis Khan, uniting the Mongol tribes into a single fighting force.',
        focusSlug: 'mongol-empire',
      },
      {
        year: 1227,
        title: 'Death of Genghis Khan',
        description: "The founder dies with his empire already stretching from the Caspian Sea to the Pacific — his sons and grandsons will expand it further.",
        focusSlug: 'mongol-empire',
      },
      {
        year: 1260,
        title: 'Peak Under Kublai Khan',
        description: 'The Mongol Empire reaches its greatest extent, the largest contiguous land empire in history, connecting China to Europe under the Pax Mongolica.',
        focusSlug: 'mongol-empire',
      },
      {
        year: 1368,
        title: 'The Yuan Dynasty Falls',
        description: 'Rebellion drives the Mongols out of China, and the empire fractures permanently into separate khanates.',
        focusSlug: 'mongol-empire',
      },
    ],
  },
  {
    slug: 'ottoman-empire',
    name: 'Ottoman Empire',
    color: '#922b21',
    chapters: [
      {
        year: 1299,
        title: 'Osman I Founds a Beylik',
        description: 'A small Turkish frontier state in Anatolia begins its rise under Osman I, giving the empire its name.',
        focusSlug: 'ottoman-empire',
      },
      {
        year: 1453,
        title: 'Conquest of Constantinople',
        description: 'Mehmed the Conqueror captures the Byzantine capital, ending the Roman Empire and giving the Ottomans a new imperial seat.',
        focusSlug: 'ottoman-empire',
      },
      {
        year: 1683,
        title: 'The Gates of Vienna',
        description: 'Ottoman power crests at the second siege of Vienna — the empire never expands further into Europe after this defeat.',
        focusSlug: 'ottoman-empire',
      },
      {
        year: 1922,
        title: 'The End of an Empire',
        description: 'Defeat in World War I and the rise of Turkish nationalism bring the six-century-old empire to an end.',
        focusSlug: 'ottoman-empire',
      },
    ],
  },
]
