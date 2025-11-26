import * as React from "react"
import { useDropzone } from "react-dropzone"

interface DropUploadProps {
  onFiles: (_files: File[]) => void
}

export function DropUpload({ onFiles }: DropUploadProps): JSX.Element {
  const onDrop = React.useCallback(
    (accepted: File[]): void => {
      if (accepted.length > 0) {
        onFiles(accepted)
      }
    },
    [onFiles]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop })

  return (
    <div
      {...getRootProps()}
      className="border-2 border-dashed rounded-xl p-6 text-center cursor-pointer hover:border-primary/50 transition-colors"
    >
      <input {...getInputProps()} />
      {isDragActive ? (
        <p className="text-primary font-medium">Ablegen…</p>
      ) : (
        <>
          <p className="font-medium">
            Dateien hierher ziehen oder klicken, um auszuwählen
          </p>
          <p className="text-xs opacity-70 mt-1">PDF, PNG, JPG, DOCX …</p>
        </>
      )}
    </div>
  )
}
