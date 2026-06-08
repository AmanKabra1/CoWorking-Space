'use client'

import { useQuery } from '@tanstack/react-query'
import { CalendarDays, MessageSquare, Pin } from 'lucide-react'
import { PageHeader } from '@/components/shared/PageHeader'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { communityService } from '@/lib/services'
import { formatDate, formatDateTime } from '@/lib/utils'
import { cn } from '@/lib/utils'

export default function CommunityPage() {
  const { data: posts, isLoading: postsLoading } = useQuery({
    queryKey: ['community-posts'],
    queryFn: () => communityService.listPosts(),
  })

  const { data: events } = useQuery({
    queryKey: ['community-events'],
    queryFn: () => communityService.listEvents(),
  })

  return (
    <div className="space-y-6">
      <PageHeader title="Community" description="Company announcements, posts, and events" />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Posts feed */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">Posts</h2>

          {postsLoading ? (
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => <div key={i} className="h-28 bg-muted rounded-lg animate-pulse" />)}
            </div>
          ) : (
            posts?.results?.map((post) => (
              <Card
                key={post.id}
                className={cn('', post.is_pinned && 'border-primary/40 bg-primary/5')}
              >
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-2">
                      {post.is_pinned && <Pin className="h-3.5 w-3.5 text-primary shrink-0" />}
                      <CardTitle className="text-base">{post.title}</CardTitle>
                    </div>
                    <Badge variant={post.post_type === 'announcement' ? 'default' : 'secondary'}>
                      {post.post_type}
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {post.author_name} · {formatDate(post.created_at)}
                  </p>
                </CardHeader>
                <CardContent className="pt-0">
                  <p className="text-sm text-foreground/80 line-clamp-3">{post.content}</p>
                  <div className="flex items-center gap-1 mt-2 text-xs text-muted-foreground">
                    <MessageSquare className="h-3.5 w-3.5" />
                    {post.comment_count} comment{post.comment_count !== 1 ? 's' : ''}
                  </div>
                </CardContent>
              </Card>
            ))
          )}
          {posts?.results?.length === 0 && (
            <p className="text-sm text-muted-foreground text-center py-8">No posts yet.</p>
          )}
        </div>

        {/* Upcoming events */}
        <div className="space-y-4">
          <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">Upcoming Events</h2>
          <div className="space-y-3">
            {events?.results?.map((event) => (
              <Card key={event.id}>
                <CardContent className="p-4 space-y-1">
                  <div className="flex items-start gap-2">
                    <CalendarDays className="h-4 w-4 text-primary shrink-0 mt-0.5" />
                    <div className="min-w-0">
                      <p className="text-sm font-medium truncate">{event.title}</p>
                      <p className="text-xs text-muted-foreground">
                        {formatDateTime(event.start_datetime)}
                      </p>
                      <p className="text-xs text-muted-foreground">{event.location}</p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {event.rsvp_count} attending
                        {event.max_attendees ? ` / ${event.max_attendees} max` : ''}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
            {events?.results?.length === 0 && (
              <p className="text-sm text-muted-foreground">No upcoming events.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
