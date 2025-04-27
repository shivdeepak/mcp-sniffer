import TabbedInterface from './TabbedInterface'
import Connection from './connection'

export default function ConnectionDetails({
  connection,
  onClose,
}: {
  connection: Connection
  onClose: () => void
}) {
  return (
    <div>
      <TabbedInterface connection={connection} onClose={onClose} />
    </div>
  )
}
