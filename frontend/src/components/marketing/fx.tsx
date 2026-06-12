'use client'

/**
 * Tiny dependency-free FX primitives for the landing page:
 * Reveal (scroll-in), TiltCard (3D hover), CountUp (animated numbers),
 * Spotlight (cursor-following glow). All respect prefers-reduced-motion.
 */
import { useEffect, useRef, useState } from 'react'
import { cn } from '@/lib/utils'

export function Reveal({
  children,
  className,
  delay = 0,
}: {
  children: React.ReactNode
  className?: string
  delay?: number
}) {
  const ref = useRef<HTMLDivElement>(null)
  useEffect(() => {
    const el = ref.current
    if (!el) return
    const io = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          el.classList.add('fx-in')
          io.disconnect()
        }
      },
      { threshold: 0.15 },
    )
    io.observe(el)
    return () => io.disconnect()
  }, [])
  return (
    <div ref={ref} className={cn('fx-reveal', className)} style={{ transitionDelay: `${delay}ms` }}>
      {children}
    </div>
  )
}

export function TiltCard({ children, className }: { children: React.ReactNode; className?: string }) {
  const ref = useRef<HTMLDivElement>(null)

  function onMove(e: React.MouseEvent) {
    const el = ref.current
    if (!el) return
    const r = el.getBoundingClientRect()
    const px = (e.clientX - r.left) / r.width - 0.5
    const py = (e.clientY - r.top) / r.height - 0.5
    el.style.transform = `perspective(900px) rotateY(${px * 10}deg) rotateX(${py * -10}deg) translateZ(0)`
    el.style.setProperty('--glow-x', `${(px + 0.5) * 100}%`)
    el.style.setProperty('--glow-y', `${(py + 0.5) * 100}%`)
  }
  function onLeave() {
    const el = ref.current
    if (el) el.style.transform = 'perspective(900px) rotateY(0deg) rotateX(0deg)'
  }

  return (
    <div
      ref={ref}
      onMouseMove={onMove}
      onMouseLeave={onLeave}
      className={cn('transition-transform duration-200 will-change-transform', className)}
      style={{
        backgroundImage:
          'radial-gradient(420px circle at var(--glow-x, 50%) var(--glow-y, 50%), hsl(var(--primary) / 0.10), transparent 65%)',
      }}
    >
      {children}
    </div>
  )
}

export function CountUp({ value, duration = 1400 }: { value: number; duration?: number }) {
  const ref = useRef<HTMLSpanElement>(null)
  const [display, setDisplay] = useState(0)

  useEffect(() => {
    const el = ref.current
    if (!el) return
    let raf = 0
    const io = new IntersectionObserver(
      ([entry]) => {
        if (!entry.isIntersecting) return
        io.disconnect()
        const start = performance.now()
        const tick = (now: number) => {
          const p = Math.min((now - start) / duration, 1)
          const eased = 1 - Math.pow(1 - p, 4)
          setDisplay(Math.round(eased * value))
          if (p < 1) raf = requestAnimationFrame(tick)
        }
        raf = requestAnimationFrame(tick)
      },
      { threshold: 0.4 },
    )
    io.observe(el)
    return () => {
      io.disconnect()
      cancelAnimationFrame(raf)
    }
  }, [value, duration])

  return <span ref={ref}>{display.toLocaleString()}</span>
}

export function Spotlight({ className }: { className?: string }) {
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const el = ref.current
    const parent = el?.parentElement
    if (!el || !parent) return
    const onMove = (e: MouseEvent) => {
      const r = parent.getBoundingClientRect()
      el.style.background = `radial-gradient(620px circle at ${e.clientX - r.left}px ${e.clientY - r.top}px, hsl(var(--primary) / 0.14), transparent 70%)`
    }
    parent.addEventListener('mousemove', onMove)
    return () => parent.removeEventListener('mousemove', onMove)
  }, [])

  return <div ref={ref} aria-hidden="true" className={cn('pointer-events-none absolute inset-0 -z-10', className)} />
}
