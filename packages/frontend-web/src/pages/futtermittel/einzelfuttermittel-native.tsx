import { useParams } from '@/app/routing/typed-router'
import { FeedingFeedDetail } from '@/features/feed-advice/FeedingFeedDetail'

export default function EinzelfuttermittelNativePage(): JSX.Element {
  const { id } = useParams<{ id?: string }>()
  return <FeedingFeedDetail feedId={id} />
}
