'use client'

import { useState, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { PageHeader } from '@/components/shared/PageHeader'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { documentService } from '@/lib/services'
import { formatDate } from '@/lib/utils'
import type { Document } from '@/types'
import { FileText, Image, File, Download, Trash2 } from 'lucide-react'

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function FileIcon({ fileType }: { fileType: string }) {
  const lower = fileType.toLowerCase()
  if (lower.includes('pdf')) return <FileText className="h-5 w-5 text-red-500" />
  if (lower.includes('image') || lower.includes('png') || lower.includes('jpg') || lower.includes('jpeg') || lower.includes('gif') || lower.includes('webp')) {
    return <Image className="h-5 w-5 text-blue-500" />
  }
  return <File className="h-5 w-5 text-muted-foreground" />
}

export default function DocumentsPage() {
  const queryClient = useQueryClient()
  const [showUpload, setShowUpload] = useState(false)
  const [title, setTitle] = useState('')
  const fileRef = useRef<HTMLInputElement>(null)

  const { data: documents, isLoading, isError } = useQuery<Document[]>({
    queryKey: ['documents'],
    queryFn: () => documentService.list(),
  })

  const uploadMutation = useMutation({
    mutationFn: (formData: FormData) => documentService.upload(formData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] })
      setShowUpload(false)
      setTitle('')
      if (fileRef.current) fileRef.current.value = ''
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => documentService.delete(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['documents'] }),
  })

  function handleUpload(e: React.FormEvent) {
    e.preventDefault()
    const file = fileRef.current?.files?.[0]
    if (!file) return
    const fd = new FormData()
    fd.append('title', title)
    fd.append('file', file)
    uploadMutation.mutate(fd)
  }

  return (
    <div className="space-y-4">
      <PageHeader
        title="Documents"
        description="Manage and share company documents"
        action={
          <Button onClick={() => setShowUpload(v => !v)}>
            {showUpload ? 'Cancel' : 'Upload Document'}
          </Button>
        }
      />

      {showUpload && (
        <Card>
          <CardContent className="p-6">
            <h2 className="text-base font-semibold mb-4">Upload New Document</h2>
            <form onSubmit={handleUpload} className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1">
                <Label htmlFor="doc_title">Title</Label>
                <Input
                  id="doc_title"
                  value={title}
                  onChange={e => setTitle(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-1">
                <Label htmlFor="doc_file">File</Label>
                <Input
                  id="doc_file"
                  type="file"
                  ref={fileRef}
                  required
                />
              </div>
              <div className="sm:col-span-2 flex justify-end gap-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setShowUpload(false)
                    setTitle('')
                    if (fileRef.current) fileRef.current.value = ''
                  }}
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={uploadMutation.isPending}>
                  {uploadMutation.isPending ? 'Uploading…' : 'Upload'}
                </Button>
              </div>
              {uploadMutation.isError && (
                <p className="sm:col-span-2 text-sm text-destructive">Upload failed. Please try again.</p>
              )}
            </form>
          </CardContent>
        </Card>
      )}

      {isLoading ? (
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-16 bg-muted rounded-lg animate-pulse" />
          ))}
        </div>
      ) : isError ? (
        <Card>
          <CardContent className="p-8 text-center text-muted-foreground">
            Failed to load documents.
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="text-left px-4 py-3 font-medium">File</th>
                    <th className="text-left px-4 py-3 font-medium">Title</th>
                    <th className="text-left px-4 py-3 font-medium">Size</th>
                    <th className="text-left px-4 py-3 font-medium">Version</th>
                    <th className="text-left px-4 py-3 font-medium">Uploaded By</th>
                    <th className="text-left px-4 py-3 font-medium">Date</th>
                    <th className="text-left px-4 py-3 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {documents?.length === 0 && (
                    <tr>
                      <td colSpan={7} className="text-center py-8 text-muted-foreground">
                        No documents found.
                      </td>
                    </tr>
                  )}
                  {documents?.map((doc) => (
                    <tr key={doc.id} className="border-b last:border-0 hover:bg-muted/30 transition-colors">
                      <td className="px-4 py-3">
                        <FileIcon fileType={doc.file_type} />
                      </td>
                      <td className="px-4 py-3 font-medium">{doc.title}</td>
                      <td className="px-4 py-3 text-muted-foreground">{formatFileSize(doc.file_size)}</td>
                      <td className="px-4 py-3 text-muted-foreground">v{doc.version}</td>
                      <td className="px-4 py-3 text-muted-foreground">
                        {doc.uploaded_by.first_name} {doc.uploaded_by.last_name}
                      </td>
                      <td className="px-4 py-3 text-muted-foreground">{formatDate(doc.created_at)}</td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <a href={doc.file} target="_blank" rel="noopener noreferrer" download>
                            <Button size="sm" variant="ghost" title="Download">
                              <Download className="h-4 w-4" />
                            </Button>
                          </a>
                          <Button
                            size="sm"
                            variant="ghost"
                            title="Delete"
                            onClick={() => deleteMutation.mutate(doc.id)}
                            disabled={deleteMutation.isPending}
                          >
                            <Trash2 className="h-4 w-4 text-destructive" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
