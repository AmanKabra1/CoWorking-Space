'use client'

import { useQuery } from '@tanstack/react-query'
import { PageHeader } from '@/components/shared/PageHeader'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { incubationService } from '@/lib/services'
import type { IncubationProfile } from '@/types'
import { Users, Globe } from 'lucide-react'

const STAGE_CLASSES: Record<IncubationProfile['stage'], string> = {
  ideation: 'bg-purple-100 text-purple-700 border-purple-200',
  mvp: 'bg-blue-100 text-blue-700 border-blue-200',
  growth: 'bg-green-100 text-green-700 border-green-200',
  scaling: 'bg-orange-100 text-orange-700 border-orange-200',
}

const STATUS_CLASSES: Record<IncubationProfile['status'], string> = {
  active: 'bg-green-100 text-green-700 border-green-200',
  graduated: 'bg-blue-100 text-blue-700 border-blue-200',
  inactive: 'bg-gray-100 text-gray-500 border-gray-200',
}

export default function IncubationPage() {
  const { data: profiles, isLoading, isError } = useQuery<IncubationProfile[]>({
    queryKey: ['incubation'],
    queryFn: () => incubationService.list(),
  })

  const total = profiles?.length ?? 0
  const active = profiles?.filter(p => p.status === 'active').length ?? 0
  const graduated = profiles?.filter(p => p.status === 'graduated').length ?? 0

  return (
    <div className="space-y-6">
      <PageHeader
        title="Incubation"
        description="Startups and incubation program members"
      />

      {/* Stats bar */}
      <div className="grid grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold">{total}</p>
            <p className="text-sm text-muted-foreground mt-1">Total Startups</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold text-green-600">{active}</p>
            <p className="text-sm text-muted-foreground mt-1">Active</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold text-blue-600">{graduated}</p>
            <p className="text-sm text-muted-foreground mt-1">Graduated</p>
          </CardContent>
        </Card>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-44 bg-muted rounded-lg animate-pulse" />
          ))}
        </div>
      ) : isError ? (
        <Card>
          <CardContent className="p-8 text-center text-muted-foreground">
            Failed to load incubation profiles.
          </CardContent>
        </Card>
      ) : profiles?.length === 0 ? (
        <Card>
          <CardContent className="p-8 text-center text-muted-foreground">
            No incubation profiles found.
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {profiles?.map((profile) => (
            <Card key={profile.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-5 space-y-3">
                {/* Header */}
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <h3 className="font-semibold text-base leading-tight">{profile.company.name}</h3>
                    <p className="text-xs text-muted-foreground mt-0.5">{profile.sector}</p>
                  </div>
                  <span
                    className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium whitespace-nowrap ${STATUS_CLASSES[profile.status]}`}
                  >
                    {profile.status}
                  </span>
                </div>

                {/* Stage badge */}
                <span
                  className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium ${STAGE_CLASSES[profile.stage]}`}
                >
                  {profile.stage}
                </span>

                {/* Description */}
                {profile.description && (
                  <p className="text-sm text-muted-foreground line-clamp-2">{profile.description}</p>
                )}

                {/* Meta */}
                <div className="flex items-center gap-4 text-xs text-muted-foreground pt-1">
                  <span className="flex items-center gap-1">
                    <Users className="h-3.5 w-3.5" />
                    {profile.team_size} members
                  </span>
                  {profile.website && (
                    <a
                      href={profile.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 hover:text-foreground transition-colors"
                    >
                      <Globe className="h-3.5 w-3.5" />
                      Website
                    </a>
                  )}
                </div>

                {/* Mentor */}
                {profile.mentor && (
                  <p className="text-xs text-muted-foreground border-t pt-2">
                    Mentor: {profile.mentor.first_name} {profile.mentor.last_name}
                  </p>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
