'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Bell, CheckCheck } from 'lucide-react'
import { PageHeader } from '@/components/shared/PageHeader'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { notificationService } from '@/lib/services'
import { formatDateTime } from '@/lib/utils'
import { cn } from '@/lib/utils'
import { toast } from '@/hooks/use-toast'

export default function NotificationsPage() {
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['notifications'],
    queryFn: () => notificationService.list(),
  })

  const markAllRead = useMutation({
    mutationFn: notificationService.markAllRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
      toast({ title: 'All notifications marked as read' })
    },
  })

  const markRead = useMutation({
    mutationFn: (id: string) => notificationService.markRead(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['notifications'] }),
  })

  const unreadCount = data?.results?.filter((n) => !n.is_read).length ?? 0

  return (
    <div className="space-y-4">
      <PageHeader
        title="Notifications"
        description={unreadCount > 0 ? `${unreadCount} unread` : 'All caught up'}
        action={
          unreadCount > 0 && (
            <Button variant="outline" size="sm" onClick={() => markAllRead.mutate()}>
              <CheckCheck className="h-4 w-4 mr-1.5" />
              Mark all read
            </Button>
          )
        }
      />

      {isLoading ? (
        <div className="space-y-2">
          {[...Array(5)].map((_, i) => <div key={i} className="h-16 bg-muted rounded-lg animate-pulse" />)}
        </div>
      ) : (
        <Card>
          <CardContent className="p-0 divide-y">
            {data?.results?.length === 0 && (
              <div className="flex flex-col items-center py-12 text-muted-foreground gap-2">
                <Bell className="h-8 w-8 opacity-30" />
                <p>No notifications yet.</p>
              </div>
            )}
            {data?.results?.map((notif) => (
              <div
                key={notif.id}
                className={cn(
                  'flex items-start gap-3 px-4 py-3 cursor-pointer hover:bg-muted/30 transition-colors',
                  !notif.is_read && 'bg-primary/5'
                )}
                onClick={() => !notif.is_read && markRead.mutate(notif.id)}
              >
                <div className={cn('mt-1 h-2 w-2 rounded-full shrink-0', notif.is_read ? 'bg-transparent' : 'bg-primary')} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-sm font-medium truncate">{notif.title}</p>
                    <span className="text-xs text-muted-foreground shrink-0">{formatDateTime(notif.created_at)}</span>
                  </div>
                  <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">{notif.message}</p>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
