/** Liquidglass — opacités, blur, bordures */
export const glass = {
  opacity: {
    strong: 0.92,
    medium: 0.72,
    subtle: 0.45,
    hover: 0.98,
  },
  blur: {
    sm: '12px',
    md: '20px',
    lg: '40px',
    xl: '100px',
  },
  border: {
    subtle: 'rgba(255, 255, 255, 0.1)',
    glow: 'rgba(200, 118, 255, 0.3)',
    active: 'rgba(114, 50, 242, 0.5)',
  },
  gradient: {
    panel: 'linear-gradient(145deg, rgba(114, 50, 242, 0.08) 0%, rgba(6, 11, 25, 0.95) 60%)',
    glow: 'radial-gradient(circle at 50% 0%, rgba(200, 118, 255, 0.15), transparent 70%)',
  },
} as const
