'use client'

import { useState } from 'react'
import { FileSpreadsheet, FileText, FileType } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { toast } from '@/hooks/use-toast'
import type { ExportFormat } from '@/types'

interface ExportButtonsProps {
  /** Returns the file as a Blob for the given format. */
  onExport: (format: ExportFormat) => Promise<Blob>
  /** Base file name without extension, e.g. "inventory". */
  filename: string
}

const EXT: Record<ExportFormat, string> = { excel: 'xlsx', word: 'docx', pdf: 'pdf' }

export function ExportButtons({ onExport, filename }: ExportButtonsProps) {
  const [busy, setBusy] = useState<ExportFormat | null>(null)

  async function handle(format: ExportFormat) {
    setBusy(format)
    try {
      const blob = await onExport(format)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${filename}.${EXT[format]}`
      a.click()
      URL.revokeObjectURL(url)
    } catch {
      toast({ title: 'Export failed', description: 'Could not generate the file.', variant: 'destructive' })
    } finally {
      setBusy(null)
    }
  }

  return (
    <div className="flex gap-2">
      <Button variant="outline" size="sm" disabled={busy !== null} onClick={() => handle('excel')}>
        <FileSpreadsheet className="h-4 w-4 mr-1.5" />
        {busy === 'excel' ? 'Excel…' : 'Excel'}
      </Button>
      <Button variant="outline" size="sm" disabled={busy !== null} onClick={() => handle('word')}>
        <FileText className="h-4 w-4 mr-1.5" />
        {busy === 'word' ? 'Word…' : 'Word'}
      </Button>
      <Button variant="outline" size="sm" disabled={busy !== null} onClick={() => handle('pdf')}>
        <FileType className="h-4 w-4 mr-1.5" />
        {busy === 'pdf' ? 'PDF…' : 'PDF'}
      </Button>
    </div>
  )
}
