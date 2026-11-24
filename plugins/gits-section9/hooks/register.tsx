import { atom, read, update } from 'claude-code'
import type { Register, ThemeSetArgs, ThemeMessageRule } from 'claude-code'

import { makeColors } from './make-colors.js'
import { SCENE, SCENE_ACTIVE } from './scene.js'

// Turns running now. Above zero, the backdrop shows the downpour scene.
const activeTurns = atom({ plugin: 'gits-section9', key: 'activeTurns' } as const, 0)

// Section 9 // Net Dive: phosphor teal on wet night glass. Dark only.
const { theme, problems } = makeColors({
  label: 'Section 9 // Net Dive',
  only: 'dark',
  roles: {
    accent: '#2ee6b6', // phosphor teal
    danger: '#ff5470', // warning-light red
    success: '#7be38a', // terminal green
    warning: '#e8b54a', // sodium streetlamp amber
    pro: '#8f86ff', // cyberbrain violet
  },
  dark: {
    gray: {
      anchors: {
        'surface-0': '#050b0d',
        'surface-1': '#0a1517',
        'surface-2': '#0e1c1f',
        'surface-3': '#132427',
        'text-primary': '#d8f6ee',
        'text-secondary': '#a3d4c6',
        'text-muted': '#7eab9f',
      },
    },
    git: { added: '#3ddc97', removed: '#ff5470', modified: '#e8b54a', merged: '#8f86ff' },
  },
})

// A clipped-corner HUD frame: notched top-left and bottom-right, a tick on the edge.
const hudFrame = (body: `#${string}`, edge: `#${string}`): ThemeMessageRule['fill'] => ({
  vector: {
    viewBox: 96,
    slice: 20,
    paths: [
      { d: 'M12 0H96V84L84 96H0V12Z', color: body },
      { d: 'M12 0H96V84L84 96H0V12Z M13 1.5L1.5 13V94.5H83.4L94.5 83.4V1.5Z', color: edge },
      { d: 'M0 12L12 0H30V3H13.2L3 13.2V30H0Z', color: edge },
    ],
  },
})

const LOOK: ThemeSetArgs = {
  colors: theme,
  overrideColorScheme: 'dark',
  backdrop: { scene: 'net-city', glass: { blur: 14, tint: '#041012', opacity: 0.72 } },
}

const STYLE: ThemeSetArgs['style'] = {
  Text: { fontFamily: ['mono'], fontSize: 14, lineHeight: 22, letterSpacing: 0.2 },
  Heading: { fontFamily: ['mono'], color: '#5ff5cc', fontWeight: 'semibold', letterSpacing: 1.5 },
  UserMessage: {
    color: '#d8f6ee',
    backgroundColor: '#0c2125',
    fill: hudFrame('#0c2125', '#2ee6b6'),
    padding: 14,
    shadow: { x: 0, y: 0, blur: 14, color: '#2ee6b633' },
  },
  AssistantMessage: {
    color: '#d8f6ee',
    backgroundColor: '#071214',
    radius: 2,
    borderColor: '#1a3a3c',
    borderWidth: 1,
    paddingX: 16,
    paddingY: 12,
  },
  ToolUse: {
    color: '#9fe8d4',
    fontFamily: ['code'],
    backgroundColor: '#081517',
    borderColor: '#1f4a48',
    borderWidth: 1,
    radius: 0,
    paddingX: 8,
  },
}

// Low city hum, rain on glass, a far choral-ish pad. Quiet: it plays for hours.
const SOUND: ThemeSetArgs['sound'] = {
  ambience: {
    reverb: 0.5,
    layers: [
      { wave: 'brown', drone: true, gain: 0.22, filter: { type: 'lowpass', hz: 260 } },
      { wave: 'pink', drone: true, gain: 0.08, filter: { type: 'bandpass', hz: 2400, to: 3600 } },
      { wave: 'crackle', scatter: 3, gain: 0.05, filter: { type: 'highpass', hz: 3000 } },
      { wave: 'sine', drone: true, notes: ['A1', 'E2'], gain: 0.12, tremolo: { hz: 0.08, depth: 0.4 } },
      { wave: 'triangle', drone: true, notes: ['A3', 'C4', 'E4'], gain: 0.05, filter: { type: 'lowpass', hz: 700, to: 1100 }, tremolo: { hz: 0.05, depth: 0.6 } },
      { wave: 'bell', scatter: 0.06, notes: ['A5', 'C6', 'E6', 'G5'], gain: 0.06, release: 2.5 },
    ],
  },
  cues: {
    send: { layers: [{ wave: 'sine', notes: ['E5', 'A5'], step: 0.06, gain: 0.25, release: 0.25 }] },
    tool: { layers: [{ wave: 'sine', notes: ['A6'], gain: 0.08, release: 0.06 }] },
    done: { reverb: 0.4, layers: [{ wave: 'bell', notes: ['A4', 'E5', 'C6'], step: 0.12, gain: 0.25, release: 1.2 }] },
    ask: { layers: [{ wave: 'triangle', notes: ['E5', 'E5'], step: 0.18, gain: 0.2, release: 0.2 }] },
    error: { layers: [{ wave: 'saw', notes: ['A2'], glide: -5, gain: 0.15, release: 0.5, filter: { type: 'lowpass', hz: 600 } }] },
    compact: { layers: [{ wave: 'pink', gain: 0.12, attack: 0.3, release: 0.8, filter: { type: 'bandpass', hz: 1200, to: 300 } }] },
    click: { layers: [{ wave: 'bell', notes: ['A4', 'C5', 'E5', 'G5', 'A5', 'C6'], gain: 0.15, release: 0.8 }] },
  },
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const unpainted = problems.find(line => line.startsWith("Desktop won't paint"))
    if (unpainted !== undefined) {
      $.ui.toast(unpainted)
    }

    let set
    try {
      set = await $.theme.set({ ...LOOK, style: STYLE, sound: SOUND })
    } catch (error) {
      // Older builds refuse style or sound: fall back to colors and scene alone.
      $.ui.log(String(error))
      set = await $.theme.set(LOOK)
    }

    if (!set.isDrawn) {
      $.ui.status(set.reason)
    }
    // A fresh session (or a reload) starts calm.
    await update($, activeTurns, () => 0)
    return next(e)
  })

  // While any turn runs, the rain turns to a downpour.
  on('turn.start', async ($, e, next) => {
    await update($, activeTurns, n => n + 1)
    return next(e)
  })

  on('turn.complete', async ($, e, next) => {
    await update($, activeTurns, n => Math.max(0, n - 1))
    return next(e)
  })

  on('ui.render', { component: 'Backdrop' }, async ($, e, next) => {
    if (e.surface !== 'desktop' && e.surface !== 'mobile') {
      return next(e)
    }
    const { Svg } = $.ui.resolve(e)
    if ((await read($, activeTurns)) > 0) {
      return <Svg source={SCENE_ACTIVE} alt="The net city in a downpour of bright green code while Claude works" isInteractive />
    }
    return <Svg source={SCENE} alt="A rain-soaked net city at night, green code falling past a rotating HUD reticle" isInteractive />
  })
}
