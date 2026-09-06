// Defaults on: the parchment/ornament/audio/discovery polish is the
// intended product experience, not an experiment. Set
// NEXT_PUBLIC_AAA_POLISH=false to opt out (e.g. for a minimal-chrome demo).
// This is only the initial value — store/settings.ts seeds its live,
// user-toggleable `visualPolish` state from it, then persists overrides.
export const AAA_POLISH_DEFAULT = process.env.NEXT_PUBLIC_AAA_POLISH !== 'false'
