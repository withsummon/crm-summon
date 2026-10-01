/* global AudioWorkletProcessor, registerProcessor, sampleRate */

class CommitteePcmCapture extends AudioWorkletProcessor {
  constructor() {
    super()
    this.pending = []
    this.cursor = 0
  }

  process(inputs) {
    const channel = inputs[0]?.[0]
    if (!channel?.length) return true
    const ratio = sampleRate / 16000
    while (this.cursor < channel.length) {
      const sample = Math.max(-1, Math.min(1, channel[Math.floor(this.cursor)]))
      this.pending.push(sample < 0 ? sample * 32768 : sample * 32767)
      this.cursor += ratio
      if (this.pending.length === 1600) {
        const frame = Int16Array.from(this.pending)
        this.pending.length = 0
        this.port.postMessage(frame.buffer, [frame.buffer])
      }
    }
    this.cursor -= channel.length
    return true
  }
}

registerProcessor('committee-pcm-capture', CommitteePcmCapture)
