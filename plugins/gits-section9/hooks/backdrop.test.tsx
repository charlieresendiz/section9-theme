import { expect, test } from 'claude-code/testing'

import { SCENE, SCENE_ACTIVE } from './scene.js'

const BACKDROP = {
  plugin: 'gits-section9',
  component: 'Backdrop',
  requestId: 'backdrop',
  props: {
    scene: 'net-city',
    plugin: 'gits-section9',
    glass: { blur: 14, tint: '#041012', opacity: 0.72 },
  },
} as const

const sourceOf = async (ui: { drawn: () => Promise<unknown> }) =>
  // Only the active scene holds the downpour layer.
  JSON.stringify(await ui.drawn()).includes('class=\\"storm\\"') ? 'active' : 'idle'

test('the rain turns to a downpour while a turn runs, then settles', async ($, on) => {
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  on('theme.set', () => ({ value: { isDrawn: true, requestId: 'backdrop' } }))
  on('turn.start', (_, e) => ({ turnId: e.turnId }))
  on('turn.complete', (_, e) => ({ text: e.answer }))

  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })

  for (const surface of ['desktop', 'mobile'] as const) {
    const ui = await $.ui.mount({ ...BACKDROP, surface })
    expect(await sourceOf(ui)).toBe('idle')

    await $.turn.start({ text: 'hi', turnId: 't1' })
    // A subagent's turn inside the main one keeps it stormy until both end.
    await $.turn.start({ text: '', turnId: 't2', agentId: 'a1' })
    expect(await sourceOf(ui)).toBe('active')

    await $.turn.complete({ answer: '', durationMs: 1, isAborted: false, turnId: 't2', agentId: 'a1', reason: 'answer' })
    expect(await sourceOf(ui)).toBe('active')

    await $.turn.complete({ answer: 'ok', durationMs: 1, isAborted: false, turnId: 't1', reason: 'answer' })
    expect(await sourceOf(ui)).toBe('idle')
    await ui.unmount()
  }
  expect(SCENE.includes('class="storm"')).toBe(false)
  expect(SCENE_ACTIVE.includes('class="storm"')).toBe(true)
  expect(SCENE.length).toBeLessThan(131072)
  expect(SCENE_ACTIVE.length).toBeLessThan(131072)
})
