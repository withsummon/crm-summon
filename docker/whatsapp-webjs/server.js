import express from 'express'
import helmet from 'helmet'
import rateLimit from 'express-rate-limit'
import qrcode from 'qrcode'
import qrcodeTerminal from 'qrcode-terminal'
import pkg from 'whatsapp-web.js'

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

app.get('/health', (_req, res) => {
  res.json({ ok: true, ready })
})

app.get('/status', requireToken, (_req, res) => {
  res.json({ ready, has_qr: Boolean(lastQr), send_count_day: sendCountDay, send_count: sendCount })
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
    res.json({ id: sent.id?._serialized || sent.id?.id, messageId: sent.id?._serialized || sent.id?.id, status: 'sent' })
  } catch (error) {
    res.status(error.statusCode || 500).json({ error: error.message || 'Send failed' })
  }
})

client.initialize()
app.listen(port, '0.0.0.0', () => {
  console.log(`Summon WhatsAppWebJS adapter listening on ${port}`)
})
