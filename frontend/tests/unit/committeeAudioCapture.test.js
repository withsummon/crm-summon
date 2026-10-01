import { hasLiveAudio, pcmFrameToBase64, startMeetingAudioCapture } from '@/lib/committeeAudioCapture'

it('requires an enabled live tab audio track', () => {
  expect(hasLiveAudio({ getAudioTracks: () => [{ enabled: true, readyState: 'live' }] })).toBe(true)
  expect(hasLiveAudio({ getAudioTracks: () => [{ enabled: false, readyState: 'live' }] })).toBe(false)
  expect(hasLiveAudio({ getAudioTracks: () => [] })).toBe(false)
})

it('encodes PCM bytes without changing their order', () => {
  expect(pcmFrameToBase64(new Uint8Array([0, 128, 255]).buffer)).toBe('AID/')
})

it('rejects a shared tab without audio and releases its tracks', async () => {
  const stop = vi.fn()
  vi.stubGlobal('AudioWorkletNode', class {})
  vi.stubGlobal('navigator', {
    mediaDevices: {
      getDisplayMedia: vi.fn().mockResolvedValue({ getAudioTracks: () => [], getTracks: () => [{ stop }] }),
      getUserMedia: vi.fn(),
    },
  })
  try {
    await expect(startMeetingAudioCapture({ onFrame: vi.fn(), onEnded: vi.fn() })).rejects.toThrow('Bagikan audio tab')
    expect(stop).toHaveBeenCalledOnce()
  } finally {
    vi.unstubAllGlobals()
  }
})
