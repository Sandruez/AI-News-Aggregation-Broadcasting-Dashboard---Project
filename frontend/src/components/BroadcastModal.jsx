import { useState } from 'react'
import { X, Mail, Linkedin, MessageCircle, BookOpen, Newspaper, CheckCircle, Loader2, Copy, Check } from 'lucide-react'
import { broadcast } from '../utils/api'
import clsx from 'clsx'

const PLATFORMS = [
  { id: 'email', label: 'Email', icon: Mail, color: 'text-blue-400', desc: 'Send to an inbox' },
  { id: 'linkedin', label: 'LinkedIn', icon: Linkedin, color: 'text-sky-400', desc: 'AI-written post' },
  { id: 'whatsapp', label: 'WhatsApp', icon: MessageCircle, color: 'text-acid-400', desc: 'Share to group' },
  { id: 'blog', label: 'Blog', icon: BookOpen, color: 'text-ember-400', desc: 'Blog post snippet' },
  { id: 'newsletter', label: 'Newsletter', icon: Newspaper, color: 'text-pulse-400', desc: 'Newsletter blurb' },
]

export default function BroadcastModal({ favoriteId, newsItem, onClose }) {
  const [selected, setSelected] = useState(null)
  const [recipient, setRecipient] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [copied, setCopied] = useState(false)

  const handleBroadcast = async () => {
    if (!selected) return
    setLoading(true)
    setResult(null)
    try {
      const data = await broadcast({
        favorite_id: favoriteId,
        platform: selected,
        recipient: selected === 'email' ? recipient : undefined,
      })
      setResult(data)
    } catch (e) {
      setResult({ status: 'error', message: e.response?.data?.detail || 'Something went wrong', platform: selected })
    } finally {
      setLoading(false)
    }
  }

  const copyContent = () => {
    if (result?.generated_content) {
      navigator.clipboard.writeText(result.generated_content)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fade-in">
      <div className="bg-ink-800 border border-ink-600 rounded-2xl w-full max-w-lg shadow-2xl shadow-black/50 animate-slide-up">
        {/* Header */}
        <div className="flex items-center justify-between p-5 border-b border-ink-700">
          <div>
            <h2 className="font-display font-700 text-white text-base">Broadcast Story</h2>
            <p className="text-xs text-ink-400 mt-0.5 line-clamp-1">{newsItem?.title}</p>
          </div>
          <button onClick={onClose} className="text-ink-500 hover:text-white transition-colors p-1 rounded-lg hover:bg-ink-700">
            <X size={18} />
          </button>
        </div>

        <div className="p-5 space-y-4">
          {/* Platform grid */}
          {!result && (
            <>
              <p className="text-xs text-ink-400 font-body">Choose where to send this story:</p>
              <div className="grid grid-cols-5 gap-2">
                {PLATFORMS.map(({ id, label, icon: Icon, color, desc }) => (
                  <button
                    key={id}
                    onClick={() => setSelected(id)}
                    className={clsx(
                      'flex flex-col items-center gap-1.5 p-3 rounded-xl border text-center transition-all duration-150',
                      selected === id
                        ? 'border-pulse-500 bg-pulse-500/15'
                        : 'border-ink-600 bg-ink-900 hover:border-ink-500'
                    )}
                  >
                    <Icon size={18} className={selected === id ? 'text-pulse-400' : color} />
                    <span className="text-xs font-body font-500 text-white">{label}</span>
                  </button>
                ))}
              </div>

              {/* Email recipient field */}
              {selected === 'email' && (
                <div className="animate-fade-in">
                  <label className="text-xs text-ink-400 block mb-1">Recipient email</label>
                  <input
                    type="email"
                    value={recipient}
                    onChange={e => setRecipient(e.target.value)}
                    placeholder="you@example.com"
                    className="w-full bg-ink-900 border border-ink-600 rounded-lg px-3 py-2 text-sm text-white 
                               placeholder:text-ink-500 focus:outline-none focus:border-pulse-500 transition-colors font-mono"
                  />
                </div>
              )}

              <button
                onClick={handleBroadcast}
                disabled={!selected || loading || (selected === 'email' && !recipient)}
                className="btn-primary w-full flex items-center justify-center gap-2"
              >
                {loading ? <><Loader2 size={15} className="animate-spin" /> Generating…</> : 'Broadcast →'}
              </button>
            </>
          )}

          {/* Result */}
          {result && (
            <div className="animate-slide-up space-y-3">
              <div className="flex items-start gap-3 p-3 rounded-xl bg-ink-900 border border-ink-700">
                <CheckCircle size={18} className="text-acid-400 mt-0.5 shrink-0" />
                <div>
                  <p className="text-sm font-body font-500 text-white capitalize">{result.platform}</p>
                  <p className="text-xs text-ink-400 mt-0.5">{result.message}</p>
                </div>
              </div>

              {result.generated_content && (
                <div className="relative">
                  <div className="bg-ink-950 border border-ink-700 rounded-xl p-4 text-xs text-ink-300 leading-relaxed whitespace-pre-wrap max-h-48 overflow-y-auto font-body">
                    {result.generated_content}
                  </div>
                  <button
                    onClick={copyContent}
                    className="absolute top-2 right-2 p-1.5 rounded-lg bg-ink-700 hover:bg-ink-600 text-ink-400 hover:text-white transition-all"
                    title="Copy to clipboard"
                  >
                    {copied ? <Check size={12} className="text-acid-400" /> : <Copy size={12} />}
                  </button>
                </div>
              )}

              <div className="flex gap-2">
                <button onClick={() => { setResult(null); setSelected(null) }} className="btn-ghost flex-1">
                  Send Another
                </button>
                <button onClick={onClose} className="btn-primary flex-1">Done</button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
