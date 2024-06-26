import { LinguineList } from './linguine.mjs'
import { translateOne } from './translate.mjs'
import { createInterface } from 'readline'

const main = async () => {
  const readline = createInterface({
    input: process.stdin,
    output: process.stdout,
  })

  const word = await new Promise((resolve) => {
    readline.question('Enter a word: ', (word) => {
      resolve(word)
    })
  })

  readline.close()
  const translatedMap = {}

  for (const language of LinguineList) {
    const translation = await translateOne({
      text: String(word),
      source: 'en',
      target: language,
    })
    translatedMap[language] = translation
  }

  console.log(translatedMap)
}

main().then(() => process.exit(0))
