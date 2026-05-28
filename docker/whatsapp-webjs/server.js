import express from 'express'
import helmet from 'helmet'
import rateLimit from 'express-rate-limit'
import qrcode from 'qrcode'
import qrcodeTerminal from 'qrcode-terminal'
import pkg from 'whatsapp-web.js'
import fs from 'fs'
import path from 'path'

const { Client, LocalAuth, MessageMedia } = pkg

const port = Number(process.env.PORT || 3020)
const apiToken = process.env.API_TOKEN || ''
const allowNoToken = process.env.ALLOW_NO_TOKEN === 'true'
const sessionDir = process.env.SESSION_DIR || '/data/session'
const dailyLimit = Number(process.env.MESSAGE_DAILY_LIMIT || 200)
const rateLimitPerMinute = Number(process.env.RATE_LIMIT_PER_MINUTE || 20)

const app = express()
app.use(helmet({ contentSecurityPolicy: false }))
app.use(express.json({ limit: '512kb' }))
app.use(rateLimit({ windowMs: 60 * 1000, limit: rateLimitPerMinute }))

let lastQr = ''
let lastQrDataUrl = ''
let ready = false
let sendCountDay = new Date().toISOString().slice(0, 10)
let sendCount = 0

function requireToken(req, res, next) {
  if (!apiToken && allowNoToken) return next()
  const bearer = String(req.headers.authorization || '').replace(/^Bearer\s+/i, '')
  const headerToken = req.headers['x-api-key']
  if (apiToken && (bearer === apiToken || headerToken === apiToken)) return next()
  return res.status(401).json({ error: 'Unauthorized' })
}

function normalizePhone(value) {
  const phone = String(value || '').replace(/[\s().-]/g, '').replace(/^00/, '+')
  if (!/^\+?\d{10,15}$/.test(phone)) {
    const error = new Error('Recipient must be one personal phone number with 10-15 digits.')
    error.statusCode = 400
    throw error
  }
  return phone.replace(/^\+/, '')
}

function assertDailyLimit() {
  const today = new Date().toISOString().slice(0, 10)
  if (today !== sendCountDay) {
    sendCountDay = today
    sendCount = 0
  }
  sendCount += 1
  if (sendCount > dailyLimit) {
    const error = new Error('Daily WhatsApp send limit reached.')
    error.statusCode = 429
    throw error
  }
}

const client = new Client({
  authStrategy: new LocalAuth({ dataPath: sessionDir }),
  puppeteer: {
    headless: process.env.PUPPETEER_HEADLESS !== 'false',
    executablePath: process.env.PUPPETEER_EXECUTABLE_PATH || undefined,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
  },
})

client.on('qr', async (qr) => {
  ready = false
  lastQr = qr
  lastQrDataUrl = await qrcode.toDataURL(qr)
  qrcodeTerminal.generate(qr, { small: true })
  console.log('WhatsApp QR refreshed. Open /qr and scan with the demo phone.')
})

client.on('ready', () => {
  ready = true
  lastQr = ''
  lastQrDataUrl = ''
  console.log('WhatsAppWebJS client is ready.')
})

client.on('disconnected', (reason) => {
  ready = false
  console.log(`WhatsAppWebJS disconnected: ${reason}`)
})

client.on('change_state', (state) => {
  console.log(`WhatsApp client state changed: ${state}`)
})

client.on('loading_screen', (percent, message) => {
  console.log(`WhatsApp loading screen: ${percent}% - ${message}`)
})

client.on('auth_failure', (msg) => {
  console.error(`WhatsApp auth failure: ${msg}`)
})

async function postWebhook(url, payload, headers) {
  if (typeof fetch === 'function') {
    try {
      const res = await fetch(url, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload)
      });
      if (!res.ok) {
        console.error(`Webhook failed with status ${res.status}: ${await res.text()}`);
      } else {
        console.log(`Webhook forwarded successfully`);
      }
      return;
    } catch (e) {
      console.error(`Webhook fetch failed: ${e.message}`);
    }
  }

  try {
    const httpOrHttps = url.startsWith('https') ? await import('https') : await import('http');
    const parsedUrl = new URL(url);
    const options = {
      hostname: parsedUrl.hostname,
      port: parsedUrl.port || (url.startsWith('https') ? 443 : 80),
      path: parsedUrl.pathname + parsedUrl.search,
      method: 'POST',
      headers: {
        ...headers,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(JSON.stringify(payload))
      }
    };

    const req = httpOrHttps.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          console.log(`Webhook forwarded successfully (fallback)`);
        } else {
          console.error(`Webhook failed with status ${res.statusCode}: ${data}`);
        }
      });
    });
    req.on('error', (e) => console.error(`Webhook fallback failed: ${e.message}`));
    req.write(JSON.stringify(payload));
    req.end();
  } catch (err) {
    console.error(`Webhook import/fallback failed: ${err.message}`);
  }
}

function getPhone(remoteJid) {
  if (!remoteJid || typeof remoteJid !== 'string') return ''
  return remoteJid.split('@')[0]
}

// Incoming message from WhatsApp WebJS v1.34.x — both events for coverage
const ALLOWED_SENDERS = process.env.ALLOWED_SENDERS
  ? process.env.ALLOWED_SENDERS.split(',').map(s => s.trim())
  : null

// LID → phone mapping built from outgoing messages (since getContact().number returns LID, not phone)
const lidToPhone = new Map()

function getLid(id) {
  if (!id || typeof id !== 'string') return ''
  const parts = id.split('@')
  const suffix = parts[1] || ''
  if (suffix.startsWith('lid')) return parts[0]
  if (suffix === 'lid') return parts[0]
  return ''
}

async function handleIncomingMessage(msg) {
  try {
    const isFromMe = msg.fromMe
    const fromRemote = String(msg.from || '')
    const fromSuffix = fromRemote.split('@')[1] || ''
    const toRemote = String(msg.to || '')
    const body = (msg.body || '(empty)').slice(0, 80)
    const idRemote = msg.id?.remote || ''
    const idSerialized = msg.id?._serialized || ''
    console.log(`WA event - fromMe:${isFromMe} from:${fromRemote} to:${toRemote} idRemote:${idRemote} id:${idSerialized} suffix:@${fromSuffix} body:${body}`)

    // For outgoing messages, capture the recipient's @lid → phone mapping
    if (isFromMe) {
      const toSuffix = toRemote.split('@')[1] || ''
      if (toSuffix.startsWith('lid')) {
        const lid = toRemote.split('@')[0]
        // Try to get the original phone from idRemote or to field
        // When we sent to a @c.us contact, WhatsApp converts to @lid
        // but the phone number is already known from the send endpoint
        if (!lidToPhone.has(lid)) {
          // If not yet mapped, try msg.getChat() which may have the @c.us form
          try {
            const chat = await msg.getChat()
            const chatId = chat?.id?._serialized || ''
            const chatSuffix = chatId.split('@')[1] || ''
            if (chatSuffix === 'c.us') {
              const phone = chatId.split('@')[0]
              lidToPhone.set(lid, phone)
              console.log(`Mapped @lid ${lid} → ${phone} (from outgoing chat)`)
            }
          } catch {}
        }
      }
      return
    }

    // Only forward personal chats (@c.us, @s.whatsapp.net, @lid)
    // Reject groups (@g.us), broadcasts (@broadcast), newsletters (@newsletter), etc.
    const isPersonal = fromSuffix === 'c.us' || fromSuffix === 's.whatsapp.net' || fromSuffix === 'lid'
    if (!isPersonal) {
      console.log(`Ignored non-personal message (type: @${fromSuffix}): ${(msg.body || '(empty)').slice(0, 80)}`)
      return
    }

    let fromPhone = getPhone(fromRemote)
    const toPhone = getPhone(msg.to)

    if (!fromPhone) {
      console.log('Ignored incoming message without a valid sender:', msg.id?.id || msg.id?._serialized || 'no-id')
      return
    }

    // For @lid users, try to resolve phone number so ALLOWED_SENDERS can match
    if (fromSuffix === 'lid') {
      // First check the mapping cache built from outgoing messages
      if (lidToPhone.has(fromPhone)) {
        fromPhone = lidToPhone.get(fromPhone)
        console.log(`Resolved @lid using senders cache: ${msg.id?._serialized} → ${fromPhone}`)
      } else {
        // Fallback: try getContact() which may or may not return the real phone
        try {
          const contact = await msg.getContact()
          if (contact && contact.number) {
            const contactPhone = String(contact.number).replace(/[^0-9]/g, '')
            if (contactPhone && contactPhone !== fromPhone) {
              console.log(`Resolved @lid ${fromPhone} to phone ${contactPhone}`)
              fromPhone = contactPhone
            }
          }
        } catch (e) {
          console.log(`Could not resolve @lid contact ${fromPhone}: ${e.message}`)
        }
      }
    }

    let isAllowed = ALLOWED_SENDERS && ALLOWED_SENDERS.includes(fromPhone)

    if (!isAllowed) {
      try {
        const frappeUrl = process.env.FRAPPE_URL || 'http://host.docker.internal:8000'
        const authUrl = `${frappeUrl.replace(/\/$/, '')}/api/method/crm.api.omnichannel.is_valid_whatsapp_sender`
        
        const headers = { 'Content-Type': 'application/json' }
        if (apiToken) {
          headers['X-Webhook-Token'] = apiToken
        }
        
        let allowedFromFrappe = false
        if (typeof fetch === 'function') {
          const res = await fetch(authUrl, {
            method: 'POST',
            headers,
            body: JSON.stringify({ sender: fromPhone })
          })
          if (res.ok) {
            const data = await res.json()
            allowedFromFrappe = Boolean(data.message)
          }
        } else {
          // Fallback node http request
          allowedFromFrappe = await new Promise((resolve) => {
            try {
              const httpOrHttps = authUrl.startsWith('https') ? import('https') : import('http')
              Promise.resolve(httpOrHttps).then((mod) => {
                const parsedUrl = new URL(authUrl)
                const options = {
                  hostname: parsedUrl.hostname,
                  port: parsedUrl.port || (authUrl.startsWith('https') ? 443 : 80),
                  path: parsedUrl.pathname + parsedUrl.search,
                  method: 'POST',
                  headers: {
                    ...headers,
                    'Content-Length': Buffer.byteLength(JSON.stringify({ sender: fromPhone }))
                  }
                }
                const req = mod.request(options, (res) => {
                  let resData = ''
                  res.on('data', (chunk) => resData += chunk)
                  res.on('end', () => {
                    if (res.statusCode >= 200 && res.statusCode < 300) {
                      try {
                        const parsed = JSON.parse(resData)
                        resolve(Boolean(parsed.message))
                      } catch { resolve(false) }
                    } else { resolve(false) }
                  })
                })
                req.on('error', () => resolve(false))
                req.write(JSON.stringify({ sender: fromPhone }))
                req.end()
              })
            } catch { resolve(false) }
          })
        }
        
        if (allowedFromFrappe) {
          isAllowed = true
          console.log(`Dynamically authorized sender ${fromPhone} via Frappe check`)
        }
      } catch (err) {
        console.error(`Error querying dynamic sender authorization: ${err.message}`)
      }
    }

    if (!isAllowed) {
      console.log(`Ignored message from non-allowlisted sender: ${fromPhone}`)
      return
    }

    console.log(`Received WhatsApp message from ${fromPhone}: ${(msg.body || '(empty)').slice(0, 200)}`)

    const frappeUrl = process.env.FRAPPE_URL || 'http://host.docker.internal:8000'
    const url = `${frappeUrl.replace(/\/$/, '')}/api/method/crm.api.omnichannel.upsert_inbound_message`

    const payload = {
      channel: 'WhatsApp',
      content: msg.body || '',
      provider_message_id: msg.id?.id || msg.id?._serialized || msg.id?.toString() || `wa:${Date.now()}:${fromPhone}`,
      sender: fromPhone,
      recipient: toPhone,
      message_type: 'Text',
      status: 'Received',
      payload: {
        provider_conversation_id: fromPhone
      }
    }

    const headers = {
      'Content-Type': 'application/json'
    }
    if (apiToken) {
      headers['X-Webhook-Token'] = apiToken
    }

    await postWebhook(url, payload, headers)
  } catch (error) {
    console.error(`Error forwarding incoming message: ${error.message}`)
  }
}

// message_create fires for ALL messages (incoming + outgoing)
client.on('message_create', async (msg) => {
  console.log(`message_create fired, id=${msg.id?._serialized || msg.id?.id || 'no-id'}`)
  await handleIncomingMessage(msg)
})

// message fires only for received messages (backup in case message_create doesn't fire)
client.on('message', async (msg) => {
  console.log(`message fired, id=${msg.id?._serialized || msg.id?.id || 'no-id'}`)
  await handleIncomingMessage(msg)
})


app.get('/health', (_req, res) => {
  res.json({ ok: true, ready })
})

app.get('/status', requireToken, async (_req, res) => {
  let state = 'unknown'
  try {
    if (typeof client.getState === 'function') state = await client.getState()
  } catch (e) { state = e.message }
  res.json({ ready, state, has_qr: Boolean(lastQr), send_count_day: sendCountDay, send_count: sendCount })
})

app.get('/qr', requireToken, (_req, res) => {
  if (!lastQrDataUrl) return res.status(404).send('QR is not available. Check /status or restart the service.')
  res.type('html').send(`<html><body><img src="${lastQrDataUrl}" alt="WhatsApp QR" /></body></html>`)
})

app.post('/send', requireToken, async (req, res) => {
  try {
    if (!ready) return res.status(503).json({ error: 'WhatsApp client is not ready. Scan QR first.' })
    assertDailyLimit()
    const phone = normalizePhone(req.body.to || req.body.phone || req.body.number)
    const chatId = `${phone}@c.us`
    const text = String(req.body.message || req.body.text || '').slice(0, 4096)
    const mediaUrl = req.body.attachment || req.body.mediaUrl || req.body.fileUrl
    if (!text && !mediaUrl) return res.status(400).json({ error: 'message or attachment is required' })
    let sent
    if (mediaUrl) {
      const media = await MessageMedia.fromUrl(mediaUrl, { unsafeMime: false })
      sent = await client.sendMessage(chatId, media, { caption: text || undefined, linkPreview: false })
    } else {
      sent = await client.sendMessage(chatId, text, { linkPreview: false })
    }
    // Eagerly store @lid → phone mapping from the sent message
    const sentTo = String(sent.to || '')
    const sentLid = getLid(sentTo)
    if (sentLid && !lidToPhone.has(sentLid)) {
      lidToPhone.set(sentLid, phone)
      console.log(`Mapped @lid ${sentLid} → ${phone} (from /send)`);
    }
    res.json({ id: sent.id?._serialized || sent.id?.id, messageId: sent.id?._serialized || sent.id?.id, status: 'sent' })
  } catch (error) {
    res.status(error.statusCode || 500).json({ error: error.message || 'Send failed' })
  }
})

// Clean up stale Chromium lock files left by previous container runs
function cleanSingletonLocks(dir) {
  if (!fs.existsSync(dir)) return
  try {
    const entries = fs.readdirSync(dir, { withFileTypes: true })
    for (const entry of entries) {
      const full = path.join(dir, entry.name)
      if (entry.isDirectory()) {
        cleanSingletonLocks(full)
      } else if (entry.name === 'SingletonLock' || entry.name === 'SingletonCookie' || entry.name === 'SingletonSocket') {
        fs.unlinkSync(full)
        console.log(`Removed stale lock: ${full}`)
      }
    }
  } catch (e) {
    console.warn(`Lock cleanup warning: ${e.message}`)
  }
}

cleanSingletonLocks(sessionDir)

process.on('unhandledRejection', (reason, promise) => {
  console.error('UNHANDLED REJECTION:', reason)
})

client.on('authenticated', () => {
  console.log('WA auth callback fired')
})

client.initialize()

// Workaround for whatsapp-web.js 1.34.x race condition:
// change:hasSynced can fire before the listener is registered inside inject(),
// or the onAppStateHasSyncedEvent callback may throw after setting client.info
// but before emitting 'ready'. Detect these and force-ready the client.
;(async function ensureReady() {
  for (let i = 0; i < 60; i++) {
    await new Promise(r => setTimeout(r, 1000))
    if (ready) return
    if (!client.pupPage) {
      if (i < 5) console.log(`ensureReady[${i}]: pupPage null, waiting...`)
      continue
    }
    try {
      const state = await client.getState()
      if (i < 5) console.log(`ensureReady[${i}]: state=${state} info=${!!client.info}`)
      if (state !== 'CONNECTED') continue

      // If the callback ran (info set) but ready is still false, force it
      if (client.info) {
        ready = true
        lastQr = ''
        lastQrDataUrl = ''
        console.log('WhatsAppWebJS client is ready (forced after callback set info).')
        return
      }

      // Otherwise try to trigger the callback manually
      const ret = await client.pupPage.evaluate(() => {
        const Socket = window.require('WAWebSocketModel').Socket
        const hasFn = typeof window.onAppStateHasSyncedEvent === 'function'
        return { sockState: Socket.state, hasFn }
      })
      if (ret && ret.hasFn) {
        await client.pupPage.evaluate(() => {
          window.onAppStateHasSyncedEvent()
        })
        console.log('Manually triggered onAppStateHasSyncedEvent (race condition workaround)')
        return
      }
    } catch {}
  }
  console.log('ensureReady: giving up after 60s (QR re-scan may be needed)')
})()

app.listen(port, '0.0.0.0', () => {
  console.log(`Summon WhatsAppWebJS adapter listening on ${port}`)
})
