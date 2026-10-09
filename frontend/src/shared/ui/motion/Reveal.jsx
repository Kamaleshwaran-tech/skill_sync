import { motion, useReducedMotion } from 'framer-motion'

const viewport = { amount: 0.2, once: true }

export function Reveal({ children, delay = 0, direction = 'up' }) {
  const prefersReducedMotion = useReducedMotion()
  const offset = direction === 'left' ? 24 : direction === 'right' ? -24 : 18
  const initial =
    direction === 'left'
      ? { opacity: 0, x: offset }
      : direction === 'right'
        ? { opacity: 0, x: offset }
        : { opacity: 0, y: offset }

  if (prefersReducedMotion) {
    return children
  }

  return (
    <motion.div
      initial={initial}
      style={{ width: '100%' }}
      transition={{ delay, duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      viewport={viewport}
      whileInView={{ opacity: 1, x: 0, y: 0 }}
    >
      {children}
    </motion.div>
  )
}
