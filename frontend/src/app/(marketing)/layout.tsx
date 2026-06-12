import Link from 'next/link'
import { Building2 } from 'lucide-react'

export default function MarketingLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col bg-background">
      <header className="sticky top-0 z-50 border-b border-border/60 bg-background/70 backdrop-blur-xl supports-[backdrop-filter]:bg-background/60">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5 font-bold text-xl text-foreground">
            <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-violet-600 shadow-lg shadow-primary/30">
              <Building2 className="h-5 w-5 text-white" />
            </span>
            CoWork<span className="text-primary">Hub</span>
          </Link>
          <nav className="flex items-center gap-2 sm:gap-6">
            <Link href="/book" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
              Book a Space
            </Link>
            <Link
              href="/login"
              className="inline-flex items-center justify-center rounded-lg text-sm font-semibold h-9 px-4 py-2 bg-primary text-primary-foreground hover:bg-primary/90 transition-colors shadow-md shadow-primary/20"
            >
              Sign In
            </Link>
          </nav>
        </div>
      </header>

      <main className="flex-1">{children}</main>

      <footer className="border-t bg-muted/30">
        <div className="max-w-6xl mx-auto px-4 py-10">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-2 font-bold text-foreground">
              <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-gradient-to-br from-primary to-violet-600">
                <Building2 className="h-4 w-4 text-white" />
              </span>
              CoWorkHub
            </div>
            <div className="flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-sm text-muted-foreground">
              <Link href="/book" className="hover:text-foreground transition-colors">Book a Space</Link>
              <Link href="/login" className="hover:text-foreground transition-colors">Sign In</Link>
            </div>
            <p className="text-sm text-muted-foreground">
              &copy; {new Date().getFullYear()} CoWorkHub. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
