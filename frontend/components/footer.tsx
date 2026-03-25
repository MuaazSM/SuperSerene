import React from "react"
import Link from "next/link"

function Footer() {
  return (
    <footer className="mt-20 border-t border-white/10 bg-neutral-950 px-6 py-12 text-white">
      <div className="mx-auto flex max-w-6xl flex-col gap-12">
        <div className="grid grid-cols-1 gap-8 md:grid-cols-4">
          <div className="md:col-span-2">
            <h3 className="text-2xl font-semibold tracking-tight">SuperSerene</h3>
            <p className="mt-3 max-w-md text-sm text-gray-400">
              Guided emotional fitness to stay steady, connected, and resilient in the moments that count.
            </p>
            <div className="mt-4 inline-flex items-center gap-3 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs text-gray-200">
              <span className="h-2 w-2 rounded-full bg-emerald-400" aria-hidden="true" />
              Always-on support, 24/7
            </div>
          </div>

          <div>
            <h4 className="text-sm font-semibold uppercase tracking-wide text-gray-300">Product</h4>
            <ul className="mt-3 space-y-2 text-sm text-gray-400">
              <li><Link href="#" className="hover:text-white">Dashboard</Link></li>
              <li><Link href="#" className="hover:text-white">Exercises</Link></li>
              <li><Link href="#" className="hover:text-white">Guided sessions</Link></li>
              <li><Link href="#" className="hover:text-white">Community</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="text-sm font-semibold uppercase tracking-wide text-gray-300">Company</h4>
            <ul className="mt-3 space-y-2 text-sm text-gray-400">
              <li><Link href="#" className="hover:text-white">About</Link></li>
              <li><Link href="#" className="hover:text-white">Careers</Link></li>
              <li><Link href="#" className="hover:text-white">Press</Link></li>
              <li><Link href="mailto:hello@SuperSerene" className="hover:text-white">Contact</Link></li>
            </ul>
          </div>
        </div>

        <div className="flex flex-col gap-4 border-t border-white/10 pt-6 text-xs text-gray-500 sm:flex-row sm:items-center sm:justify-between">
          <div>&copy; {new Date().getFullYear()} SuperSerene. All rights reserved.</div>
          <div className="flex flex-wrap items-center gap-4 text-gray-400">
            <Link href="#" className="hover:text-white">Privacy</Link>
            <span className="h-1 w-1 rounded-full bg-gray-600" aria-hidden="true" />
            <Link href="#" className="hover:text-white">Terms</Link>
            <span className="h-1 w-1 rounded-full bg-gray-600" aria-hidden="true" />
            <Link href="#" className="hover:text-white">Security</Link>
          </div>
        </div>
      </div>
    </footer>
  )
}

export default Footer