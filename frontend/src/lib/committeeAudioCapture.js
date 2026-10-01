export function hasLiveAudio(stream) {
  return stream.getAudioTracks().some((track) => track.enabled && track.readyState === 'live')
}

export function pcmFrameToBase64(buffer) {
  return btoa(String.fromCharCode(...new Uint8Array(buffer)))
}

export async function startMeetingAudioCapture({ onFrame, onEnded }) {
  if (!navigator.mediaDevices?.getDisplayMedia || !navigator.mediaDevices?.getUserMedia || !window.AudioWorkletNode) {
    throw new Error('Gunakan browser yang mendukung berbagi audio tab dan mikrofon.')
  }

  const streams = []
  let context
  try {
    const meeting = await navigator.mediaDevices.getDisplayMedia({ video: true, audio: true })
    streams.push(meeting)
    if (!hasLiveAudio(meeting)) {
      throw new Error('Pilih tab Zoom atau Google Meet lalu aktifkan “Bagikan audio tab”.')
    }

    let microphone = null
    try {
      microphone = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true } })
      streams.push(microphone)
    } catch {
      // Meeting audio can still be transcribed when microphone permission is unavailable.
    }

    context = new AudioContext({ latencyHint: 'interactive' })
    await context.audioWorklet.addModule(new URL('../worklets/committee-pcm-capture.js', import.meta.url))
    const silence = context.createGain()
    silence.gain.value = 0
    silence.connect(context.destination)

    for (const [source, stream] of [['meeting', meeting], ['mic', microphone]]) {
      if (!stream) continue
      const input = context.createMediaStreamSource(stream)
      const processor = new AudioWorkletNode(context, 'committee-pcm-capture')
      processor.port.onmessage = (event) => onFrame(source, event.data)
      input.connect(processor).connect(silence)
    }
    meeting.getVideoTracks()[0]?.addEventListener('ended', onEnded, { once: true })
    await context.resume()

    return {
      microphoneAvailable: !!microphone,
      setMicrophoneEnabled(enabled) {
        microphone?.getAudioTracks().forEach((track) => { track.enabled = enabled })
      },
      async stop() {
        streams.forEach((stream) => stream.getTracks().forEach((track) => track.stop()))
        await context.close()
      },
    }
  } catch (error) {
    streams.forEach((stream) => stream.getTracks().forEach((track) => track.stop()))
    await context?.close()
    if (error?.name === 'NotAllowedError') throw new Error('Izin berbagi tab atau mikrofon ditolak.')
    throw error
  }
}
