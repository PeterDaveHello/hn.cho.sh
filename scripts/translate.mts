import { TRANSLATE, YOU_MUST_WRITE_IN, ONLY_TRANSLATE_WHAT_IS_GIVEN, BEGIN_IMMEDIATELY } from './default.mjs'
import { log, sanitize } from './util.mjs'
import OpenAI from 'openai'

const openai = new OpenAI({
  organization: process.env.OPENAI_ORG_ID,
  project: process.env.OPENAI_PROJECT_ID,
})

const RETRY_DELAY = 60_000 // 1 minute

export async function retryTranslation(func, args, maxRetries) {
  let tryCount = 0
  while (tryCount < maxRetries) {
    try {
      return await func({
        text: args?.payload,
        source: args?.source,
        target: args?.locale,
      })
    } catch (e) {
      log(`🤔 Retrying\t${args?.locale} ${e}`, 'error')
      await new Promise((r) => setTimeout(r, RETRY_DELAY))
      tryCount++
    }
  }
  log(`🤬 Failed\t${args?.locale}`, 'error')
  throw new Error('Failed to translate')
}

export const translateOne = async ({
  text,
  source,
  target,
}: {
  text: string
  source: string
  target: string
}): Promise<string> => {
  const completion = await openai.chat.completions.create({
    messages: [
      {
        role: 'system',
        content:
          TRANSLATE[target] +
          '\n\n' +
          ONLY_TRANSLATE_WHAT_IS_GIVEN[source] +
          '\n\n' +
          YOU_MUST_WRITE_IN[target] +
          '\n\n' +
          BEGIN_IMMEDIATELY[target] +
          '\n\n',
      },
      { role: 'user', content: `TEXT:\n${text}` },
    ],
    model: 'gpt-4o',
    temperature: 0,
  })

  let { content } = completion.choices[0].message

  if (content.includes('RESULT:')) {
    content = content.split('RESULT:')[1].trim()
  }

  if (content.includes('RESULTAAT:')) {
    content = content.split('RESULTAAT:')[1].trim()
  }

  content = sanitize(content)

  return content
}

export const translate = async ({
  text,
  source,
  target,
}: {
  text: string[]
  source: string
  target: string
}): Promise<string[]> => {
  if (source === target) {
    return text
  }

  if (text.length === 0) {
    return []
  }

  const translatedPromises = text.map((t) => translateOne({ text: t, source, target }))

  const translatedTexts = await Promise.all(translatedPromises)

  return translatedTexts
}
