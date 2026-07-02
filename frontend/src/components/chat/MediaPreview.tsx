import type { MediaAttachment } from "../../types";

interface MediaPreviewProps {
  media: MediaAttachment;
}

export function MediaPreview({ media }: MediaPreviewProps) {
  const isPdf = media.mime_type.includes("pdf") || media.filename?.toLowerCase().endsWith(".pdf");

  if (isPdf) {
    return (
      <a
        href={media.url}
        target="_blank"
        rel="noopener noreferrer"
        className="mt-2 flex items-center gap-2.5 rounded-lg border border-border bg-canvas px-3 py-2.5 transition-colors hover:bg-white"
      >
        <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-danger/10 text-xs font-bold text-danger">
          PDF
        </span>
        <span className="min-w-0">
          <span className="block truncate text-sm font-medium text-ink">{media.filename ?? "Document"}</span>
          <span className="block text-xs text-ink-muted">Tap to open</span>
        </span>
      </a>
    );
  }

  return (
    <img
      src={media.url}
      alt="Shared media"
      className="mt-2 max-h-64 w-full rounded-lg border border-border object-cover"
      loading="lazy"
    />
  );
}
