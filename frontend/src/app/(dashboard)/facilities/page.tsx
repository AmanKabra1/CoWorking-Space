'use client'

import { useQuery } from '@tanstack/react-query'
import { MapPin, Users, DollarSign } from 'lucide-react'
import { PageHeader } from '@/components/shared/PageHeader'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { facilityService } from '@/lib/services'
import { formatCurrency } from '@/lib/utils'

export default function FacilitiesPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['facilities'],
    queryFn: () => facilityService.list(),
  })

  return (
    <div className="space-y-4">
      <PageHeader title="Facilities" description="All spaces available for booking" />

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-48 bg-muted rounded-lg animate-pulse" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {data?.results?.map((facility) => (
            <Card key={facility.id} className="overflow-hidden">
              {facility.primary_image && (
                <img
                  src={facility.primary_image}
                  alt={facility.name}
                  className="w-full h-36 object-cover"
                />
              )}
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between gap-2">
                  <CardTitle className="text-base">{facility.name}</CardTitle>
                  <Badge variant={facility.is_available ? 'success' : 'secondary'}>
                    {facility.is_available ? 'Available' : 'Unavailable'}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="pt-0 space-y-1.5 text-sm text-muted-foreground">
                <div className="flex items-center gap-1.5">
                  <MapPin className="h-3.5 w-3.5" />
                  {facility.building_name}, Floor {facility.floor_number}
                </div>
                <div className="flex items-center gap-1.5">
                  <Users className="h-3.5 w-3.5" />
                  Capacity: {facility.capacity}
                </div>
                <div className="flex items-center gap-1.5">
                  <DollarSign className="h-3.5 w-3.5" />
                  {formatCurrency(facility.price_per_hour)}/hr
                </div>
              </CardContent>
            </Card>
          ))}
          {data?.results?.length === 0 && (
            <p className="col-span-full text-center py-12 text-muted-foreground">No facilities found.</p>
          )}
        </div>
      )}
    </div>
  )
}
