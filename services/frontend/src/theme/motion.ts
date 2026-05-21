/** Timings & courbes d'animation */
export const motion = {
  duration: {
    instant: '120ms',
    fast: '250ms',
    normal: '400ms',
    slow: '600ms',
    cinematic: '1200ms',
  },
  easing: {
    standard: 'cubic-bezier(0.4, 0, 0.2, 1)',
    enter: 'cubic-bezier(0, 0, 0.2, 1)',
    exit: 'cubic-bezier(0.4, 0, 1, 1)',
    spring: 'cubic-bezier(0.34, 1.56, 0.64, 1)',
  },
  stagger: {
    logo: '0.05s',
    card: '0.08s',
  },
} as const
