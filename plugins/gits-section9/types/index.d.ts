/** How many turns (the main one and any subagents') are running now. */
export type ActiveTurns = number

declare module 'claude-code' {
  interface PluginState {
    'gits-section9': { activeTurns: ActiveTurns }
  }
}
